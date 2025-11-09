from mysql import connector
from init_db import init_database
import os

# Parametri di connessione 
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Modifica  se hai una password
    'database': 'gestione_aule_db'
}

# INIZIALIZZAZIONE AUTOMATICA (SOLO AL PRIMO AVVIO)
DB_MARKER = '.db_initialized'

if not os.path.exists(DB_MARKER):
    print(" Prima inizializzazione - Setup database...")
    try:
        success = init_database(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        
        if success:
            # Crea file marker per evitare re-inizializzazioni
            with open(DB_MARKER, 'w') as f:
                f.write('Database initialized successfully')
            print(" Setup completato! Gli avvii successivi saranno istantanei.")
        else:
            print(" Inizializzazione fallita. Tentativo di connessione...")
    except Exception as e:
        print(f" Errore durante l'inizializzazione: {e}")
        print(" Tentativo di connessione al database esistente...")

# CONNESSIONE AL DATABASE 
conn = connector.connect(
    host='localhost',
    user='root',
    #password='password',
    password='',
    database='gestione_aule_db'
)

# Messaggio di connessione (solo se non è la prima volta)
if os.path.exists(DB_MARKER):
    print(" Connessione al database stabilita!")