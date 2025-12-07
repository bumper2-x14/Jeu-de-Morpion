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

#===========================================================
# ===============   FONCTIONS SPÉCIFIQUES   =================
#===========================================================


def get_instances(connexion, table_name):
    """
    Récupère toutes les lignes d'une table.

    Paramètres:
      - connexion: objet de connexion psycopg
      - table_name: nom de la table (string)

    Retour:
      - liste de tuples avec les lignes, ou None.
    """
    query = sql.SQL('SELECT * FROM {tab}').format(tab=sql.Identifier(table_name))
    return select_query(connexion, query)


def get_instances_by_id(connexion, table_name, id):
    """
    Récupère les lignes d'une table correspondant à un id donné.

    Paramètres:
      - connexion: objet de connexion psycopg
      - table_name: nom de la table
      - id: identifiant recherché

    Retour:
      - liste de tuples correspondant à l'id, ou None.
    """
    query = sql.SQL("SELECT * FROM {table} WHERE id = %s").format(
        table=sql.Identifier(table_name)
    )
    return select_query(connexion, query, [id])


def get_column(connexion, table_name, att_name):
    """
    Récupère une colonne spécifique pour toutes les lignes d'une table.

    Paramètres:
      - connexion: objet de connexion psycopg
      - table_name: nom de la table
      - att_name: nom de la colonne à récupérer

    Retour:
      - liste des valeurs de la colonne (une par ligne), ou None.
    """
    query = sql.SQL('SELECT {att} FROM {tab}').format(
        att=sql.Identifier(att_name),
        tab=sql.Identifier(table_name)
    )
    res = select_query(connexion, query)  
    return [r[0] for r in res]

    

def get_equipe_details(connexion, eq_id):
    """
    Récupère les détails (morpions) d'une équipe.

    Paramètres:
      - connexion: objet de connexion psycopg
      - eq_id: identifiant de l'équipe

    Retour:
      - liste de tuples (name, image, hp, attack, mana, skill, id) pour chaque morpion.
    """
    query = """
        SELECT m.name, m.image, m.hp, m.attack, m.mana, m.skill, m.id
        FROM equipe e
        JOIN equipe_morpion em ON e.id = em.equipe_id
        JOIN morpion m ON em.morpion_id = m.id
        WHERE e.id = %s
        """
    return select_query(connexion, query, [eq_id])


def get_equipe_name_color(connexion, eq_id):
    """
    Récupère le nom et la couleur d'une équipe.

    Paramètres:
      - connexion: objet de connexion psycopg
      - eq_id: identifiant de l'équipe

    Retour:
      - liste de tuples (name, color, id).
    """
    query = """
            SELECT name, color, id from equipe WHERE id = %s    
        """
    return select_query(connexion, query, [eq_id])


def create_equipe(connexion, eq_name, eq_color, eq_morpions, nb_morpions):
    """
    Crée une nouvelle équipe et associe des morpions à cette équipe.

    Paramètres:
      - connexion: objet de connexion psycopg
      - eq_name: nom de l'équipe
      - eq_color: couleur de l'équipe
      - eq_morpions: itérable d'IDs de morpions à associer
      - nb_morpions: nombre de morpions à insérer

    Retour:
      - id de l'équipe créée (via RETURNING) ou None si échec.
    """
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
    """
    Supprime une équipe et ses références (parties et associations morpions).

    Paramètres:
      - connexion: objet de connexion psycopg
      - eq_id: identifiant de l'équipe à supprimer

    Retour:
      - True si toutes les suppressions ont réussi, False sinon.
    """
    query_partie_a = """
        DELETE FROM partie WHERE equipe1_id = %s OR equipe2_id = %s
    """
    query_eq_morp = """
        DELETE FROM equipe_morpion WHERE equipe_id = %s
    """
    query_eq = """ 
        DELETE FROM equipe WHERE id = %s
    """
    success_partie = delete_query(connexion, query_partie_a, [eq_id, eq_id])
    if not success_partie:
        return False 
    success_morp = delete_query(connexion, query_eq_morp, [eq_id])
    if not success_morp:
        return False
    success_eq = delete_query(connexion, query_eq, [eq_id])
    return success_eq


