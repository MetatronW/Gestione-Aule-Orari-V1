from mysql import connector

conn = connector.connect(
    host='localhost',
    user='root',
    #password='password',
    password='',
    database='gestione_aule_db'
)
