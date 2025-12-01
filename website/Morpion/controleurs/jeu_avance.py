from model.model import get_instances_by_id, get_equipe_details, get_equipe_name_color
import random

# ----------------------------
#  UTILITAIRES / CREATION DE L'EQUIPE
# ----------------------------
def create_equipe_list(equipe_data):
    """Crée la liste de morpions pour une équipe avec toutes leurs stats"""
    team_list = []
    for entry in equipe_data:
        name, image, pv, att, mana, reu, id = entry
        team_list.append({
            'name': name,
            'image': image,
            'pv': pv,
            'mana': mana,
            'pv_max': pv,
            'mana_max': mana,
            'att': att,
            'reu': reu,
            'id': id,
            'fireball': 100,
            'heal': 100,
            'armageddon': 100
        })
    return team_list

def roll_success(reu_points):
    """Retourne True si l’action réussit selon les points de réussite"""
    chance = reu_points * 10
    return random.randint(0, 100) < chance

def reward_success(morpion_data):
    """Ajoute 0.5 point de réussite après action réussie"""
    morpion_data['reu'] = morpion_data.get('reu', 0) + 0.5

# ----------------------------
#  ACTIONS DU JEU
# ----------------------------
def attack_action(actor_cell, target_cell):
    """Action d'attaque classique"""
    if not isinstance(actor_cell, dict) or not isinstance(target_cell, dict):
        return "invalid_target"
    if actor_cell['team'] == target_cell['team']:
        return "friendly_fire_blocked"
    if roll_success(actor_cell['reu']):
        reward_success(actor_cell)
        target_cell['pv'] -= actor_cell['att']
        if target_cell['pv'] <= 0:
            target_cell['pv'] = 0
            return "killed"
        return "hit"
    return "miss"

def cast_fireball(actor_cell, target_cell):
    """Sort boule de feu"""
    COST, DMG = 2, 3
    if actor_cell['mana'] < COST:
        return "no_mana"
    if actor_cell['team'] == target_cell['team']:
        return "friendly_fire_blocked"
    actor_cell['mana'] -= COST
    if roll_success(actor_cell['reu']):
        reward_success(actor_cell)
        target_cell['pv'] -= DMG
        if target_cell['pv'] <= 0:
            target_cell['pv'] = 0
            return "killed"
        return "hit"
    return "miss"

def cast_heal(actor_cell, target_cell):
    """Sort de soin"""
    COST, HEAL = 1, 2
    if actor_cell['mana'] < COST:
        return "no_mana"
    if actor_cell['team'] != target_cell['team']:
        return "heal_enemy_blocked"
    actor_cell['mana'] -= COST
    if roll_success(actor_cell['reu']):
        reward_success(actor_cell)
        target_cell['pv'] += HEAL
        if target_cell['pv'] > target_cell['pv_max']:
            target_cell['pv'] = target_cell['pv_max']
        return "healed"
    return "miss"

def cast_armageddon(actor_cell, board, target_index):
    """Sort Armageddon détruisant une case"""
    COST = 5
    if actor_cell['mana'] < COST:
        return "no_mana"
    if target_index < 0 or target_index >= len(board):
        return "invalid_target"
    cell = board[target_index]
    if isinstance(cell, dict) and cell['team'] == actor_cell['team']:
        return "kill_self_blocked"
    actor_cell['mana'] -= COST
    if roll_success(actor_cell['reu']):
        reward_success(actor_cell)
        if isinstance(cell, dict):
            cell['pv'] = 0
        board[target_index] = "X"
        return "destroyed"
    return "miss"

# ----------------------------
#  UTILITAIRES PLATEAU
# ----------------------------
def find_board_index_by_card_id(board, card_id):
    """Retourne l'index d'une carte sur le plateau via son ID"""
    for i, c in enumerate(board):
        if isinstance(c, dict) and str(c.get('id')) == str(card_id):
            return i
    return None

def update_cell_percents(cell):
    """Met à jour les pourcentages de PV et Mana pour l'affichage"""
    if not isinstance(cell, dict):
        return
    cell['pv_percent'] = int(cell.get('pv', 0) / max(cell.get('pv_max', 1), 1) * 100)
    cell['mana_percent'] = int(cell.get('mana', 0) / max(cell.get('mana_max', 1), 1) * 100)

