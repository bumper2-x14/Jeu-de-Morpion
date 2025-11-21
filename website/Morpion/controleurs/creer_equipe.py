from model.model import get_instances, create_equipe, get_column

morpions = get_instances(SESSION['CONNEXION'], "morpion")
if morpions:
    REQUEST_VARS['morpions'] = morpions

used_cols = get_column(SESSION['CONNEXION'], "equipe", "color")
used_name = get_column(SESSION['CONNEXION'], "equipe", "name")
print(used_cols)
print(used_name)

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

    errors = {}

    if eq_col.lower() in {c.lower() for c in used_cols}:
        errors['eq_col'] = "Cette couleur est déjà utilisée."

    if eq_name.lower() in {n.lower() for n in used_name}:
        errors['eq_name'] = "Ce nom est déjà utilisé."


    if not errors:
        REQUEST_VARS['equipe_size'] = equipe_size
        REQUEST_VARS['eq_col'] = eq_col
        REQUEST_VARS['eq_name'] = eq_name
        # -------- Selected morpions --------
        selected_morpions = []
        selected_ids = []
        REQUEST_VARS.setdefault('equipe_size', 0)
        REQUEST_VARS.setdefault('selected_morpions', [])

        if POST and "selected_ids" in POST:
            selected_ids = POST['selected_ids']
            selected_morpions = [m for m in morpions if str(m[0]) in selected_ids]

        if equipe_size > 0:
            selected_ids = selected_ids[:equipe_size]

        REQUEST_VARS['selected_morpions'] = selected_morpions
        final_ids = [str(m[0]) for m in selected_morpions]

        # -------- FINALISER CLICKED --------
        if POST and "finaliser" in POST:
            
            if len(selected_ids) != equipe_size:
                REQUEST_VARS['msg'] = "Vous devez sélectionner exactement {} morpions.".format(equipe_size)
            else:
                create_equipe(SESSION['CONNEXION'], eq_name, eq_col, selected_ids, equipe_size)  
                REQUEST_VARS['msg_sc'] = "Équipe créée avec succès !"        

    else:
        print(errors)
        REQUEST_VARS['err_choice'] = errors