def insert_to_config(connexion, grid_size, max_turn):
    """
    Insère une nouvelle configuration (taille de grille et max tours).

    Paramètres:
      - connexion: objet de connexion psycopg
      - grid_size: taille de la grille
      - max_turn: nombre maximal de tours

    Retour:
      - True si l'insertion a réussi, False sinon.
    """
    query = sql.SQL("""
            INSERT INTO configuration (grid_size, max_turns)
            VALUES (%s, %s) 
            """)
    
    return insert_query(connexion, query, [grid_size, max_turn])


def get_last_config(connexion):
    """
    Récupère la dernière configuration insérée (la plus récente).

    Paramètres:
      - connexion: objet de connexion psycopg

    Retour:
      - dictionnaire avec id, grid_size et max_turns ou None.
    """
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
    """
    Compte le nombre d'instances (lignes) d'une table.

    Paramètres:
      - connexion: objet de connexion psycopg
      - table_name: nom de la table

    Retour:
      - résultat du SELECT COUNT, ou None.
    """
    query = sql.SQL("SELECT COUNT(id) FROM {tab}").format(tab=sql.Identifier(table_name)) 
    
    return select_query(connexion, query)


def create_partie(connexion, grid_size, mx_turn, eq1_id, eq2_id):
    """
    Crée une nouvelle partie (configuration + entrée partie).

    Paramètres:
      - connexion: objet de connexion psycopg
      - grid_size: taille de la grille
      - mx_turn: nombre maximal de tours
      - eq1_id, eq2_id: identifiants des équipes participantes

    Retour:
      - id de la partie créée, ou None si échec.
    """
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
    """
    Supprime une partie et ses dépendances (journal, configuration).

    Paramètres:
      - connexion: objet de connexion psycopg
      - prt_id: identifiant de la partie à supprimer

    Retour:
      - True si toutes les suppressions ont réussi, False sinon.
    """
    query_config = """
        DELETE FROM configuration
        WHERE id = (
            SELECT config_id FROM partie WHERE id = %s
        )
    """
    query_journal = """
        DELETE FROM journal WHERE partie_id = %s
    """
    query_partie = """ 
        DELETE FROM partie WHERE id = %s
    """
    success_journal = delete_query(connexion, query_journal, [prt_id])
    if not success_journal:
        return False
    success_partie = delete_query(connexion, query_partie, [prt_id])
    if not success_partie:
        return False
    success_config = delete_query(connexion, query_config, [prt_id])
    return success_config   


def update_partie_winner(connexion, prt_id, winner_id, max_turns_reached=False):
    """
    Met à jour l'entrée 'partie' pour enregistrer le gagnant et la date de fin.

    Paramètres:
      - connexion: objet de connexion psycopg
      - prt_id: id de la partie
      - winner_id: id de l'équipe gagnante
      - max_turns_reached: bool si la partie s'est terminée par max tours

    Retour:
      - True si la mise à jour a réussi, False sinon.
    """
    query= sql.SQL("""
        UPDATE partie
        SET winning_equipe_id = %s,
            end_time = %s,
            max_turns_reached = %s
        WHERE id = %s
    """)
    return update_query(connexion, query, [winner_id, datetime.now(), max_turns_reached, prt_id])
        

def get_game_hist(connexion):
    """
    Récupère l'historique de parties (équipes et gagnants).

    Paramètres:
      - connexion: objet de connexion psycopg

    Retour:
      - liste de tuples décrivant les parties et le gagnant.
    """
    query="""
    SELECT e1.name AS name1, e2.name AS name2, ew.name as winner, p.id AS partie_id
    FROM partie p
    JOIN equipe e1 ON p.equipe1_id = e1.id
    JOIN equipe e2 ON p.equipe2_id = e2.id
    JOIN equipe ew ON p.winning_equipe_id = ew.id; 
    """
    return select_query(connexion, query)


