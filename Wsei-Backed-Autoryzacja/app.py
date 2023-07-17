from flask import Flask, request
from flask_restx import Resource
from flask_cors import CORS
from appModels.formsNamespaces import rest_api, login_namespace
from appModels.loginFormsModels import login_model
from background.authenticaction import login, is_valid_token_exists_token, block_token
from background.logsconf import logger
from appModels.docModelsNamespaces import FailureModel, SuccessModel, SuccessDataModelUserToken
from appModels.models import Base
from background.config import BaseConfig
from passlib.hash import pbkdf2_sha256
from background.connections import conn_to_db
def create_app():

    app = Flask(__name__)
    app.secret_key = BaseConfig.SECRET_KEY
    rest_api.init_app(app)
    CORS(app)
    with app.app_context():
        Base.metadata.create_all(BaseConfig.engine)
        try:
            conn = conn_to_db()
            cursor = conn.cursor()

            # Sprawdź, czy istnieje użytkownik "admin"
            cursor.execute("SELECT * FROM users WHERE username='admin'")
            users_tester = cursor.fetchone()

            if not users_tester:
                hashed_pswd = pbkdf2_sha256.hash('12345')
                cursor.execute("INSERT INTO users (first_name, last_name, username, password, deleted) VALUES (%s, %s, %s, %s, %s);", ('Admin','Admin','admin', hashed_pswd, False))
                conn.commit()

            # Sprawdź, czy istnieje rola "Administrator"
            cursor.execute("SELECT * FROM roles WHERE role='Administrator';")
            roles_tester = cursor.fetchone()

            if not roles_tester:
                cursor.execute("INSERT INTO roles (role) VALUES (%s);", ('Wykladowca',))
                cursor.execute("INSERT INTO roles (role) VALUES (%s);", ('Student',))
                cursor.execute("INSERT INTO roles (role) VALUES (%s);", ('Administrator',))
                conn.commit()

                # Pobierz id nowo utworzonych ról
                cursor.execute("SELECT id FROM roles WHERE role='Wykladowca';")
                wykladowca_id = cursor.fetchone()[0]
                cursor.execute("SELECT id FROM roles WHERE role='Student';")
                student_id = cursor.fetchone()[0]
                cursor.execute("SELECT id FROM roles WHERE role='Administrator';")
                administrator_id = cursor.fetchone()[0]

                # Pobierz id użytkownika 'admin'
                cursor.execute("SELECT id FROM users WHERE username='admin';")
                admin_id = cursor.fetchone()[0]

                # Przypisz użytkownika 'admin' do ról
                cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s);", (admin_id, student_id))
                cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s);", (admin_id, wykladowca_id))
                cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s);", (admin_id, administrator_id))
                
                
                

                conn.commit()


        finally:
            cursor.close()
            conn.close()

       
    return app


app = create_app()

# working on frontend
@login_namespace.route('/login')
class Login(Resource):
    """
    Endpoint obsługujący operacje związane z logowaniem.
    """
    @login_namespace.doc(
        responses={
            200: ('Successful operation', SuccessDataModelUserToken),
            400: ('Bad Request', FailureModel),
            422: ('Unprocessable entity', FailureModel),
            500: ('Server Error', FailureModel),
        }
    )
    @rest_api.expect(login_model, validate=True)
    def post(self):
        """
        Loguje użytkownika do systemu

        Zwraca wiadomość wraz z danymi o wyniku próby logowania.
        """
        req_data = request.get_json()
        _username = req_data.get("username").lower()
        _password = req_data.get("password")

        if not all([_username, _password]):
            return {"success": False, "msg": "Failed to validate required data"}, 422

        response = login(_username, _password)
        if response['success'] == True:
            logger.info(
                '[%s] -- logged in success', _username)
            return response, 200
        else:
            logger.info(
                '[%s] -- logged in failed', _username)
            return response, 500
        
# partialy working on frontend
@login_namespace.route('/logout')
class LogoutUser(Resource):
    """
    Klasa reprezentująca zasób wylogowania użytkownika.

    Metody:
    post: Wylogowuje użytkownika, dodając jego token JWT do listy zablokowanych tokenów.
    """
    @login_namespace.doc(
        responses={
            200: ('Successful operation', SuccessModel),
            400: ('Bad Request', FailureModel),
            401: ('Unauthorized', FailureModel),
            500: ('Server Error', FailureModel),
        }
    )
    def post(self):
        """
        Wylogowywuje użytkownika z systemu

        Zwraca wiadomość o wyniku próby wylogowania.
        """
        _jwt_token = request.headers.get("authorization")
        if _jwt_token and is_valid_token_exists_token(_jwt_token):
            response = block_token(_jwt_token)
            return response

        else:
            return {"success": False, "msg": "Valid JWT token is missing"}, 401


if __name__ == "__main__":
    app.run(port=5000)
