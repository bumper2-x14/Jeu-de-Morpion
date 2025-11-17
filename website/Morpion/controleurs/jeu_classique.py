from model.model import get_last_config 

config = get_last_config(SESSION['CONNEXION'])

if config is None:
    REQUEST_VARS['has_config'] = False
else:
    REQUEST_VARS['has_config'] = True
    REQUEST_VARS['grid_size'] = config['grid_size']    
    REQUEST_VARS['max_turns'] = config['max_turns']    