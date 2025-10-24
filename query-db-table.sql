
CREATE DATABASE IF NOT EXISTS gestione_aule_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE gestione_aule_db;

CREATE TABLE users (
    id_user INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    cognome VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    ruolo ENUM('admin', 'docente') NOT NULL,
    data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE aule (
    id_aula INT AUTO_INCREMENT PRIMARY KEY,
    nome_aula VARCHAR(50) NOT NULL UNIQUE,
    tipo_aula ENUM('aula', 'laboratorio') NOT NULL DEFAULT 'aula',
    capacita INT,
    data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE materie (
    id_materia INT AUTO_INCREMENT PRIMARY KEY,
    nome_materia VARCHAR(100) NOT NULL,
    data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE docenti_materie (
    id_docente INT NOT NULL,
    id_materia INT NOT NULL,
    ruolo_docente ENUM('titolare', 'assistente') DEFAULT 'titolare',
    data_assegnazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id_docente, id_materia),
    FOREIGN KEY (id_docente) REFERENCES users(id_user),
    FOREIGN KEY (id_materia) REFERENCES materie(id_materia)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE prenotazioni (
    id_prenotazione INT AUTO_INCREMENT PRIMARY KEY,
    data_prenotazione DATE NOT NULL,
    fascia_oraria VARCHAR(10) NOT NULL, -- Formato: "09-10", "10-11", "14-15"
    id_aula INT NOT NULL,
    id_materia INT NOT NULL,
    id_docente INT NOT NULL,
    data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_aula) REFERENCES aule(id_aula),
    FOREIGN KEY (id_materia) REFERENCES materie(id_materia),
    FOREIGN KEY (id_docente) REFERENCES users(id_user),
    
    UNIQUE (id_aula, data_prenotazione, fascia_oraria) -- Impedisce doppie prenotazioni: stessa aula, stessa data, stessa fascia
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE avvisi (
    id_avviso INT AUTO_INCREMENT PRIMARY KEY,
    titolo VARCHAR(200) NOT NULL,
    messaggio TEXT NOT NULL,
    id_autore INT NOT NULL,
    data_pubblicazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_autore) REFERENCES users(id_user) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


 
 