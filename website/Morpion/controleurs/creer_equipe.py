from model.model import get_instances, create_equipe

morpions = get_instances(SESSION['CONNEXION'], "morpion")
if morpions:
    REQUEST_VARS['morpions'] = morpions

# -------- Parameters --------
equipe_size = 0
eq_col = ''
eq_name = ''

if POST:
    if 'eq_size' in POST:
        equipe_size = int(POST['eq_size'][0])
    if 'eq_col' in POST:
        eq_col = POST['eq_col'][0]
    if 'eq_name' in POST:
        eq_name = POST['eq_name'][0]

REQUEST_VARS['equipe_size'] = equipe_size
REQUEST_VARS['eq_col'] = eq_col
REQUEST_VARS['eq_name'] = eq_name

# -------- Selected morpions --------
selected_morpions = []
selected_ids = []

if POST and "selected_ids" in POST:
    selected_ids = POST['selected_ids']
    selected_morpions = [m for m in morpions if str(m[0]) in selected_ids]

if equipe_size > 0:
    selected_ids = selected_ids[:equipe_size]

REQUEST_VARS['selected_morpions'] = selected_morpions
final_ids = [str(m[0]) for m in selected_morpions]

# -------- FINALISER CLICKED --------
if POST and "finaliser" in POST:
    
    print("FINAL ID" ,final_ids)

    if len(selected_ids) != equipe_size:
        REQUEST_VARS['msg'] = "Vous devez sélectionner exactement {} morpions.".format(equipe_size)
    else:
        create_equipe(
            SESSION['CONNEXION'],
            eq_name,
            eq_col,
            selected_ids,
            equipe_size
        )
        REQUEST_VARS['msg'] = "Équipe créée avec succès !"
