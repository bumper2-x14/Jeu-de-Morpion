import psycopg
from psycopg import sql
from logzero import logger
from datetime import datetime


# ============================================================
# ===============   FONCTIONS CRUD (BASE DE DONNÉES)   =======
# ============================================================

# ------------------------------------------------------------
# LECTURE (SELECT)
# ------------------------------------------------------------
# Cette fonction exécute une requête SELECT sur la base de données.
# - connexion : objet de connexion à la base
# - query     : requête SQL à exécuter (peut être un objet sql.SQL)
# - param     : liste des paramètres à passer à la requête
# Retourne : le résultat de la requête (liste de tuples) ou None en cas d'erreur.
def select_query(connexion, query, param=[]):
    with connexion.cursor() as cursor:
        try:
            cursor.execute(query, param)
            res = cursor.fetchall()
            return res
        except psycopg.Error as err:
            logger.error("Erreur de base de données : %s", err)
    
    return None


# ------------------------------------------------------------
# INSERTION (INSERT)
# ------------------------------------------------------------
# Cette fonction insère de nouvelles données dans la base.
# - connexion : objet de connexion à la base
# - query     : requête SQL d'insertion
# - param     : liste des valeurs à insérer
# Retourne True si l’insertion réussit, False sinon.
def insert_query(connexion, query, param=[]):
    with connexion.cursor() as cursor:  
        try:
            cursor.execute(query, param)
            connexion.commit() 
            return True
        except psycopg.Error as err:
            connexion.rollback()
            logger.error("INSERT échoué : %s", err)
            return False


# ------------------------------------------------------------
# MISE À JOUR (UPDATE)
# ------------------------------------------------------------
# Cette fonction met à jour des enregistrements existants.
# - connexion : objet de connexion à la base
# - query     : requête SQL de mise à jour
# - param     : paramètres associés à la requête
# Retourne True si la mise à jour réussit, False sinon.
def update_query(connexion, query, param=[]):
    with connexion.cursor() as cursor: 
        try:
            cursor.execute(query, param)
            connexion.commit()  
            return True
        except psycopg.Error as err:
            connexion.rollback()
            logger.error("UPDATE échoué : %s", err)
            return False


# ------------------------------------------------------------
# SUPPRESSION (DELETE)
# ------------------------------------------------------------
# Cette fonction supprime un ou plusieurs enregistrements de la base.
# - connexion : objet de connexion à la base
# - query     : requête SQL de suppression
# - param     : paramètres associés à la requête
# Retourne True si la suppression réussit, False sinon.
def delete_query(connexion, query, param=[]):
    with connexion.cursor() as cursor: 
        try:
            cursor.execute(query, param)
            connexion.commit()  
            return True
        except psycopg.Error as err:
            connexion.rollback()
            logger.error("DELETE échoué : %s", err)
            return False


# ------------------------------------------------------------
# RÉCUPÉRATION DES ENREGISTREMENTS D’UNE TABLE
# ------------------------------------------------------------
# Cette fonction récupère toutes les lignes d'une table donnée.
# - connexion : objet de connexion à la base
# - nom_table : nom de la table dont on veut les données
# Retourne : le résultat du SELECT (liste de tuples) ou None.
def get_instances(connexion, table_name):
    query = sql.SQL('SELECT * FROM {tab}').format(tab=sql.Identifier(table_name))
    return select_query(connexion, query)


def get_instances_by_id(connexion, table_name, id):
    query = sql.SQL("SELECT * FROM {table} WHERE id = %s").format(
        table=sql.Identifier(table_name)
    )
    return select_query(connexion, query, [id])


def get_column(connexion, table_name, att_name):
    query = sql.SQL('SELECT {att} FROM {tab}').format(
        att=sql.Identifier(att_name),
        tab=sql.Identifier(table_name)
    )
    res = select_query(connexion, query)  
    return [r[0] for r in res]

    

def get_equipe_details(connexion, eq_id):
    query = """
        SELECT m.name, m.image, m.hp, m.attack, m.mana, m.skill, m.id
        FROM equipe e
        JOIN equipe_morpion em ON e.id = em.equipe_id
        JOIN morpion m ON em.morpion_id = m.id
        WHERE e.id = %s
        """
    return select_query(connexion, query, [eq_id])


def get_equipe_name_color(connexion, eq_id):
    query = """
            SELECT name, color, id from equipe WHERE id = %s    
        """
    return select_query(connexion, query, [eq_id])


def create_equipe(connexion, eq_name, eq_color, eq_morpions, nb_morpions):
    insert_eq_query = """
        INSERT INTO equipe (name, color)
        VALUES (%s, %s)
        RETURNING id;
    """

    with connexion.cursor() as cursor:
        cursor.execute(insert_eq_query, [eq_name, eq_color])
        eq_id = cursor.fetchone()[0]
        connexion.commit()

    values_placeholder = ", ".join(["(%s, %s)"] * nb_morpions)

    insert_morpions_query = f"""
        INSERT INTO equipe_morpion (equipe_id, morpion_id)
        VALUES {values_placeholder};
    """

    params = []
    for m in eq_morpions:
        params.extend([eq_id, m])
    
    insert_query(connexion, insert_morpions_query, params)


