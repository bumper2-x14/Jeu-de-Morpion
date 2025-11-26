from model.model import get_instances_by_id, get_equipe_details

def create_equipe_dict(equipe_data):
    team = {}

    for entry in equipe_data:
        name, image, pv, att, mana, reu = entry
        
        team[name] = {
            'image': image,
            'pv': pv,
            'att': att,
            'mana': mana,
            'reu': reu
        }
    
    return team


if GET and 'game_id' in GET:
    game_id = int(GET['game_id'][0][0])
    game_data = get_instances_by_id(SESSION['CONNEXION'], 'partie', game_id)
    config_id = game_data[0][3]
    config_data = get_instances_by_id(SESSION['CONNEXION'], 'configuration', config_id)

    eq1_id = game_data[0][1]
    eq2_id = game_data[0][2]
    eq1_data = get_equipe_details(SESSION['CONNEXION'], eq1_id)
    eq2_data = get_equipe_details(SESSION['CONNEXION'], eq2_id)

    eq1_data = create_equipe_dict(eq1_data)
    eq2_data = create_equipe_dict(eq2_data)

    SESSION['eq1_data'] = eq1_data
    SESSION['eq2_data'] = eq2_data
    
    size = config_data[0][1]
    mx_turn = config_data[0][2]
    REQUEST_VARS['grid_size'] = size
    REQUEST_VARS['max_turn'] = mx_turn


SESSION.setdefault('board_av', [""] * (size * size))
REQUEST_VARS.get('end_game', False)  

board = SESSION['board_av']
REQUEST_VARS['board_av'] = board

