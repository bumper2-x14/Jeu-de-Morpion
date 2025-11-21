from model.model import insert_to_config

# ======================================================
# SAUVGARDER
# ======================================================

if POST and 'bouton_sauvgarder' in POST:

    grid_size = int(POST['size'][0])
    max_turns = int(POST['max_turn'][0])

    success = insert_to_config(SESSION['CONNEXION'], grid_size, max_turns)

    REQUEST_VARS['size'] = str(grid_size)
    REQUEST_VARS['max_turn'] = str(max_turns)
    REQUEST_VARS['play'] = "/jeu_classique"