def remove_dead_from_board(board):
    """Supprime les cartes mortes du plateau"""
    for i, c in enumerate(board):
        if isinstance(c, dict) and c.get('pv', 0) <= 0:
            board[i] = ""

# ----------------------------
#  INITIALISATION DE LA PARTIE
# ----------------------------
size = None
game_id = None
if 'max_turn_av' not in SESSION:
    max_turn = None
else:
    max_turn = SESSION['max_turn_av']

if GET and 'game_id' in GET:
    game_id = int(GET['game_id'][0])
elif POST and 'game_id' in POST:
    game_id = int(POST['game_id'][0])

if game_id is not None:
    REQUEST_VARS['current_game_id'] = game_id
    if 'eq1_data' not in SESSION or 'eq2_data' not in SESSION:
        game_data = get_instances_by_id(SESSION['CONNEXION'], 'partie', game_id)
        config_id = game_data[0][3]
        config_data = get_instances_by_id(SESSION['CONNEXION'], 'configuration', config_id)

        eq1_id, eq2_id = game_data[0][1], game_data[0][2]

        SESSION['eq1_data'] = create_equipe_list(get_equipe_details(SESSION['CONNEXION'], eq1_id))
        SESSION['eq2_data'] = create_equipe_list(get_equipe_details(SESSION['CONNEXION'], eq2_id))

        SESSION['eq1_name_col'] = get_equipe_name_color(SESSION['CONNEXION'], eq1_id)
        SESSION['eq2_name_col'] = get_equipe_name_color(SESSION['CONNEXION'], eq2_id)

        size = config_data[0][1]
        max_turn = config_data[0][2]  # Nombre maximal de tours
        SESSION['max_turn_av'] = max_turn

# ----------------------------
#  INITIALISATION PLATEAU / SESSION
# ----------------------------
if size is None:
    size = 3
SESSION.setdefault('board_av', [""] * (size * size))
board = SESSION['board_av']
REQUEST_VARS['board_av'] = board
REQUEST_VARS['grid_size'] = size

SESSION.setdefault('p1_turn', True)
SESSION.setdefault('p2_turn', False)
SESSION.setdefault('turn_count', 0)   # compteur de tours
SESSION.setdefault('game_over', False)

# ----------------------------
#  FONCTION DE FIN DE TOUR ET FIN DE JEU
# ----------------------------
def end_turn_if_needed(action_result, max_turn):
    """
    Incrémente le compteur de tours après une action valide.
    Termine la partie si le nombre maximal de tours est atteint.
    """
    if action_result not in ("actor_not_found", "target_not_found", "actor_not_yours", "target_not_adjacent"):
        SESSION['turn_count'] += 1
        print(f"[DEBUG] Tour {SESSION['turn_count']} / {max_turn}")

        # Changement de joueur
        SESSION['p1_turn'] = not SESSION['p1_turn']
        SESSION['p2_turn'] = not SESSION['p2_turn']
        print(f"[DEBUG] Changement de tour: P1={SESSION['p1_turn']}, P2={SESSION['p2_turn']}")

        # Vérifier fin de partie
        if SESSION['turn_count'] >= max_turn:
            SESSION['game_over'] = True
            REQUEST_VARS['game_over'] = True
            print("[DEBUG] Nombre maximal de tours atteint, fin de la partie !")

# ----------------------------
#  TRAITEMENT PLACEMENT
# ----------------------------
if POST and POST.get('action_type', [None])[0] == 'place':
    move = int(POST['selected_move'][0])
    selected_id = int(POST['selected_card'][0])
    print(f"[DEBUG] PLACE action: card_id={selected_id}, move={move}")

    selected_card, selected_team, color = None, None, None

    if SESSION['p1_turn']:
        for inst in SESSION['eq1_data']:
            if inst['id'] == selected_id:
                selected_card = inst
                selected_team = 'eq1'
                color = SESSION['eq1_name_col'][0][1]
                break
    elif SESSION['p2_turn']:
        for inst in SESSION['eq2_data']:
            if inst['id'] == selected_id:
                selected_card = inst
                selected_team = 'eq2'
                color = SESSION['eq2_name_col'][0][1]
                break

    if selected_card and board[move] == "":
        board[move] = {
            **selected_card,
            'color': color,
            'team': 1 if selected_team == 'eq1' else 2,
            'pv_percent': int(selected_card['pv'] / selected_card['pv_max'] * 100),
            'mana_percent': int(selected_card['mana'] / selected_card['mana_max'] * 100)
        }
        print(f"[DEBUG] Carte {selected_card['name']} placée en position {move}")

        if selected_team == 'eq1':
            SESSION['eq1_data'] = [c for c in SESSION['eq1_data'] if c['id'] != selected_id]
        else:
            SESSION['eq2_data'] = [c for c in SESSION['eq2_data'] if c['id'] != selected_id]

        end_turn_if_needed("valid_place", max_turn)