def delete_equipe(connexion, eq_id):
    query_eq_morp = """
        DELETE FROM equipe_morpion WHERE equipe_id = %s
    """

    query_eq = """ 
        DELETE FROM equipe WHERE id = %s
    """

    return delete_query(connexion, query_eq_morp, [eq_id]) and delete_query(connexion, query_eq, [eq_id])



def insert_to_config(connexion, grid_size, max_turn):
    query = sql.SQL("""
            INSERT INTO configuration (grid_size, max_turns)
            VALUES (%s, %s) 
            """)
    
    return insert_query(connexion, query, [grid_size, max_turn])


def get_last_config(connexion):
    with connexion.cursor() as cursor:
        cursor.execute("""
            SELECT id, grid_size, max_turns
            FROM configuration
            ORDER BY id DESC
            LIMIT 1
        """)
        row = cursor.fetchone()

    if row is None:
        return None
    
    return {
        "id": row[0],
        "grid_size": row[1],
        "max_turns": row[2],
    }   

def get_nb_instances(connexion, table_name):
    query = sql.SQL("SELECT COUNT(id) FROM {tab}").format(tab=sql.Identifier(table_name)) 
    
    return select_query(connexion, query)


def create_partie(connexion, grid_size, mx_turn, eq1_id, eq2_id):
    config_query = sql.SQL("""
            INSERT INTO configuration (grid_size, max_turns)
            VALUES (%s, %s)
            RETURNING id 
    """)

    partie_query = sql.SQL("""
            INSERT INTO partie (equipe1_id, equipe2_id, config_id)
            VALUES (%s, %s, %s) 
            RETURNING id
    """)
    
    with connexion.cursor() as cursor:
        try:
            cursor.execute(config_query, [grid_size, mx_turn])
            config_id = cursor.fetchone()[0]
            cursor.execute(partie_query, [eq1_id, eq2_id, config_id])
            partie_id = cursor.fetchone()[0]
            connexion.commit()
            return partie_id
        except psycopg.Error as err:
            connexion.rollback()
            logger.error("Insertion de Partie: %s", err)
            return None
    
def delete_partie(connexion, prt_id):
    query_config = """
        DELETE FROM configuration
        WHERE id = (
            SELECT config_id FROM partie WHERE id = %s
        )
    """

    query_partie = """ 
        DELETE FROM partie WHERE id = %s
    """
    return delete_query(connexion, query_partie, [prt_id]) and delete_query(connexion, query_config, [prt_id])


def update_partie_winner(connexion, prt_id, winner_id, max_turns_reached=False):
    query= sql.SQL("""
        UPDATE partie
        SET winning_equipe_id = %s,
            end_time = %s,
            max_turns_reached = %s
        WHERE id = %s
    """)
    return update_query(connexion, query, [winner_id, datetime.now(), max_turns_reached, prt_id])
        

def get_game_hist(connexion):
    query="""
    SELECT e1.name AS name1, e2.name AS name2, ew.name as winner
    FROM partie p
    JOIN equipe e1 ON p.equipe1_id = e1.id
    JOIN equipe e2 ON p.equipe2_id = e2.id
    JOIN equipe ew ON p.winning_equipe_id = ew.id; 
    """
    return select_query(connexion, query)


def get_team_hist(connexion, eq_id):
    query="""
    SELECT 
    e1.name AS name1, e1.id AS id1,
    e2.name AS name2, e2.id AS id2,
    ew.name as winner, start_time  
    FROM partie p
    JOIN equipe e1 ON p.equipe1_id = e1.id
    JOIN equipe e2 ON p.equipe2_id = e2.id
    JOIN equipe ew ON p.winning_equipe_id = ew.id
    WHERE e1.id=%s OR e2.id=%s
    """
    return select_query(connexion, query, [eq_id, eq_id])


def insert_into_journal(connexion, partie_id, seq, text):
    query= sql.SQL("""INSERT INTO journal(partie_id, seq, text)
                   values(%s,%s,%s)""")
    return insert_query(connexion, query, [partie_id, seq, text])


def get_journal_by_id(connexion, prt_id):
    query="""
    SELECT seq, text
    FROM journal 
    WHERE partie_id = %s
    """
    return select_query(connexion, query,[prt_id])  


def game_duration(connexion, prt_id):
    query="""
    SELECT start_time, end_time
    FROM partie 
    WHERE id = %s
    """
    res = select_query(connexion, query,[prt_id])  
    if res and res[0][1]:
        start_time = res[0][0]
        end_time = res[0][1]
        duration = end_time - start_time
        return duration
    return None


