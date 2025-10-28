from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from connection import conn

app = Flask(__name__)
app.secret_key = 'chiave123'

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nome = request.form['nome']
        cognome = request.form['cognome']
        email = request.form['email']
        password = request.form['password']
        id_materia = request.form['id_materia']
        
        # Validazione email @uni.com
        if not email.endswith('@uni.com'):
            cursor.execute("SELECT id_materia, nome_materia FROM materie ORDER BY nome_materia")
            materie = cursor.fetchall()
            cursor.close()
            return render_template('register.html', errore="L'email deve essere del dominio @uni.com", materie=materie)
        
        # Verifica se email esiste
        query_mail = "SELECT email FROM users WHERE email = %s"
        cursor.execute(query_mail, (email,))
        email_esiste = cursor.fetchone()
        
        if email_esiste:
            cursor.execute("SELECT id_materia, nome_materia FROM materie ORDER BY nome_materia")
            materie = cursor.fetchall()
            cursor.close()
            return render_template('register.html', errore="Email già presente nel sistema", materie=materie)
        
        # Inserisci il nuovo utente , ruolo docente di default, admin con ruolo admin è già presente nel db
        query_user = "INSERT INTO users (nome, cognome, email, password, ruolo) VALUES (%s, %s, %s, %s, %s)"
        valori_user = (nome, cognome, email, password, 'docente')
        
        try:
            cursor.execute(query_user, valori_user)
            conn.commit()
            
            # Recupera l'ID dell'utente appena creato
            id_docente = cursor.lastrowid
            
            # Inserisci nella tabella pivot docenti_materie con ruolo 'titolare'
            query_pivot = "INSERT INTO docenti_materie (id_docente, id_materia, ruolo_docente) VALUES (%s, %s, %s)"
            valori_pivot = (id_docente, id_materia, 'titolare')
            cursor.execute(query_pivot, valori_pivot)
            conn.commit()
            
            cursor.close()
            return redirect(url_for('login'))
            
        except Exception as e:
            conn.rollback()
            cursor.execute("SELECT id_materia, nome_materia FROM materie ORDER BY nome_materia")
            materie = cursor.fetchall()
            cursor.close()
            return render_template('register.html', errore=f"Errore durante la registrazione: {str(e)}", materie=materie)
    
    # GET - Mostra il form con le materie
    cursor.execute("SELECT id_materia, nome_materia FROM materie ORDER BY nome_materia")
    materie = cursor.fetchall()
    cursor.close()
    return render_template('register.html', materie=materie)

#####################################################################

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'email' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = conn.cursor()
        query = "SELECT id_user, email, password, ruolo FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        utente = cursor.fetchone()
        cursor.close()
        
        if utente and utente[2] == password:
            session['id_user'] = utente[0]
            session['email'] = utente[1]
            session['ruolo'] = utente[3]
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', errore="Email o password non corretti")
    
    return render_template('login.html')

#####################################################################

@app.route('/dashboard')
def dashboard():
    email = session.get('email', None)
    
    # Recupera data da query string o da sessione
    data_selezionata = request.args.get('data', None)
    
    if data_selezionata:
        #SESSIONE: Se c'è una nuova data nel query string, salvala in sessione
        session['data_selezionata'] = data_selezionata
    else:
        # altrimenti usa quella salvata in sessione
        data_selezionata = session.get('data_selezionata', None)
    
    cursor = conn.cursor()
    
    # Recupera tutte le aule ordinate
    cursor.execute("SELECT id_aula, nome_aula, tipo_aula, capacita FROM aule ORDER BY nome_aula")
    aule = cursor.fetchall()
    
    # Fasce orarie standard 
    fasce_orarie = ['08-09', '09-10', '10-11', '11-12', '12-13', '13-14', '14-15', '15-16', '16-17', '17-18', '18-19']
    
    griglia_oraria = {}
    
    if data_selezionata:
        # Query per ottenere tutte le prenotazioni per la data selezionata
        query = """
            SELECT 
                p.fascia_oraria,
                p.id_aula,
                m.nome_materia,
                a.nome_aula,
                CONCAT(u.cognome, ' ', u.nome) AS docente
            FROM prenotazioni p
            INNER JOIN materie m ON p.id_materia = m.id_materia
            INNER JOIN aule a ON p.id_aula = a.id_aula
            INNER JOIN users u ON p.id_docente = u.id_user
            WHERE p.data_prenotazione = %s
            ORDER BY p.fascia_oraria, a.nome_aula
        """
        cursor.execute(query, (data_selezionata,))
        prenotazioni = cursor.fetchall()
        
        # Costruisci la griglia oraria: chiave = (fascia_oraria, id_aula), 
        #                               valore = dati prenotazione
        for pren in prenotazioni:
            fascia = pren[0]
            id_aula = pren[1]
            nome_materia = pren[2]
            nome_aula = pren[3]
            docente = pren[4]
            
            griglia_oraria[(fascia, id_aula)] = {
                'nome_materia': nome_materia,
                'nome_aula': nome_aula,
                'docente': docente
            }
    
    cursor.close()
    
    return render_template('dashboard.html', 
                         email=email,
                         data_selezionata=data_selezionata,
                         aule=aule,
                         fasce_orarie=fasce_orarie,
                         griglia_oraria=griglia_oraria)



