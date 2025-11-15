from model.model import insert_to_config

if POST and 'size' in POST:
    grid_size = POST['size'][0]
    max_turn = 9

    success = insert_to_config(SESSION['CONNEXION'], grid_size, max_turn)