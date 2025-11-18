from model.model import insert_to_config, get_last_config

# ======================================================
# SAUVGARDER
# ======================================================

if POST and 'bouton_sauvgarder' in POST:

    grid_size = int(POST['size'][0])
    max_turns = int(POST['max_turn'][0])

    success = insert_to_config(SESSION['CONNEXION'], grid_size, max_turns)

    REQUEST_VARS['size'] = str(grid_size)
    REQUEST_VARS['max_turn'] = str(max_turns)

    if success:
        REQUEST_VARS['message'] = "Configuration sauvegardée."


# ======================================================
# JOUER
# ======================================================

elif POST and 'bouton_jouer' in POST:

    if "size" not in POST or "max_turn" not in POST:
        REQUEST_VARS['error'] = "Veuillez remplir toutes les options."
    else:
        grid_size = int(POST['size'][0])
        max_turns = int(POST['max_turn'][0])

        insert_to_config(SESSION['CONNEXION'], grid_size, max_turns)

        REQUEST_VARS['go_play'] = "/jeu_classique"

        REQUEST_VARS['size'] = str(grid_size)
        REQUEST_VARS['max_turn'] = str(max_turns)