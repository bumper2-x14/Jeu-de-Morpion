from model.model import get_instances, create_partie

team_list = get_instances(SESSION['CONNEXION'], 'equipe')

if team_list:
    REQUEST_VARS['team_list'] = team_list

size = max_turn = team1_id = team2_id = 0

if POST and 'bouton_sauvgarder' in POST:
    size = int(POST['size'][0])
    max_turn = int(POST['max_turn'][0])
    team1_id = int(POST['team_player_1'][0])
    team2_id = int(POST['team_player_2'][0])

    partie_id = create_partie(SESSION['CONNEXION'], size, max_turn, team1_id, team2_id)
    if partie_id != None:
        REQUEST_VARS['partie_id'] = partie_id
        REQUEST_VARS['av_play'] = '/jeu_avance'