#####################################################################
## new
@app.route('/fasce-occupate', methods=['GET'])
def get_fasce_occupate():
    """ restituisce le fasce orarie già prenotate per una data e aula."""
    if 'email' not in session:
        # Blocca l'accesso se l'utente non è loggato
        return jsonify({'errore': 'Non autorizzato'}), 403
        
    data_prenotazione = request.args.get('data')
    id_aula = request.args.get('id_aula')
    
    if not data_prenotazione or not id_aula:
        return jsonify({'errore': 'Parametri mancanti: data o id_aula'}), 400

    cursor = conn.cursor()
    # Query per trovare tutte le fasce orarie occupate
    query = "SELECT fascia_oraria FROM prenotazioni WHERE data_prenotazione = %s AND id_aula = %s"
    cursor.execute(query, (data_prenotazione, id_aula))
    
    # Estrae solo i valori della fascia oraria
    fasce_occupate = [row[0] for row in cursor.fetchall()]
    cursor.close()
    
    # Restituisce l'elenco in formato JSON
    return jsonify({'fasce_occupate': fasce_occupate})

#####################################################################


@app.route('/inserisci-materie', methods=['GET', 'POST'])
def inserisci_materie():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Recupera i dati dal form e filtra gli eventuali valori vuoti
        id_materia = request.form['id_materia']
        id_aula = request.form['id_aula']
        date_prenotazioni = [d for d in request.form.getlist('date_prenotazioni[]') if d]
        fasce_orarie_selezionate = [f for f in request.form.getlist('fascia_oraria[]') if f]
        id_docente = session['id_user']
        
        if not date_prenotazioni or not fasce_orarie_selezionate:
            # Reperimento materie,aule per il template in caso di errore
            cursor.execute("SELECT id_materia, nome_materia FROM materie ORDER BY nome_materia")
            materie = cursor.fetchall()
            cursor.execute("SELECT id_aula, nome_aula, tipo_aula, capacita FROM aule ORDER BY nome_aula")
            aule = cursor.fetchall()
            cursor.close()
            return render_template('inserisci_materie.html', 
                                 email=session['email'],
                                 materie=materie,
                                 aule=aule,
                                 errore=" Seleziona almeno una data e una fascia oraria.")

        try:
            # PREPARAZIONE: Crea la lista di tutte le combinazioni richieste (senza verifica)
            prenotazioni_da_inserire = []
            for data_prenotazione in date_prenotazioni:
                for fascia_oraria in fasce_orarie_selezionate:
                    # Formato: (data, fascia, id_aula, id_materia, id_docente)
                    prenotazioni_da_inserire.append((data_prenotazione, fascia_oraria, id_aula, id_materia, id_docente))

            #  INSERIMENTO 
            prenotazioni_inserite = 0
            if prenotazioni_da_inserire:
                query_insert_batch = """
                    INSERT INTO prenotazioni 
                    (data_prenotazione, fascia_oraria, id_aula, id_materia, id_docente) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                # Esegue l'inserimento multiplo
                cursor.executemany(query_insert_batch, prenotazioni_da_inserire)
                prenotazioni_inserite = cursor.rowcount # Conta le righe inserite
            
            conn.commit()
            
            # PREPARAZIONE MESSAGGISTICA DI RISPOSTA
            cursor.execute("SELECT id_materia, nome_materia FROM materie ORDER BY nome_materia")
            materie = cursor.fetchall()
            cursor.execute("SELECT id_aula, nome_aula, tipo_aula, capacita FROM aule ORDER BY nome_aula")
            aule = cursor.fetchall()
            cursor.close()
            
            if prenotazioni_inserite > 0:
                messaggio = f" {prenotazioni_inserite} prenotazione/i inserita/e con successo!"
                return render_template('inserisci_materie.html', 
                                     email=session['email'],
                                     materie=materie,
                                     aule=aule,
                                     messaggio_successo=messaggio)
            else:
                errore = " Nessuna prenotazione inserita (Verifica se la lista delle date/fasce era vuota o se c'è stato un problema di connessione)."
                return render_template('inserisci_materie.html', 
                                     email=session['email'],
                                     materie=materie,
                                     aule=aule,
                                     errore=errore)
            
        except Exception as e:
            # CATCH>>> per  errori SQL: duplicati, gestione conflitti
            conn.rollback()
            # Ricarica i dati per il template in caso di errore
            cursor.execute("SELECT id_materia, nome_materia FROM materie ORDER BY nome_materia")
            materie = cursor.fetchall()
            cursor.execute("SELECT id_aula, nome_aula, tipo_aula, capacita FROM aule ORDER BY nome_aula")
            aule = cursor.fetchall()
            cursor.close()
            return render_template('inserisci_materie.html', 
                                 email=session['email'],
                                 materie=materie,
                                 aule=aule,
                                 errore=f" Errore durante l'inserimento (potrebbe essere un duplicato): {str(e)}")
    
    # GET - Mostra il form
    cursor.execute("SELECT id_materia, nome_materia FROM materie ORDER BY nome_materia")
    materie = cursor.fetchall()
    cursor.execute("SELECT id_aula, nome_aula, tipo_aula, capacita FROM aule ORDER BY nome_aula")
    aule = cursor.fetchall()
    cursor.close()
    
    return render_template('inserisci_materie.html', 
                         email=session['email'],
                         materie=materie,
                         aule=aule)

#####################################################################

@app.route('/logout')
def logout():
    session.pop('id_user', None)
    session.pop('email', None)
    session.pop('ruolo', None)
    session.pop('data_selezionata', None)  # Rimuove anche la data salvata
    return redirect(url_for('dashboard'))


#####################################################################

@app.route('/avvisi')
def avvisi():
    email = session.get('email', None)
    ruolo = session.get('ruolo', None)
    
    cursor = conn.cursor()
    
    # Recupera tutti gli avvisi ordinati per data 
    query_avvisi = """
        SELECT 
            a.id_avviso,
            a.titolo,
            a.messaggio,
            CONCAT(u.nome, ' ', u.cognome) AS autore,
            u.ruolo,
            a.data_pubblicazione
        FROM avvisi a
        INNER JOIN users u ON a.id_autore = u.id_user
        ORDER BY a.data_pubblicazione DESC
    """
    cursor.execute(query_avvisi)
    avvisi_list = cursor.fetchall()
    cursor.close()
    
    return render_template('avvisi.html',
                         email=email,
                         ruolo=ruolo,
                         avvisi=avvisi_list)

@app.route('/inserisci-avvisi', methods=['GET', 'POST'])
def inserisci_avvisi():
    # Solo docenti e admin possono accedere
    if 'email' not in session:
        return redirect(url_for('login'))
    
    if session.get('ruolo') not in ['docente', 'admin']:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        titolo = request.form['titolo']
        messaggio = request.form['messaggio']
        id_autore = session['id_user']
        
        cursor = conn.cursor()
        
        try:
            query = "INSERT INTO avvisi (titolo, messaggio, id_autore) VALUES (%s, %s, %s)"
            cursor.execute(query, (titolo, messaggio, id_autore))
            conn.commit()
            cursor.close()
            
            return render_template('inserisci_avvisi.html',
                                 email=session['email'],
                                 messaggio_successo=" Avviso pubblicato con successo!")
        except Exception as e:
            conn.rollback()
            cursor.close()
            return render_template('inserisci_avvisi.html',
                                 email=session['email'],
                                 errore=f" Errore durante la pubblicazione: {str(e)}")
    
    # GET - Mostra il form
    return render_template('inserisci_avvisi.html', email=session['email'])

@app.route('/cancella-avviso/<int:id_avviso>', methods=['POST'])
def cancella_avviso(id_avviso):
    # Solo admin può cancellare
    if 'email' not in session or session.get('ruolo') != 'admin':
        return redirect(url_for('avvisi'))
    
    cursor = conn.cursor()
    
    try:
        query = "DELETE FROM avvisi WHERE id_avviso = %s"
        cursor.execute(query, (id_avviso,))
        conn.commit()
        cursor.close()
    except Exception as e:
        conn.rollback()
        cursor.close()
    
    return redirect(url_for('avvisi'))

#####################################################################

if __name__ == '__main__':
    app.run(debug=True)