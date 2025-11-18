from model.model import get_instances

morpions = get_instances(SESSION['CONNEXION'], "morpion")
REQUEST_VARS['morpions'] = morpions if morpions else []


equipe_size = int(POST.get('eq_size', [0])[0]) if POST else 0
eq_col      = POST.get('eq_col', [''])[0] if POST else ''

REQUEST_VARS['equipe_size'] = equipe_size
REQUEST_VARS['eq_col']       = eq_col


selected_morpions = []

if POST:
    selected_ids = POST['selected_ids']
    if selected_ids:
        # garder uniquement les morpions qui ont un id sélectionné
        selected_morpions = [
            m for m in REQUEST_VARS['morpions']
            if str(m[0]) in selected_ids
        ]

# limiter à la taille maximale d'équipe
if equipe_size > 0:
    selected_morpions = selected_morpions[:equipe_size]

REQUEST_VARS['selected_morpions'] = selected_morpions

