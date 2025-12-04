from model.model import get_instances_by_id, get_equipe_details, get_equipe_name_color, delete_partie, update_partie_winner, insert_into_journal
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


def win_check(board, player_team, move_pos, size):
    """
    Vérifie si un joueur gagne après avoir joué à move_pos.
    player_team = 1 ou 2.
    """
    row = move_pos // size
    col = move_pos % size

    # ----- Vérifier ligne -----
    row_cells = []
    for c in range(size):
        cell = board[row * size + c]
        if isinstance(cell, dict) and cell.get('team') == player_team:
            row_cells.append(row * size + c)
    if len(row_cells) == size:
        return row_cells

    # ----- Vérifier colonne -----
    col_cells = []
    for r in range(size):
        cell = board[r * size + col]
        if isinstance(cell, dict) and cell.get('team') == player_team:
            col_cells.append(r * size + col)
    if len(col_cells) == size:
        return col_cells

    # ----- Vérifier diagonale principale -----
    if row == col:
        diag1 = []
        for i in range(size):
            cell = board[i * size + i]
            if isinstance(cell, dict) and cell.get('team') == player_team:
                diag1.append(i * size + i)
        if len(diag1) == size:
            return diag1

    # ----- Vérifier diagonale secondaire -----
    if row + col == size - 1:
        diag2 = []
        for i in range(size):
            idx = i * size + (size - i - 1)
            cell = board[idx]
            if isinstance(cell, dict) and cell.get('team') == player_team:
                diag2.append(idx)
        if len(diag2) == size:
            return diag2

    return None

def evaluate_victory(board, size, last_move=None, last_team=None):
    """
    Évalue s'il y a une victoire.
    Retourne un tuple (winner_team, winning_cells) :
      - winner_team: 1, 2, 'draw', or None
      - winning_cells: list of indices pour surligner ou None
    Utilise win_check si last_move & last_team fournis; sinon vérifie élimination.
    NOTE: la vérification d'élimination tient désormais compte des réserves
          (SESSION['eq1_data'] / SESSION['eq2_data']) pour éviter de conclure
          qu'une équipe est éliminée simplement parce qu'elle n'a pas encore
          posé de carte sur le plateau.
    """
    # 1) Si un alignement a été réalisé (si dernière action fournie)
    if last_move is not None and last_team is not None:
        result = win_check(board, last_team, last_move, size)
        if result:
            return last_team, result

    # 2) Victoire par élimination : si une équipe n'a plus de morpions
    #    SUR LE PLATEAU **ET** n'a plus de cartes dans sa réserve.
    team1_on_board = any(isinstance(c, dict) and c.get('team') == 1 for c in board)
    team2_on_board = any(isinstance(c, dict) and c.get('team') == 2 for c in board)

    team1_in_reserve = bool(SESSION.get('eq1_data'))  # True si la réserve contient encore des cartes
    team2_in_reserve = bool(SESSION.get('eq2_data'))

    # Si l'équipe 1 possède encore des cartes sur le plateau
    # et l'équipe 2 n'a ni cartes sur le plateau ni en réserve => victoire 1
    if team1_on_board and not team2_on_board and not team2_in_reserve:
        return 1, None

    # Si l'équipe 2 possède encore des cartes sur le plateau
    # et l'équipe 1 n'a ni cartes sur le plateau ni en réserve => victoire 2
    if team2_on_board and not team1_on_board and not team1_in_reserve:
        return 2, None

    # 3) Pas de victoire détectée
    return None, None

