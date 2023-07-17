from functools import wraps
from flask import request
from background.logsconf import logger
import psycopg2
import jwt
from background.config import BaseConfig
from background.connections import conn_to_db

class CurrectUser:
    def __init__(self, id, username):
        self.id = id
        self.username = username


def UserObjectToJson(user_object: list) -> CurrectUser:
    return CurrectUser(user_object[0], user_object[1])




def token_required_with_role(role):
    def token_user_role_required(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            token = None
            if "authorization" in request.headers:
                token = request.headers["authorization"]
            if not token:
                return {"success": False, "msg": "Brak waznego Tokenu"}, 401

            try:
                data = jwt.decode(token, BaseConfig.SECRET_KEY,
                                  algorithms=["HS256"])

            except jwt.ExpiredSignatureError:
                return {"success": False, "msg": "Sesja wygasla, zaloguj się ponownie."}, 401
            except jwt.DecodeError:
                return {"success": False, "msg": "Nieprawidlowy token."}, 400
            except UnicodeEncodeError:
                return {"success": False, "msg": "Token zawiera nieobslugiwane znaki."}, 400

            try:
                conn = conn_to_db()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute(
                    "select jwt_token from jwt_token_block_list where jwt_token = %s", (token,))
                token_expired = cur.fetchone()

                if token_expired is not None:
                    return {"success": False, "msg": "Ta sesja już wygasła"}, 401

                cur.execute(
                    "Select user_roles.role_id from user_roles INNER JOIN roles on user_roles.role_id = roles.id where user_roles.user_id=%s and roles.role=%s", (data["id"], role))

                current_user = cur.fetchone()
                if not current_user:
                    return {"success": False, "msg": "Nie masz uprawnień do przeglądania tej zawartości."}, 403

                return f(UserObjectToJson([data["id"], data["username"]]))

            except Exception as e:
                logger.error("Wystąpił Błąd %s" % e)
                logger.debug('ERROR!', exc_info=True)
                return {"success": False, "msg": f"Nieznany bład"}, 400

            finally:
                cur.close()
                conn.close()

        return decorator
    return token_user_role_required
