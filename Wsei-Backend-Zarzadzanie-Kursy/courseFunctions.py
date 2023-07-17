import psycopg2
import psycopg2.extras
from connection import conn_to_db
def delete_course(course_id): 
    try:
        conn = conn_to_db()
        # Create a cursor object to interact with the database
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Execute the DELETE statement
        
        cursor.execute(
            "Select * FROM courses WHERE id = %s", (course_id,))
        check_course = cursor.fetchone()
        if not check_course:
            return {"success": False,"msg": "This course doesn't exists."}
        
        cursor.execute("DELETE FROM courses WHERE id = %s", (course_id,))
        return {"success": True,"msg": "Deleted Succesfully"}

    except Exception as e:
        conn.rollback()
        return {"success": False, "msg": "Unexpected error"}

    finally:
        conn.commit()
        cursor.close()
        conn.close()

def add_course(course_name,course_description,course_id_user):
    try:
        conn = conn_to_db()
        # Create a cursor object to interact with the database
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Execute the DELETE statement
        
        cursor.execute(
            "Select * FROM courses WHERE name=%s and description=%s and id_user=%s", (course_name,course_description,course_id_user,))
        check_course = cursor.fetchone()
        if check_course:
            return {"success": False,"msg": "This already exists."}
        # Execute the INSERT statement
        cursor.execute(
            "INSERT INTO courses (name, description, id_user) VALUES (%s, %s, %s)",
            (course_name,course_description,course_id_user,)
        )

        # Commit the transaction
        

        return {"success": True,"msg": "Dodano kurs pomyśnie."}

    except Exception as e:
        conn.rollback()
        return {"success": False, "msg": "Unexpected error"}

    finally:
        conn.commit()
        cursor.close()
        conn.close()