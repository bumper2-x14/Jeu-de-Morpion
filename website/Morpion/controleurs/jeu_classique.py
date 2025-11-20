from model.model import get_last_config 

config = get_last_config(SESSION['CONNEXION'])

if config is None:
    REQUEST_VARS['has_config'] = False
else:
    REQUEST_VARS['has_config'] = True
    size = config['grid_size']
    REQUEST_VARS['grid_size'] = size    
    REQUEST_VARS['max_turns'] = config['max_turns']


    if "board" not in SESSION:
        SESSION["board"] = [""] * (size * size)

    board = SESSION["board"]

    if POST and "move" in POST:
        ind = int(POST["move"][0])
        if board[ind] == "":
            board[ind] = "X"   

        SESSION["board"] = board


    REQUEST_VARS['board'] = board
    print(board)
