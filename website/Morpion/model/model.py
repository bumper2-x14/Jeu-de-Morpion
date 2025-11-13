import psycopg
from psycopg import sql
from logzero import logger
from datetime import datetime

def get_morpion(connexion):
    table = "morpion"
    query = f"""
                SELECT * FROM morpion;
            """
    with connexion.cursor() as cursor:
        try:
            cursor.execute(query)
            res = cursor.fetchall()
            return res
        except psycopg.Error as e:
            logger.error(e)
        
    return None