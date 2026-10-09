# Gestionale Clinica Sportiva

Programma gestionale per uno studio medico sportivo. Permette di gestire
pazienti, personale, appuntamenti, cartelle cliniche e referti,
pagamenti e fatture, e di consultare report di attività e fatturato.
L'accesso è differenziato per ruolo: Medico, Segretario, Amministratore.

## Installazione e avvio

Servono Python 3 e la libreria PyQt6. Dalla cartella principale del progetto
(quella che contiene `main.py`):

```
python -m venv venv
```


Attivare l'ambiente virtuale:

- Windows: `venv\Scripts\activate`
- macOS / Linux: `source venv/bin/activate`


Poi installare la dipendenza e avviare:

```
pip install PyQt6
python main.py
```

Il programma va avviato dalla cartella principale. Al primo avvio crea
da solo il database (`database/clinica.db`) con alcuni dati di esempio:
non serve nessuna configurazione.

## Credenziali di accesso

Password per tutti gli utenti: `password123`

| Ruolo | Email |
|---|---|
| Amministratore | admin@clinica.it |
| Medico | medico@clinica.it |
| Segretario | segreteria@clinica.it |

Nella schermata di login va selezionato anche il ruolo corrispondente
all'email.

## Nota

L'invio di email (promemoria, fatture, recupero password) e
l'esportazione dei report sono simulati: il risultato compare nel
terminale da cui è stato avviato il programma.
