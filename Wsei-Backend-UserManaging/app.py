import psycopg2
from flask import Flask, request
from flask_cors import CORS
from flask_restx import Resource
from UserModel import user_model, api
from dbconn import conn_to_db
from passlib.hash import pbkdf2_sha256
import psycopg2.extras
from authenticaction import token_required_with_role

# Create Flask app
app = Flask(__name__)
api.init_app(app)
CORS(app)
@api.route('/api/add-user')

class UserResource(Resource):
    #@token_required_with_role('Wykladowca')
    @api.expect(user_model)
    def post(self):
        req_data = request.get_json()
        firstname=req_data.get("first_name")
        lastname=req_data.get("last_name")
        username=req_data.get("username")
        password=req_data.get("password")
        password_hash=pbkdf2_sha256.hash(password)
        userrole=req_data.get("role")

        try:
            # Create a cursor object to interact with the database
            conn=conn_to_db()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(
                "SELECT * from users where username = %s",(username,)
            )
            usercheck=cursor.fetchone()
            if usercheck:
                return {"success": False, "msg": "This username already exists."}
            # Execute the INSERT statement
            cursor.execute(
                "INSERT INTO users (first_name, last_name, username, password, deleted) VALUES (%s, %s, %s, %s, FALSE) RETURNING id",
                (firstname, lastname, username, password_hash,)
            )
            

            # Get the generated user ID
            user_id = cursor.fetchone()[0]
            cursor.execute(
                "SELECT id from roles WHERE role = %s",(userrole,)
            )
            role_id=cursor.fetchone()
            if not role_id:
                return {"success": False, "msg": "This role doesn't exist."}
            
            # Assign the selected role to the user
            role_id=role_id[0]
            cursor.execute(
                "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
                (user_id, role_id)
            )

            # Commit the transaction
            conn.commit()

            return {'success':True,'message': 'User added successfully'}, 201

        except (Exception, psycopg2.Error) as error:
            conn.rollback()
            return {"success": False, "msg": "Unexpected error"}

        finally:
            # Close the cursor
            cursor.close()
            conn.close()

@api.route('/api/delete-user')
class DeleteUser(Resource):
    # @token_required_with_role('Wykladowca')

    def post(self):
        try:
            # Create a cursor object to interact with the database
            conn=conn_to_db()
            cursor = conn.cursor()
            req_data = request.get_json()
            user_id=req_data.get("id_user")

            cursor.execute(
                "SELECT * from users WHERE id =%s and deleted=false",(user_id,)
            )
            userexistcheck=cursor.fetchone()
            if not userexistcheck:
                return {"success": False, "msg": "This username is terminated"}
            # Execute the DELETE statement
            cursor.execute("DELETE FROM user_roles WHERE user_id = %s", (user_id,))
            cursor.execute("UPDATE users set deleted=true WHERE id = %s", (user_id,))

            # Commit the transaction
            conn.commit()

            return {'success': True,'msg': 'User deleted successfully'}, 200

        except (Exception, psycopg2.Error) as error:
            conn.rollback()
            return {"success": False, "msg": "Unexpected error"},500
        

        finally:
            # Close the cursor
            cursor.close()
            conn.close()
            
@api.route('/api/list-users')
class UserList(Resource):
    @token_required_with_role('Administrator')

    def get(self):
        try:
            # Create a cursor object to interact with the database
            conn=conn_to_db()
            cursor = conn.cursor()

            # Execute the SELECT statement to retrieve all users with their roles
            cursor.execute("""
                SELECT u.id, u.first_name, u.last_name, u.username, u.deleted, r.role
                FROM users u
                JOIN user_roles ur ON u.id = ur.user_id
                JOIN roles r ON ur.role_id = r.id
            """)

            # Fetch all rows from the cursor
            rows = cursor.fetchall()

            # Transform rows into a list of dictionaries
            users = []
            for row in rows:
                user = {
                    'id': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'username': row[3],
                    'deleted': row[4],
                    'role': row[5]
                }
                users.append(user)

            return {"success": True,'users': users}, 200

        except (Exception, psycopg2.Error) as error:
            return {"success": False, "msg": "Unexpected error"},500

        finally:
            # Close the cursor
            cursor.close()
            conn.close()



if __name__ == '__main__':
    app.run(port=5003)