import urllib
from sqlalchemy import create_engine

def connect(connectionstring):
    params = urllib.parse.quote_plus(connectionstring)
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    return engine
