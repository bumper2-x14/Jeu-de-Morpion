from model.model import get_nb_instances, get_top_3_teams, get_min_max_duration_game

def format_duration(td):
    total_seconds = int(td.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}min {seconds}s"


nb_morpion = get_nb_instances(SESSION['CONNEXION'], "morpion")
nb_equipe = get_nb_instances(SESSION['CONNEXION'], "equipe")
nb_partie = get_nb_instances(SESSION['CONNEXION'], "partie")
top3_teams = get_top_3_teams(SESSION['CONNEXION'])
dur_teams = get_min_max_duration_game(SESSION['CONNEXION'])


if nb_morpion:
    REQUEST_VARS['nb_morpion'] = nb_morpion

if nb_equipe:
    REQUEST_VARS['nb_equipe'] = nb_equipe

if nb_partie:
    REQUEST_VARS['nb_partie'] = nb_partie

if top3_teams:
    REQUEST_VARS['top3_teams'] = top3_teams   

if dur_teams:
    row = dur_teams[0]
    print(row)

    min_dur = row[0]
    team1_min = row[1]
    team2_min = row[2]
    max_dur = row[3]
    team1_max = row[4]
    team2_max = row[5]

    REQUEST_VARS['min_dur'] = format_duration(min_dur)
    REQUEST_VARS['max_dur'] = format_duration(max_dur)

    REQUEST_VARS['min_team1'] = team1_min
    REQUEST_VARS['min_team2'] = team2_min

    REQUEST_VARS['max_team1'] = team1_max
    REQUEST_VARS['max_team2'] = team2_max