# ----------------------------
#  JOURNAL DES ACTIONS
# ----------------------------
def make_journal(action_type, actor_cell=None, target_cell=None, move_pos=None, ability_name=None, action_result=None):
    """
    Retourne une description textuelle en français pour une action.
    
    action_type: 'place' ou 'ability'
    actor_cell: dictionnaire du morpion agissant
    target_cell: dictionnaire du morpion cible
    move_pos: index de placement (0-based)
    ability_name: nom de la capacité utilisée
    action_result: résultat de l'action ('hit', 'miss', 'killed', etc.)
    """
    if action_type == 'place':
        if actor_cell and move_pos is not None:
            return f"{actor_cell['name']} a été placé en position {move_pos + 1}."
        else:
            return "Placement invalide."

    elif action_type == 'ability':
        if not actor_cell:
            return "Action impossible : acteur introuvable."
        
        actor_name = actor_cell.get('name', 'Un morpion')
        target_name = target_cell.get('name', 'la cible') if target_cell else 'la cible'

        if ability_name == 'attack':
            if action_result == 'hit':
                return f"{actor_name} attaque {target_name} et inflige des dégâts."
            elif action_result == 'killed':
                return f"{actor_name} attaque {target_name} et le détruit !"
            elif action_result == 'miss':
                return f"{actor_name} attaque {target_name} mais échoue."
            elif action_result == 'friendly_fire_blocked':
                return f"{actor_name} ne peut pas attaquer un allié !"
            elif action_result == 'target_not_adjacent':
                return f"{actor_name} ne peut attaquer {target_name} : cible non adjacente."
        
        elif ability_name == 'fireball':
            if action_result == 'hit':
                return f"{actor_name} lance une boule de feu sur {target_name}, dégâts infligés."
            elif action_result == 'killed':
                return f"{actor_name} lance une boule de feu et détruit {target_name} !"
            elif action_result == 'miss':
                return f"{actor_name} lance une boule de feu sur {target_name} mais échoue."
            elif action_result == 'no_mana':
                return f"{actor_name} n'a pas assez de mana pour lancer une boule de feu."
            elif action_result == 'friendly_fire_blocked':
                return f"{actor_name} ne peut pas lancer de boule de feu sur un allié !"
        
        elif ability_name == 'heal':
            if action_result == 'healed':
                return f"{actor_name} soigne {target_name} avec succès."
            elif action_result == 'miss':
                return f"{actor_name} tente de soigner {target_name} mais échoue."
            elif action_result == 'no_mana':
                return f"{actor_name} n'a pas assez de mana pour soigner."
            elif action_result == 'heal_enemy_blocked':
                return f"{actor_name} ne peut pas soigner un ennemi !"
        
        elif ability_name == 'armageddon':
            if action_result == 'destroyed':
                return f"{actor_name} lance Armageddon et détruit la case de {target_name} !"
            elif action_result == 'miss':
                return f"{actor_name} tente Armageddon sur {target_name} mais échoue."
            elif action_result == 'no_mana':
                return f"{actor_name} n'a pas assez de mana pour lancer Armageddon."
            elif action_result == 'kill_self_blocked':
                return f"{actor_name} ne peut pas détruire une case alliée !"

        elif action_result == 'unknown_ability':
            return f"{actor_name} tente une capacité inconnue."
        
        else:
            return f"{actor_name} effectue {ability_name} avec résultat : {action_result}."

    return "Action inconnue."

def clear_game_data():
    """Supprime les données de la partie en cours dans la session."""
    keys_to_clear = [
        'board_av', 'p1_turn', 'p2_turn', 'turn_count',
        'game_over', 'winning_cells', 'eq1_data', 'eq2_data',
        'eq1_name_col', 'eq2_name_col', 'grid_size', 'max_turn_av','current_game_id'
    ]
    for key in keys_to_clear:
        SESSION.pop(key, None)

def end_game_handler():
    # 1. Enregistrer & Quitter (Save and Exit)
    if POST and POST.get('end_submit', [None])[0] == '1':
        winner_team_num = REQUEST_VARS.get('winning_team')
        if winner_team_num is None:
            # Fallback in case of form submission without redirection after victory
            try:
                winner_team_num = int(POST.get('winning_equipe_id', [None])[0])
            except (TypeError, ValueError):
                winner_team_num = None
                
        game_id_to_update = SESSION.get('current_game_id')
        
        # Get max_turn_reached status
        max_turn_reached = POST.get('max_turn_reached', ['0'])[0] == '1' # Convert to boolean

        # Update winner in DB if a winner exists
        if winner_team_num in (1, 2) and game_id_to_update is not None:
            
            session_key = f'eq{winner_team_num}_name_col'
            team_col_data = SESSION.get(session_key, [[None, None, None]])
            winner_equipe_id = team_col_data[0][2]

            if winner_equipe_id is not None:
                # Calls update_partie_winner(connexion, prt_id, winner_id, max_turns_reached)
                update_partie_winner(
                    SESSION['CONNEXION'], 
                    game_id_to_update, 
                    winner_equipe_id, 
                    max_turn_reached
                )
                print(f"[DEBUG] Partie enregistrée. Winner DB ID: {winner_equipe_id}, Max Turns: {max_turn_reached}")
            else:
                print(f"[ERROR] Could not find DB Equipe ID for team {winner_team_num}. Save failed.")
                
        REQUEST_VARS['end_submit'] = True        
        clear_game_data()
        return

    # 2. Quitter (Abandon and Exit)
    if POST and POST.get('end_non_submit', [None])[0] == '1':
        game_id_to_delete = SESSION.get('current_game_id')
        
        # Delete the game and its configuration from the database
        if game_id_to_delete is not None:
            # Calls delete_partie(connexion, prt_id)
            delete_partie(SESSION['CONNEXION'], game_id_to_delete)
            
        REQUEST_VARS['end_non_submit'] = True
        clear_game_data()
        return

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

