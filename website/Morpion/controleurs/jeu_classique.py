from model.model import get_last_config

def win_check(board, player, move_pos, size):
    row = move_pos // size
    col = move_pos % size

    # Check row
    if all(board[row * size + c] == player for c in range(size)):
        return [row * size + c for c in range(size)]

    # Check column
    if all(board[r * size + col] == player for r in range(size)):
        return [r * size + col for r in range(size)]

    # Check main diagonal
    if row == col and all(board[i * size + i] == player for i in range(size)):
        return [i * size + i for i in range(size)]

    # Check anti-diagonal
    if row + col == size - 1 and all(board[i * size + (size - i - 1)] == player for i in range(size)):
        return [i * size + (size - i - 1) for i in range(size)]

    return None


def reset_session_board(turn_count_only=False):
    if turn_count_only:
        SESSION['turn_count'] = 0
    else:
        SESSION.pop('board', None)
        SESSION.pop('player', None)
        SESSION.pop('turn_count', None)


def game(config):
    if config is None:
        REQUEST_VARS['has_config'] = False
        return

    REQUEST_VARS['has_config'] = True
    size = config['grid_size']
    REQUEST_VARS['grid_size'] = size
    REQUEST_VARS['max_turns'] = config['max_turns']

    # Initialize session variables safely
    SESSION.setdefault('board', [""] * (size * size))
    SESSION.setdefault('player', "X")
    SESSION.setdefault('turn_count', 0)

    board = SESSION['board']
    player = SESSION['player']

    # Handle exit / configuration button
    if POST and 'exit' in POST:
        reset_session_board()
        REQUEST_VARS['to_config'] = '/config_classique'
        # Ensure board exists for template
        REQUEST_VARS['board'] = [""] * size
        return

    # Handle restart button
    if POST and 'restart' in POST:
        SESSION['board'] = [""] * (size * size)
        SESSION['player'] = "X"
        SESSION['turn_count'] = 0
        REQUEST_VARS['end_msg'] = "La partie a été recommencée."

    # Handle player move
    if POST and "move" in POST and SESSION["turn_count"] < config['max_turns']:
        ind = int(POST["move"][0])

        if board[ind] == "":
            board[ind] = player
            SESSION["turn_count"] += 1

            # Check for win
            win_cells = win_check(board, player, ind, size)
            if win_cells is not None:
                REQUEST_VARS['board'] = board
                REQUEST_VARS['end_msg'] = f"Fin de Jeu, {player} a Gagné!"
                REQUEST_VARS['win_cells'] = win_cells
                reset_session_board(turn_count_only=True)
                return True

            # Switch player
            player = "X" if player == "O" else "O"

    # Update session
    SESSION["board"] = board
    SESSION["player"] = player

    # Always provide board for template to avoid UndefinedError
    REQUEST_VARS['board'] = board
    REQUEST_VARS['count'] = SESSION["turn_count"]

    # Check draw
    if SESSION["turn_count"] >= config['max_turns']:
        REQUEST_VARS['end_msg'] = "Fin de Jeu, Égalité"
        return True


# MAIN
config = get_last_config(SESSION['CONNEXION'])
if game(config):
    REQUEST_VARS['end_game'] = True
