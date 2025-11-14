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
    with connexion.cursor() as cursor:  # ← CORRECTION : ajouter les parenthèses après cursor()
        try:
            cursor.execute(query, param)
            connexion.commit()  # ← CORRECTION : commit() doit être appelé sur la connexion, pas le curseur
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
    with connexion.cursor() as cursor:  # ← ajouter ()
        try:
            cursor.execute(query, param)
            connexion.commit()  # ← corriger ici aussi
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
    with connexion.cursor() as cursor:  # ← ajouter ()
        try:
            cursor.execute(query, param)
            connexion.commit()  # ← corriger ici aussi
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
    query = sql.SQL('SELECT {att} FROM {tab}').format(att=sql.Identifier(att_name), tab=sql.Identifier(table_name))
    return select_query(connexion, query)
    

def get_equipe_details(connexion, eq_id):
    query = """
        SELECT m.name, m.image, m.hp, m.attack, m.mana, m.skill
        FROM equipe e
        JOIN equipe_morpion em ON e.id = em.equipe_id
        JOIN morpion m ON em.morpion_id = m.id
        WHERE e.id = %s
        """
    
    return select_query(connexion, query, [eq_id])
    
    
