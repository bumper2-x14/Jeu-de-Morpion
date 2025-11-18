from model.model import get_nb_instances


nb_morpion = get_nb_instances(SESSION['CONNEXION'], "morpion")
nb_equipe = get_nb_instances(SESSION['CONNEXION'], "equipe")
nb_partie = get_nb_instances(SESSION['CONNEXION'], "partie")

if (nb_morpion):
    REQUEST_VARS['nb_morpion'] = nb_morpion

if (nb_equipe):
    REQUEST_VARS['nb_equipe'] = nb_equipe

if (nb_partie):
    REQUEST_VARS['nb_partie'] = nb_partie