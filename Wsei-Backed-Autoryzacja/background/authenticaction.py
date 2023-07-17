from functools import wraps
from flask import request
from passlib.hash import pbkdf2_sha256
from background.logsconf import logger
from typing import Union, Tuple, Dict
import psycopg2
import jwt
import uuid
import datetime
from appModels.models import User
from background.config import BaseConfig
from background.connections import conn_to_db


def token_required(f):
    """
    Dekorator do sprawdzania prawidłowości tokenu autoryzacji w żądaniu HTTP.

    Ten dekorator sprawdza, czy żądanie HTTP zawiera nagłówek "authorization" z prawidłowym tokenem. Jeśli token jest prawidłowy, dekorator pozwala na wykonanie dekorowanej funkcji. W przeciwnym razie, zwraca odpowiedź HTTP z odpowiednim kodem błędu i komunikatem.

    Argumenty:
    f (Callable): Funkcja do dekorowania.

    Zwraca:
    Callable: Dekorowana funkcja, która zostanie wykonana, jeśli token autoryzacji jest prawidłowy. W przeciwnym razie, zwraca odpowiedź HTTP z kodem błędu i komunikatem.
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if "authorization" in request.headers:
            token = request.headers["authorization"]
        if not token:
            return {"success": False, "msg": "Brak ważnego Tokenu"}, 401

        try:
            conn = conn_to_db()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            data = jwt.decode(token, BaseConfig.SECRET_KEY,
                              algorithms=["HS256"])
            cur.execute(
                "Select id,username from users where username=%s and deleted=FALSE", (data["username"],))
            current_user = cur.fetchone()
            if current_user == []:
                return {"success": False, "msg": "Ten użytkownik nie istnieje"}, 401
            cur.execute(
                "select id from jwt_token_block_list where jwt_token = %s", (token,))
            token_expired = cur.fetchone()
            if token_expired is not None:
                return {"success": False, "msg": "Ta sesja już wygasła"}, 401
            return f(UserObjectToJson(current_user))

        except jwt.ExpiredSignatureError:
            return {"success": False, "msg": "Sesja wygasła, zaloguj się ponownie."}, 401

        except jwt.DecodeError:
            return {"success": False, "msg": "Nieprawidłowy token."}, 400

        except Exception as e:
            logger.info("Wystąpił Błąd %s" % e)
            logger.debug('ERROR!', exc_info=True)
            return {"success": False, "msg": f"Nieznany bład"}, 400

        finally:
            cur.close()
            conn.close()

    return decorator


def login(_username: str, _password: str) -> Tuple[Dict, int]:
    """
    Loguje użytkownika do systemu.

    Ta funkcja najpierw sprawdza, czy podane dane uwierzytelniające są prawidłowe, korzystając z funkcji invalid_credentials. Jeśli dane są nieprawidłowe, zwraca odpowiednią odpowiedź.

    Następnie, jeśli dane są prawidłowe, funkcja łączy się z bazą danych i pobiera informacje o użytkowniku o podanej nazwie użytkownika. Jeśli taki użytkownik nie istnieje, zwraca odpowiedź z informacją o błędzie.

    Jeśli użytkownik istnieje, funkcja pobiera uprawnienia użytkownika z bazy danych i generuje token JWT, który zawiera nazwę użytkownika, uprawnienia i czas wygaśnięcia.

    Na koniec funkcja zwraca słownik zawierający informacje o wyniku logowania, w tym token JWT, informacje o użytkowniku i jego uprawnienia.

    Argumenty:
    _username (str): Nazwa użytkownika do zalogowania.
    _password (str): Hasło użytkownika do zalogowania.

    Zwraca:
    dict: Słownik zawierający informacje o wyniku logowania. Jeśli logowanie jest pomyślne, słownik zawiera pola 'success', 'token', 'user' i 'permissions'. Jeśli logowanie nie powiedzie się, słownik zawiera pola 'success' i 'msg'.

    Wyjątki:
    Rzuca wyjątek, jeśli wystąpi nieoczekiwany błąd podczas logowania.
    """

    auth_check = invalid_credentials(_username, _password)
    if auth_check != 200:
        return auth_check
    else:
        try:
            conn = conn_to_db()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(
                "Select id,username,first_name,last_name from users where username=%s and deleted=FALSE", (_username,))
            user_exists = cur.fetchone()
            if not user_exists:
                return {"success": False,
                        "msg": "This username does not exist."}
            cur.execute(
                "select role from roles inner join user_roles on roles.id=user_roles.role_id Inner join users on user_roles.user_id=users.id where users.id=%s", (user_exists[0],))
            permissions = [item[0] for item in cur.fetchall()]
            session_id = str(uuid.uuid4())
            token = jwt.encode({'id': user_exists[0], 'username': user_exists[1], 'permisions': permissions, 'exp': datetime.datetime.now(
            ) + datetime.timedelta(minutes=118),
                'session_id': session_id
            }, BaseConfig.SECRET_KEY)

            return {"success": True,
                    "token": token,
                    "user": {'id': user_exists[0],'username': user_exists[1],'first_name':user_exists[2],'last_name':user_exists[3], },
                    "permissions": permissions}

        except Exception as e:
            logger.error("Wystąpił błąd: %s" % e)
            logger.debug('ERROR!', exc_info=True)
            return {"success": False, "msg": "Unexpected error"}

        finally:
            cur.close()
            conn.close()


def invalid_credentials(username: str, password: str) -> Union[int, Tuple[Dict, int]]:
    """
        Sprawdza, czy podane dane uwierzytelniające są prawidłowe.

        Ta funkcja najpierw łączy się z bazą danych i sprawdza, czy istnieje użytkownik o podanej nazwie użytkownika. Jeśli taki użytkownik nie istnieje, zwraca odpowiedź z informacją o błędzie.

        Następnie, jeśli użytkownik istnieje, funkcja sprawdza, czy podane hasło jest prawidłowe. Jeśli hasło jest nieprawidłowe, zwraca odpowiedź z informacją o błędzie.

        

        Argumenty:
        username (str): Nazwa użytkownika do sprawdzenia.
        password (str): Hasło użytkownika do sprawdzenia.

        Zwraca:
         Union[int, dict]: Zwraca 200, jeśli dane uwierzytelniające są prawidłowe. W przeciwnym razie, zwraca słownik zawierający klucze 'success' i 'msg', które opisują błąd.
    """
    try:
        conn = conn_to_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        username_entered = username
        password_entered = password
        cur.execute(
            "Select * from users where username=%s and deleted=FALSE", (username_entered,))
        ub = cur.fetchone()
        if ub != None:
            user_object = User(ub[0], ub[3], ub[4], ub[5])
        else:
            user_object = None

        if user_object is None:
            return {"success": False,
                    "msg": "Username or password is incorrect"}

        elif not pbkdf2_sha256.verify(password_entered, user_object.password):
            return {"success": False,
                    "msg": "Username or password is incorrect"}
        
        return 200

    
    except psycopg2.Error as e:
        conn.rollback()
        logger.error("Wystąpił błąd: %s" % e)
        logger.debug('ERROR!', exc_info=True)
        return {"success": False, "msg": "Unexpected error"}, 500

    finally:
        conn.commit()
        cur.close()
        conn.close()


class CurrectUser:
    def __init__(self, id, username):
        self.id = id
        self.username = username


def UserObjectToJson(user_object: list) -> CurrectUser:
    return CurrectUser(user_object[0], user_object[1])


def is_valid_token_exists_token(token: str) -> bool:
    """
    Sprawdza, czy podany token JWT jest prawidłowy i nie wygasł.

    Argumenty:
    token (str): Token JWT do sprawdzenia.

    Zwraca:
    bool: True jeśli token jest prawidłowy i nie wygasł, False w przeciwnym razie.
    """
    try:
        jwt.decode(token, BaseConfig.SECRET_KEY,
                   algorithms=['HS256'])
        return True
    except jwt.exceptions.DecodeError:
        return False

    except jwt.ExpiredSignatureError:
        return True

    except jwt.exceptions.InvalidTokenError:
        return True

    except Exception:
        return True


def block_token(_jwt_token: str) -> Tuple[Dict, int]:
    """
    Dodaje podany token JWT do listy zablokowanych tokenów w bazie danych.

    Ta funkcja łączy się z bazą danych i dodaje podany token JWT do listy zablokowanych tokenów. Jeśli operacja zakończy się powodzeniem, zwraca słownik z kluczem "success" ustawionym na True i kodem statusu HTTP 200. W przypadku wystąpienia nieoczekiwanego błędu, zwraca słownik z kluczem "success" ustawionym na False, komunikatem o błędzie i kodem statusu HTTP 500.

    Argumenty:
    _jwt_token (str): Token JWT, który ma zostać zablokowany.

    Zwraca:
    dict, int: Słownik zawierający informację o powodzeniu operacji (klucz "success") oraz ewentualny komunikat o błędzie (klucz "msg"), oraz kod statusu HTTP.
    """
    try:
        conn = conn_to_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(
            "Insert into jwt_token_block_list (jwt_token,created_at) Values(%s,%s)", (_jwt_token, datetime.datetime.now(),))
        return {"success": True, "msg": "Zostales Wylogowany pomysnie"}, 200

    except Exception as e:
        conn.rollback()
        logger.error("Wystąpił błąd: %s" % e)
        logger.debug('ERROR!', exc_info=True)
        return {"success": False, "msg": "Unexpected error"}, 500

    finally:
        conn.commit()
        cur.close()
        conn.close()