def get_team_hist(connexion, eq_id):
    """
    Récupère l'historique des parties pour une équipe donnée.

    Paramètres:
      - connexion: objet de connexion psycopg
      - eq_id: identifiant de l'équipe

    Retour:
      - liste de tuples avec les informations de parties impliquant l'équipe.
    """
    query="""
    SELECT 
    e1.name AS name1, e1.id AS id1,
    e2.name AS name2, e2.id AS id2,
    ew.name as winner, start_time, p.id AS partie_id 
    FROM partie p
    JOIN equipe e1 ON p.equipe1_id = e1.id
    JOIN equipe e2 ON p.equipe2_id = e2.id
    JOIN equipe ew ON p.winning_equipe_id = ew.id
    WHERE e1.id=%s OR e2.id=%s  
    """
    return select_query(connexion, query, [eq_id, eq_id])


def insert_into_journal(connexion, partie_id, seq, text):
    """
    Insère une ligne dans le journal d'une partie.

    Paramètres:
      - connexion: objet de connexion psycopg
      - partie_id: identifiant de la partie
      - seq: numéro de séquence/ordre de l'entrée
      - text: texte à insérer dans le journal

    Retour:
      - True si l'insertion a réussi, False sinon.
    """
    query= sql.SQL("""INSERT INTO journal(partie_id, seq, text)
                   values(%s,%s,%s)""")
    return insert_query(connexion, query, [partie_id, seq, text])


def get_journal_by_prt_id(connexion, prt_id):
    """
    Récupère toutes les entrées du journal pour une partie donnée.

    Paramètres:
      - connexion: objet de connexion psycopg
      - prt_id: identifiant de la partie

    Retour:
      - liste de tuples (seq, text) ou None.
    """
    query="""
    SELECT seq, text
    FROM journal 
    WHERE partie_id = %s
    """
    return select_query(connexion, query,[prt_id])  



def game_duration(connexion, prt_id):
    """
    Calcule la durée d'une partie (end_time - start_time).

    Paramètres:
      - connexion: objet de connexion psycopg
      - prt_id: identifiant de la partie

    Retour:
      - timedelta de la durée si disponible, sinon None.
    """
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

def get_min_max_duration_game(connexion):
    """
    Récupère la partie la plus courte et la plus longue (durée).

    Paramètres:
      - connexion: objet de connexion psycopg

    Retour:
      - liste/tuple contenant informations sur les parties min/max.
    """
    query = """
        SELECT 
        p_min.min_duration,
        e1_min.name AS team1_min,
        e2_min.name AS team2_min,
        p_max.max_duration,
        e1_max.name AS team1_max,
        e2_max.name AS team2_max
    FROM
        (SELECT id, equipe1_id, equipe2_id, end_time - start_time AS min_duration
        FROM partie
        WHERE end_time IS NOT NULL
        ORDER BY min_duration ASC
        LIMIT 1) AS p_min
    JOIN equipe e1_min ON e1_min.id = p_min.equipe1_id
    JOIN equipe e2_min ON e2_min.id = p_min.equipe2_id,
        (SELECT id, equipe1_id, equipe2_id, end_time - start_time AS max_duration
        FROM partie
        WHERE end_time IS NOT NULL
        ORDER BY max_duration DESC
        LIMIT 1) AS p_max
    JOIN equipe e1_max ON e1_max.id = p_max.equipe1_id
    JOIN equipe e2_max ON e2_max.id = p_max.equipe2_id;
    """
    return select_query(connexion, query)



def get_top_3_teams(connexion):
    """
    Récupère les trois équipes ayant le plus de victoires.

    Paramètres:
      - connexion: objet de connexion psycopg

    Retour:
      - liste de tuples (team_name, wins) ordonnée par victoires décroissantes.
    """
    query ="""
    SELECT e.name, COUNT(*) AS wins
    FROM partie p
    JOIN equipe e ON p.winning_equipe_id = e.id
    WHERE p.winning_equipe_id IS NOT NULL
    GROUP BY e.id, e.name
    ORDER BY wins DESC
    LIMIT 3
    """
    return select_query(connexion, query)
