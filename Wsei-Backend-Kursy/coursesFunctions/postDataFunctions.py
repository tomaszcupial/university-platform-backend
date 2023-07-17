import psycopg2
from background.connections import conn_to_db
from background.logsconf import logger
def sign_to_course(id_user, id_course):
    try:
        conn = conn_to_db()
        cur = conn.cursor()

        # Sprawdzanie, czy użytkownik istnieje
        cur.execute("SELECT * FROM users WHERE id = %s", (id_user,))
        user = cur.fetchone()
        if not user:
            return {"success": False, "msg": "Podany użytkownik nie istnieje"}

        # Sprawdzanie, czy kurs istnieje
        cur.execute("SELECT * FROM courses WHERE id = %s", (id_course,))
        course = cur.fetchone()
        if not course:
            return {"success": False, "msg": "Podany kurs nie istnieje"}

        # Zapisanie użytkownika do kursu
        cur.execute("INSERT INTO users_courses (id_user, id_course) VALUES (%s, %s)", (id_user, id_course))
        
        conn.commit()
        
        

        return {"success": True, "msg": "Dołaczono pomyśnie"}

    except Exception as e:
        conn.rollback()
        logger.error("Wystąpił błąd: %s" % e)
        logger.debug('ERROR!', exc_info=True)
        return {"success": False, "msg": "Unexpected error"}

    finally:
        cur.close()
        conn.close()