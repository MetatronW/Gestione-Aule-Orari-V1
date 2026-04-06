# Gestione Aule e Laboratori Università ABC

Sistema web per la gestione di aule e laboratori universitari che permette a docenti e amministratori di prenotare spazi, visualizzare orari e pubblicare comunicazioni.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![License](https://img.shields.io/badge/License-Educational-yellow.svg)

---


## Caratteristiche

- **Prenotazione Aule** - Prenota aule e laboratori per date e fasce orarie specifiche
- **Griglia Oraria** - Visualizza la disponibilità in tempo reale con griglia dinamica
- **Sistema Avvisi** - Pubblica e visualizza comunicazioni per tutta la comunità
- **Gestione Ruoli** - Accesso differenziato per pubblico, docenti e amministratori
- **Auto-Setup** - Database creato automaticamente al primo avvio
- **Responsive Design** - Interfaccia ottimizzata per desktop, tablet e mobile
- **Verifica Real-time** - Controllo disponibilità fasce orarie via AJAX

---


## Tecnologie

### Backend
- **Flask 2.3.3** - Framework web Python
- **MySQL** - Database relazionale
- **mysql-connector-python 8.1.0** - Driver MySQL

### Frontend
- **HTML5** - Struttura semantica
- **Tailwind CSS 2.2.19** - Framework CSS utility-first
- **Font Awesome 5.3.1** - Icone
- **JavaScript ES6** - Interazioni dinamiche e AJAX

---

## Installazione

### Prerequisiti

- Python 3.8 o superiore
- MySQL 8.0 o superiore
- pip (package manager Python)


### Primo Avvio

Al primo avvio vedrai:

```
============================================================
Prima inizializzazione - Setup database...
============================================================
Database inizializzato correttamente!
============================================================
Setup completato! Gli avvii successivi saranno istantanei.
============================================================
 * Running on http://127.0.0.1:5000
```

Apri il browser su: **http://localhost:5000**

---

## Utilizzo

### Credenziali di Prova

Il sistema crea automaticamente due utenti di test:

| Ruolo | Email | Password |
|-------|-------|----------|
| **Admin** | `admin@uni.com` | `admin123` |
| **Docente** | `mario.rossi@uni.com` | `docente123` |

### Registrazione Nuovi Docenti

1. Vai su `/register`
2. Compila il form con email `@uni.com`
3. Seleziona la materia di cui sei titolare
4. Accedi con le credenziali create

### Flusso di Lavoro

#### Come Docente:
1. **Login** - Accedi con le credenziali
2. **INSERISCI PRENOTAZIONE** - Seleziona materia, aula, date e fasce orarie
3. Il sistema verifica la disponibilità in tempo reale
4. **Salva** - Le prenotazioni appaiono nella griglia oraria

#### Come Admin:
- Tutte le funzionalità del docente
- **Elimina Avvisi** - Gestisci le comunicazioni pubblicate

#### Come Pubblico (senza login):
- **Visualizza Dashboard** - Consulta gli orari
- **Visualizza Avvisi** - Leggi le comunicazioni

---

 
## Database

### Schema

Il sistema utilizza **6 tabelle**:

1. **users** - Utenti (admin, docenti)
2. **aule** - Aule e laboratori
3. **materie** - Materie/insegnamenti
4. **docenti_materie** - Relazione docenti-materie (Many-to-Many)
5. **prenotazioni** - Prenotazioni aule
6. **avvisi** - Avvisi e comunicazioni



### Constraint Importanti

- **Email univoca** in `users`
- **UNIQUE (id_aula, data_prenotazione, fascia_oraria)** in `prenotazioni` - Impedisce doppie prenotazioni
- **Foreign Keys** con ON DELETE CASCADE dove appropriato

---

## Funzionalità

### 1. Autenticazione

#### Login
- Route: `/login`
- Metodi: GET, POST
- Accesso: Pubblico

#### Registrazione Docenti
- Route: `/register`
- Metodi: GET, POST
- Accesso: Pubblico
- Validazione: Email deve terminare con `@uni.com`

#### Logout
- Route: `/logout`
- Metodi: GET
- Accesso: Loggati

---

### 2. Dashboard Orari

#### Visualizzazione Griglia
- Route: `/dashboard` o `/`
- Metodi: GET
- Accesso: Tutti (pubblico + loggati)

**Caratteristiche:**
- Selezione data tramite calendario HTML5
- Griglia oraria 08:00 - 19:00
- Celle colorate per materie prenotate
- Riga evidenziata per pausa pranzo (13:00-14:00)
- Persistenza data in sessione

---

### 3. Prenotazione Aule

#### Form Prenotazione
- Route: `/inserisci-materie`
- Metodi: GET, POST
- Accesso: Docenti e Admin

**Funzionalità:**
- Selezione materia da database
- Selezione aula/laboratorio
- Date multiple (aggiunta dinamica)
- Fasce orarie multiple (select multiple)
- Verifica disponibilità real-time via AJAX

#### Endpoint AJAX Disponibilità
- Route: `/fasce-occupate`
- Metodi: GET
- Accesso: Loggati
- Parametri: `data`, `id_aula`
- Response: JSON con fasce occupate

**Logica Disponibilità:**
- Fascia OCCUPATA se prenotata in ALMENO UNA delle date selezionate (OR)
- Fascia DISPONIBILE solo se libera in TUTTE le date selezionate (AND)

---
 

## Matrice Permessi

| Funzionalità | Pubblico | Docente | Admin |
|--------------|----------|---------|-------|
| Visualizza Dashboard | SI | SI | SI |
| Visualizza Avvisi | SI | SI | SI |
| Inserisci Prenotazioni | NO | SI | SI |
| Inserisci Avvisi | NO | SI | SI |
| Elimina Avvisi | NO | NO | SI |

---
 
## Testing

### Test Manuale - Checklist Essenziale

#### Autenticazione
- [ ] Login funziona per entrambi gli utenti test
- [ ] Registrazione con email @uni.com funziona
- [ ] Logout funziona correttamente

#### Dashboard
- [ ] Griglia oraria visualizza correttamente
- [ ] Selezione data funziona
- [ ] Persistenza data in sessione

#### Prenotazioni
- [ ] Form accessibile solo per loggati
- [ ] Verifica disponibilità AJAX funziona
- [ ] Inserimento prenotazioni funziona
- [ ] Duplicati vengono bloccati

#### Avvisi
- [ ] Visualizzazione avvisi per tutti
- [ ] Inserimento avvisi per docenti/admin
- [ ] Eliminazione solo per admin

---
 

## Sicurezza

### Implementato
- Query parametrizzate (prevenzione SQL injection)
- Sessioni Flask server-side
- Validazione input email
- Controllo ruoli per route protette

### Da Implementare
- Password hashing (attualmente in chiaro)
- CSRF protection
- Rate limiting
- HTTPS in produzione
- Logging tentativi login falliti

 
---

## Licenza

Progetto educativo/didattico per la gestione di aule universitarie.  
Libero per uso accademico e apprendimento.

 
---

**Versione:** 2.0  
**Ultimo Aggiornamento:** Novembre 2025  
**Status:** Attivo / In Sviluppo