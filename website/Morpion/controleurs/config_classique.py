from model.model import insert_to_config

if POST and 'size' in POST:
    print(POST['size'])
    grid_size = POST['size'][0]
    if grid_size == '3':
        max_turns = 9
    else:
        max_turns = 16    

    success = insert_to_config(SESSION['CONNEXION'], grid_size, max_turns)
    if (success):
        REQUEST_VARS['link'] ="/jeu_classique" 