# ----------------------------
#  TRAITEMENT SORTS / ATTAQUES
# ----------------------------
if POST and POST.get('action_type', [None])[0] == 'ability':
    acting_card_id = POST.get('acting_card', [None])[0]
    ability_name = POST.get('ability', [None])[0]
    ability_target_id = POST.get('ability_target', [None])[0]

    print(f"[DEBUG] ABILITY action: actor={acting_card_id}, ability={ability_name}, target={ability_target_id}")

    action_result = None

    # --- Trouver l'acteur ---
    a_idx = find_board_index_by_card_id(board, acting_card_id)
    if a_idx is None:
        action_result = "actor_not_found"
        print(f"[DEBUG] Acteur introuvable sur le plateau: {acting_card_id}")
    else:
        actor_cell = board[a_idx]
        currentPlayer = 1 if SESSION['p1_turn'] else 2
        print(f"[DEBUG] Acteur trouvé à l'index {a_idx}, team={actor_cell['team']}")

        if actor_cell['team'] != currentPlayer:
            action_result = "actor_not_yours"
            print("[DEBUG] L'acteur n'appartient pas au joueur courant")
        else:
            # --- Trouver la cible ---
            target_index = find_board_index_by_card_id(board, ability_target_id)
            if target_index is None:
                action_result = "target_not_found"
                print(f"[DEBUG] Cible introuvable: {ability_target_id}")
            else:
                target_cell = board[target_index]
                print(f"[DEBUG] Cible trouvée à l'index {target_index}")

                if not isinstance(target_cell, dict):
                    action_result = "invalid_target"
                    print("[DEBUG] Cible invalide")
                else:
                    # --- Exécuter la capacité ---
                    if ability_name == 'attack':
                        r1, c1 = divmod(a_idx, size)
                        r2, c2 = divmod(target_index, size)
                        if abs(r1 - r2) + abs(c1 - c2) != 1:
                            action_result = "target_not_adjacent"
                            print("[DEBUG] Cible non adjacente")
                        else:
                            action_result = attack_action(actor_cell, target_cell)
                            print(f"[DEBUG] Résultat attaque: {action_result}")

                    elif ability_name == 'fireball':
                        action_result = cast_fireball(actor_cell, target_cell)
                        print(f"[DEBUG] Résultat fireball: {action_result}")

                    elif ability_name == 'heal':
                        action_result = cast_heal(actor_cell, target_cell)
                        print(f"[DEBUG] Résultat heal: {action_result}")

                    elif ability_name == 'armageddon':
                        action_result = cast_armageddon(actor_cell, board, target_index)
                        print(f"[DEBUG] Résultat armageddon: {action_result}")

                    else:
                        action_result = "unknown_ability"
                        print(f"[DEBUG] Capacité inconnue: {ability_name}")

    remove_dead_from_board(board)
    for cell in board:
        if isinstance(cell, dict):
            update_cell_percents(cell)

    print("[DEBUG] État du plateau après action:")
    for i, c in enumerate(board):
        if isinstance(c, dict):
            print(f"  Index {i}: {c['name']} PV={c['pv']} Mana={c['mana']}")
        else:
            print(f"  Index {i}: vide")

    end_turn_if_needed(action_result, max_turn)

    SESSION['board_av'] = board
    REQUEST_VARS['board_av'] = board
    REQUEST_VARS['last_action_result'] = action_result
    print(f"[DEBUG] Résultat de l'action: {action_result}")
