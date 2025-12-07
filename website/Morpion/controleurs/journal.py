from model.model import get_journal_by_prt_id


if GET and 'team_journal_id' in GET:
    team_journal_id = GET['team_journal_id'][0]
    journal_entries = get_journal_by_prt_id(SESSION['CONNEXION'], team_journal_id)
    REQUEST_VARS['journal_entries'] = journal_entries