if 'grid_size' in SESSION:
    size = SESSION['grid_size']

if 'max_turn_av' not in SESSION:
    max_turn = None
else:
    max_turn = SESSION['max_turn_av']

if GET and 'game_id' in GET:
    game_id = int(GET['game_id'][0])
elif POST and 'game_id' in POST:
    game_id = int(POST['game_id'][0])

if game_id is not None:
    SESSION['current_game_id'] = game_id
    if 'eq1_data' not in SESSION or 'eq2_data' not in SESSION:
        game_data = get_instances_by_id(SESSION['CONNEXION'], 'partie', game_id)
        config_id = game_data[0][3]
        config_data = get_instances_by_id(SESSION['CONNEXION'], 'configuration', config_id)

        eq1_id, eq2_id = game_data[0][1], game_data[0][2]

        SESSION['eq1_data'] = create_equipe_list(get_equipe_details(SESSION['CONNEXION'], eq1_id))
        SESSION['eq2_data'] = create_equipe_list(get_equipe_details(SESSION['CONNEXION'], eq2_id))

        SESSION['eq1_name_col'] = get_equipe_name_color(SESSION['CONNEXION'], eq1_id)
        print(f"[DEBUG] Équipe 1: {SESSION['eq1_name_col']}")
        SESSION['eq2_name_col'] = get_equipe_name_color(SESSION['CONNEXION'], eq2_id)

        size = config_data[0][1]
        SESSION['grid_size'] = size

        max_turn = config_data[0][2]  # Nombre maximal de tours
        SESSION['max_turn_av'] = max_turn

# ----------------------------
#  INITIALISATION PLATEAU / SESSION
# ----------------------------
if size is None:
    size = 3
    SESSION['grid_size'] = size


SESSION.setdefault('board_av', [""] * (size * size))
board = SESSION['board_av']
REQUEST_VARS['board_av'] = board
SESSION['grid_size'] = size

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

        journal_text = make_journal(
            action_type='place',
            actor_cell=board[move],
            move_pos=move
        )
        REQUEST_VARS['journal_txt'] = journal_text

        winner, winning_cells = evaluate_victory(board, size, last_move=move, last_team=board[move]['team'])
        if winner is not None:
            SESSION['game_over'] = True
            SESSION['winning_cells'] = winning_cells
            REQUEST_VARS['game_over'] = True
            REQUEST_VARS['winning_cells'] = winning_cells
            REQUEST_VARS['winning_team'] = winner
            print(f"[DEBUG] Victoire détectée après placement pour l'équipe {winner} !")

        
        end_turn_if_needed("valid_place", max_turn)


# ----------------------------
#  TRAITEMENT SORTS / ATTAQUES
# ----------------------------
if POST and POST.get('action_type', [None])[0] == 'ability':
    actor_cell = None
    target_cell = None
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
        
    journal_text = make_journal(
        action_type='ability',
        actor_cell=actor_cell,
        target_cell=target_cell,
        ability_name=ability_name,      
        action_result=action_result
    )
    REQUEST_VARS['journal_txt'] = journal_text

    winner, winning_cells = None, None
    if a_idx is not None and isinstance(board[a_idx], dict):
        winner, winning_cells = evaluate_victory(board, size, last_move=a_idx, last_team=board[a_idx].get('team'))
    else:
        # Si l'acteur n'existe plus (par ex. armageddon l'a détruit), essayer la team de l'attaquant original
        try:
            actor_team_guess = int(POST.get('acting_team_guess', [None])[0]) if POST.get('acting_team_guess') else None
        except Exception:
            actor_team_guess = None
        if actor_team_guess is not None:
            winner, winning_cells = evaluate_victory(board, size, last_move=None, last_team=actor_team_guess)

    # Si pas de victoire par alignement, vérifier élimination
    if winner is None:
        elim_winner, _ = evaluate_victory(board, size)
        if elim_winner is not None:
            winner = elim_winner

    if winner is not None:
        SESSION['game_over'] = True
        SESSION['winning_cells'] = winning_cells
        REQUEST_VARS['game_over'] = True
        REQUEST_VARS['winning_cells'] = winning_cells
        REQUEST_VARS['winning_team'] = winner
        print(f"[DEBUG] Victoire détectée après action pour l'équipe {winner} !")
    
    end_turn_if_needed(action_result, max_turn)

    SESSION['board_av'] = board
    REQUEST_VARS['board_av'] = board
    REQUEST_VARS['last_action_result'] = action_result
    print(f"[DEBUG] Résultat de l'action: {action_result}")


# ----------------------------
#  TRAITEMENT FIN DE PARTIE
# ----------------------------

end_game_handler()
