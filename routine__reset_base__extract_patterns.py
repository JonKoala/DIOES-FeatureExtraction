import inout
from db import Dbinterface
from db.models import Publicacao, Predicao, Patterns

import re
from decimal import Decimal


##
# Utils

def to_decimal(match):
    return Decimal(''.join(match.group(0).split()).replace('$', '').replace('.', '').replace(',', '.'))

re_money = re.compile('\$\s*[1-9][\d\.]*(,\d{2})?')


##
# Get resources

appconfig = inout.read_yaml('./appconfig')
dbi = Dbinterface(appconfig['db']['connectionstring'])

# get unextracted publicacoes
with dbi.opensession() as session:
    to_extract = session.query(Predicao).join(Predicao.publicacao)
    data = [(predicao.publicacao.id, predicao.publicacao.corpo) for predicao in to_extract]


##
# Find Regex patterns (for now, just biggest value)

results = []
for index, publicacao in enumerate(data):

    #get values from publicacao
    iter_matches = re.finditer(re_money, publicacao[1])
    values = [to_decimal(match) for match in iter_matches]

    # get biggest value
    values.sort(reverse=True)
    biggest = next(iter(values), None)

    results += [(publicacao[0], biggest)]


##
# Persist patterns on database

with dbi.opensession() as session:

    # clean old entries
    session.query(Patterns).delete()
    session.flush()

    # insert new patterns
    for result in results:
        patterns = Patterns(publicacao_id=result[0], valor=result[1])
        session.add(patterns)

    session.commit()
