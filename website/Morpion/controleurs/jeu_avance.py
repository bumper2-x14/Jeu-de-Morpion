from model.model import get_instances_by_id, get_equipe_details, get_equipe_name_color


def create_equipe_list(equipe_data):
    team_list = []
    for entry in equipe_data:
        name, image, pv, att, mana, reu, id = entry
        team_list.append({
            'name': name,
            'image': image,
            'pv': pv,
            'att': att,
            'mana': mana,
            'reu': reu,
            'id': id,
        })

    return team_list


# ---------------------
#   TRAITEMENT PARTIE
# ---------------------
size = None
game_id = None # Initialize game_id to None

if GET and 'game_id' in GET:
    # Page load (GET)
    game_id = int(GET['game_id'][0][0])

# Check for game_id in POST (for form submission)
elif POST and 'game_id' in POST:
    # Form submission (POST)
    game_id = int(POST['game_id'][0])
    

if game_id is not None:
    REQUEST_VARS['current_game_id'] = game_id

    # ⭐️ FIX START: Only load initial decks if they are not already in the session
    if 'eq1_data' not in SESSION or 'eq2_data' not in SESSION:
        game_data = get_instances_by_id(SESSION['CONNEXION'], 'partie', game_id)
        config_id = game_data[0][3]
        config_data = get_instances_by_id(SESSION['CONNEXION'], 'configuration', config_id)

        eq1_id = game_data[0][1]
        eq2_id = game_data[0][2]

        eq1_data = get_equipe_details(SESSION['CONNEXION'], eq1_id)
        eq2_data = get_equipe_details(SESSION['CONNEXION'], eq2_id)

        # Conversion en format propre
        SESSION['eq1_data'] = create_equipe_list(eq1_data)
        SESSION['eq2_data'] = create_equipe_list(eq2_data)
        SESSION['eq1_name_col'] = get_equipe_name_color(SESSION['CONNEXION'], eq1_id)
        SESSION['eq2_name_col'] = get_equipe_name_color(SESSION['CONNEXION'], eq2_id)

        size = config_data[0][1]
        max_turn = config_data[0][2]
    
   
    if size is None:
        try:
             game_data = get_instances_by_id(SESSION['CONNEXION'], 'partie', game_id)
             config_id = game_data[0][3]
             config_data = get_instances_by_id(SESSION['CONNEXION'], 'configuration', config_id)
             size = config_data[0][1]
             max_turn = config_data[0][2]
        except:
             pass

    REQUEST_VARS['grid_size'] = size
    REQUEST_VARS['max_turn'] = max_turn


# -------------------------
#  INITIALISATION DU BOARD
# -------------------------

# Sécurisation : si size n’est pas définie
if size is None:
    size = REQUEST_VARS.get('grid_size', 3)  # valeur par défaut

SESSION.setdefault('board_av', [""] * (size * size))

board = SESSION['board_av']
REQUEST_VARS['board_av'] = board

REQUEST_VARS.get('end_game', False)


# -------------------------
#  TRAITEMENT DU COUP
# -------------------------

if POST and ('selected_id_eq1' in POST or 'selected_id_eq2' in POST) and 'move' in POST:
    move = int(POST['move'][0])

    # Récupération de la carte sélectionnée
    selected_card = None
    selected_team = None

    if 'selected_id_eq1' in POST:
        selected_id = int(POST['selected_id_eq1'][0])
        selected_team = 'eq1'
        # Reads from SESSION['eq1_data'], which is now persistent
        for inst in SESSION['eq1_data']:
            if inst['id'] == selected_id:
                selected_card = inst
                break

    elif 'selected_id_eq2' in POST:
        selected_id = int(POST['selected_id_eq2'][0])
        selected_team = 'eq2'
        # Reads from SESSION['eq2_data'], which is now persistent
        for inst in SESSION['eq2_data']:
            if inst['id'] == selected_id:
                selected_card = inst
                break

    if selected_card and board[move] == "":
        # On affiche le nom de la carte dans la grille
        board[move] = selected_card['name']

        # On retire la carte du deck (this line successfully updates the persistent SESSION data)
        if selected_team == 'eq1':
            SESSION['eq1_data'] = [c for c in SESSION['eq1_data'] if c['id'] != selected_id]
        else:
            SESSION['eq2_data'] = [c for c in SESSION['eq2_data'] if c['id'] != selected_id]

    # mise à jour du board
    SESSION['board_av'] = board
    REQUEST_VARS['board_av'] = board