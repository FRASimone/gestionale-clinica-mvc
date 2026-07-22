from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QComboBox, QMessageBox, QGroupBox,
                             QListWidget, QListWidgetItem)

from PyQt6.QtCore import Qt
from controllers.gestore_anagrafica import GestoreAnagrafica

class GestioneRuoliView(QWidget):
    #la dashboard passa l'id
    def __init__(self, id_utente_loggato: int):
        super().__init__()
        self.id_utente_loggato = id_utente_loggato
        self.gestore = GestoreAnagrafica() # Istanzia il controller
        self._build_ui()
        #dobbiamo avere la lista dei dipendenti per modificarne il ruolo
        #chiamata al metodo di sotto
        self.carica_dipendenti()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --- TABELLA DIPENDENTI ---
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(5)
        self.tabella.setHorizontalHeaderLabels(["ID", "Nome", "Cognome", "Email", "Ruolo Attuale"])
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabella.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabella.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabella)

        # --- PANNELLO MODIFICA RUOLO ---
        group_modifica = QGroupBox("Modifica Permessi e Ruolo")
        layout_modifica = QVBoxLayout()  # cambiato da QHBoxLayout a QVBoxLayout per fare spazio alla lista

        riga_ruolo = QHBoxLayout()
        riga_ruolo.addWidget(QLabel("Nuovo Ruolo:"))

        self.combo_nuovo_ruolo = QComboBox()
        self.combo_nuovo_ruolo.addItems(["Medico", "Segretario", "Amministratore"])
        #toggle fa spuntare la visione della lista delle specializzazioni
        self.combo_nuovo_ruolo.currentTextChanged.connect(self.toggle_specializzazioni)
        riga_ruolo.addWidget(self.combo_nuovo_ruolo)

        btn_salva = QPushButton("Aggiorna Ruolo")
        btn_salva.setStyleSheet("background-color: #E67E22; color: white; font-weight: bold;")
        #al click su aggiorna ruolo parte il metodo aggiorna
        btn_salva.clicked.connect(self.aggiorna_ruolo)
        riga_ruolo.addWidget(btn_salva)

        layout_modifica.addLayout(riga_ruolo)

        # --- SEZIONE: specializzazioni (visibile solo se nuovo ruolo = Medico) ---
        self.label_spec = QLabel("Specializzazioni da assegnare:")
        self.lista_spec = QListWidget()
        self.lista_spec.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        #popolamento iniziale della lista
        self._carica_specializzazioni()

        layout_modifica.addWidget(self.label_spec)
        layout_modifica.addWidget(self.lista_spec)

        # Nascoste di default finché non selezioni "Medico" nella combo
        self.label_spec.setVisible(False)
        self.lista_spec.setVisible(False)
        self.toggle_specializzazioni(self.combo_nuovo_ruolo.currentText())

        group_modifica.setLayout(layout_modifica)
        layout.addWidget(group_modifica)

    def carica_dipendenti(self):
        """Richiede al controller la lista dei dipendenti e popola la tabella."""
        #chiamata al gestore Anagrafica per ricavare i dipendenti
        risultati = self.gestore.get_tutti_dipendenti() 
        #prende tutti i dipendenti salvati nel sistema e li 
        #inserisce, riga per riga, in una tabella visiva.
        self.tabella.setRowCount(0)
        for riga, dipendente in enumerate(risultati):
            self.tabella.insertRow(riga)
            self.tabella.setItem(riga, 0, QTableWidgetItem(str(dipendente["id"])))
            self.tabella.setItem(riga, 1, QTableWidgetItem(dipendente["nome"]))
            self.tabella.setItem(riga, 2, QTableWidgetItem(dipendente["cognome"]))
            self.tabella.setItem(riga, 3, QTableWidgetItem(dipendente["email"]))
            self.tabella.setItem(riga, 4, QTableWidgetItem(dipendente["ruolo"]))

    def aggiorna_ruolo(self):
        #controllo che venga premuta una riga
        riga = self.tabella.currentRow()
        if riga < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un dipendente dalla tabella.")
            return
        #controllo che l'amministratore non si autodegradi
        id_dipendente = int(self.tabella.item(riga, 0).text())
        if id_dipendente == self.id_utente_loggato:
            QMessageBox.warning(self, "Operazione non consentita",
                         "Non puoi modificare il tuo stesso ruolo.")
            return
        nuovo_ruolo = self.combo_nuovo_ruolo.currentText()
        ruolo_attuale = self.tabella.item(riga, 4).text()
        #se i due ruoli sono uguali, non fare niente
        if nuovo_ruolo == ruolo_attuale:
            QMessageBox.information(self, "Info", "Il dipendente ha già questo ruolo.")
            return

        # CHIAMATA AL CONTROLLER ANAGRAFICA
        successo = self.gestore.modifica_ruolo(id_dipendente, nuovo_ruolo)

        #ritorno del metodo modifica
        if not successo:
            QMessageBox.critical(self, "Errore", "Impossibile aggiornare il ruolo.")
            return
        #se il nuovo ruolo e' Medico diverso dall'attuale si assegnano le specializzazioni
        if nuovo_ruolo == "Medico" and ruolo_attuale != "Medico":
            elementi_selezionati = self.lista_spec.selectedItems()
            for item in elementi_selezionati:
                id_spec = item.data(Qt.ItemDataRole.UserRole)
                self.gestore.assegnaSpecializzazione(id_dipendente, id_spec)

        QMessageBox.information(self, "Successo", f"Ruolo aggiornato in '{nuovo_ruolo}'.")
        self.carica_dipendenti()
    
    def _carica_specializzazioni(self):
        """Popola la lista specializzazioni prendendole dal DB."""
        #viene chiamato una sola volta all'inizio in build
        specializzazioni = self.gestore.getTutteSpecializzazioni()
        for spec in specializzazioni:
            item = QListWidgetItem(spec["nome"])
            item.setData(Qt.ItemDataRole.UserRole, spec["id"])
            self.lista_spec.addItem(item)

    def toggle_specializzazioni(self, nuovo_ruolo):
        """Mostra la selezione specializzazioni solo se stai promuovendo a Medico."""
        is_medico = (nuovo_ruolo == "Medico")
        self.label_spec.setVisible(is_medico)
        self.lista_spec.setVisible(is_medico)