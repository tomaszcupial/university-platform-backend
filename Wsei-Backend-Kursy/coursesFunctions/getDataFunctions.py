from background.connections import conn_to_db
import psycopg2
from background.logsconf import logger

def get_courses():
    try:
        conn =conn_to_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cur.execute("""
            SELECT json_agg(row_to_json(t)) 
            FROM (
                SELECT id, name, description, id_user
                FROM courses
            ) t
        """)

        rows = cur.fetchall()[0]
        
        cur.close()
        conn.close()

        return {"success": True,
                "data": rows
                }
    
    except Exception as e:
        logger.error("Wystąpił błąd: %s" % e)
        logger.debug('ERROR!', exc_info=True)
        return {"success": False, "msg": "Unexpected error"}

    finally:
        cur.close()
        conn.close()
