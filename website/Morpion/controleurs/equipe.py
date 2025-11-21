from model.model import get_instances, delete_equipe

equipes = get_instances(SESSION['CONNEXION'], "equipe")
if (equipes):
        REQUEST_VARS['equipes'] = equipes


if GET and "id" in GET:
        print( GET['id'][0])
        if delete_equipe(SESSION['CONNEXION'], GET['id'][0]):
                REQUEST_VARS['delete'] = '/equipe'

