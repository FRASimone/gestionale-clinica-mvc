from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QSpinBox, QGroupBox)
from PyQt6.QtCore import Qt

from controllers.gestore_reportistica import GestoreReportistica

class ReportisticaView(QWidget):
    def __init__(self):
        super().__init__()
        self.gestore = GestoreReportistica()
        self._build_ui()
        self.ricerca_report() # Carica tutti i report all'avvio

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --- SEZIONE 1: Simulazione Attore TEMPO (Sostituisce la generazione manuale) ---
        group_tempo = QGroupBox("Simulazione Sistema (Trigger Automatico: Attore TEMPO)")
        # Lilla chiaro ad alto contrasto per un'ottima leggibilità sul grigio scuro
        group_tempo.setStyleSheet("QGroupBox { font-weight: bold; color: #D7BDE2; }") 
        layout_tempo = QHBoxLayout()

        lbl_info = QLabel("Simula lo scatto temporale per generare i 5 report in background:")
        layout_tempo.addWidget(lbl_info)

        self.spin_anno_sim = QSpinBox()
        self.spin_anno_sim.setRange(2020, 2030)
        self.spin_anno_sim.setValue(2026)
        
        self.combo_mese_sim = QComboBox()
        self.combo_mese_sim.addItem("Tutti i mesi (Annuale)", 0) # <-- OPZIONE ANNUALE 
        for m in range(1, 13):
            self.combo_mese_sim.addItem(f"Mese {m}", m)
            
        layout_tempo.addWidget(QLabel("Anno:"))
        layout_tempo.addWidget(self.spin_anno_sim)
        layout_tempo.addWidget(QLabel("Mese:"))
        layout_tempo.addWidget(self.combo_mese_sim)

        btn_simula = QPushButton("Esegui Batch Mese/Anno") # <-- TESTO BOTTONE AGGIORNATO
        btn_simula.setStyleSheet("background-color: #8E44AD; color: white; font-weight: bold;")
        #bottone che quando premuto chiama il metodo della view simula_scatto
        btn_simula.clicked.connect(self.simula_scatto_tempo)
        layout_tempo.addWidget(btn_simula)
        
        group_tempo.setLayout(layout_tempo)
        layout.addWidget(group_tempo)


        # --- SEZIONE 2: Archivio e Ricerca ---
        group_ricerca = QGroupBox("Archivio Report Generati")
        layout_ricerca_main = QVBoxLayout()
        
        layout_filtri = QHBoxLayout()
        self.combo_tipo_filtro = QComboBox()
        self.combo_tipo_filtro.addItems([
            "Tutti", "Pazienti", "Fatturato Globale", 
            "Fatturato Prestazione", "Fatturato Medico", "Statistico Prestazioni"
        ])
        
        self.combo_anno_filtro = QComboBox()
        self.combo_anno_filtro.addItem("Tutti gli anni", 0) 
        for y in range(2020, 2031):
            self.combo_anno_filtro.addItem(str(y), y)
        
        self.combo_mese_filtro = QComboBox()
        self.combo_mese_filtro.addItem("Tutti i mesi (Annuale)", 0)
        for m in range(1, 13):
            self.combo_mese_filtro.addItem(f"Mese {m}", m)

        layout_filtri.addWidget(QLabel("Filtra per Tipo:"))
        layout_filtri.addWidget(self.combo_tipo_filtro)
        layout_filtri.addWidget(QLabel("Anno:"))
        layout_filtri.addWidget(self.combo_anno_filtro)
        layout_filtri.addWidget(QLabel("Mese:"))
        layout_filtri.addWidget(self.combo_mese_filtro)
        
        btn_cerca = QPushButton("Applica Filtri")
        btn_cerca.clicked.connect(self.ricerca_report)
        layout_filtri.addWidget(btn_cerca)
        
        layout_ricerca_main.addLayout(layout_filtri)

        # Tabella Risultati
        self.tabella_report = QTableWidget()
        self.tabella_report.setColumnCount(4)
        self.tabella_report.setHorizontalHeaderLabels(["ID", "Tipo Report", "Anno", "Mese"])
        self.tabella_report.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabella_report.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout_ricerca_main.addWidget(self.tabella_report)
        
        group_ricerca.setLayout(layout_ricerca_main)
        layout.addWidget(group_ricerca)

        # --- SEZIONE 3: Azioni (Visualizza / Esporta) ---
        layout_azioni = QHBoxLayout()
        
        btn_visualizza = QPushButton("Visualizza Dettagli")
        btn_visualizza.clicked.connect(self.visualizza_dettagli)
        layout_azioni.addWidget(btn_visualizza)
        
        btn_esporta = QPushButton("Esporta in PDF")
        btn_esporta.setStyleSheet("background-color: #C0392B; color: white;")
        btn_esporta.clicked.connect(lambda: self.esporta_dati("PDF"))
        layout_azioni.addWidget(btn_esporta)

        btn_esporta_excel = QPushButton("Esporta in Excel")
        btn_esporta_excel.setStyleSheet("background-color: #2980B9; color: white;")
        btn_esporta_excel.clicked.connect(lambda: self.esporta_dati("Excel"))
        layout_azioni.addWidget(btn_esporta_excel)
        
        layout.addLayout(layout_azioni)

    # --- METODI LOGICI ---

    def simula_scatto_tempo(self):
        """Metodo che simula l'innesco automatico dei report."""
        anno = self.spin_anno_sim.value()
        mese = self.combo_mese_sim.currentData()

        successo = self.gestore.generaReportMensiliAutomatici(anno, mese)

        if successo:
            # Testo dinamico per il pop-up
            periodo = f"il mese {mese}/{anno}" if mese > 0 else f"l'intero anno {anno}"
            QMessageBox.information(self, "Batch Completato", f"Il sistema ha generato in background tutti e 5 i report per {periodo}.")
            self.ricerca_report() 
        else:
            QMessageBox.critical(self, "Errore", "Si è verificato un errore nell'elaborazione automatica.")
    
    def ricerca_report(self):
        tipo = self.combo_tipo_filtro.currentText()
        anno = self.combo_anno_filtro.currentData()
        mese = self.combo_mese_filtro.currentData()

        risultati = self.gestore.getListaReport(anno, mese, tipo)
        
        self.tabella_report.setRowCount(0)
        for riga, rep in enumerate(risultati):
            self.tabella_report.insertRow(riga)
            mese_str = str(rep['meseRiferimento']) if rep['meseRiferimento'] else "Annuale"
            
            self.tabella_report.setItem(riga, 0, QTableWidgetItem(str(rep['id'])))
            self.tabella_report.setItem(riga, 1, QTableWidgetItem(rep['tipoReport']))
            self.tabella_report.setItem(riga, 2, QTableWidgetItem(str(rep['annoRiferimento'])))
            self.tabella_report.setItem(riga, 3, QTableWidgetItem(mese_str))

    def get_id_selezionato(self):
        riga = self.tabella_report.currentRow()
        if riga < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un report dalla tabella.")
            return None
        return int(self.tabella_report.item(riga, 0).text())

    def visualizza_dettagli(self):
        id_report = self.get_id_selezionato()
        if not id_report: return
        
        report_data = self.gestore.visualizzaReport(id_report)
        if report_data:
            testo = f"--- DETTAGLI REPORT (ID {report_data['id']}) ---\n"
            testo += f"Tipo: {report_data['tipoReport']}\n"
            testo += f"Periodo: Anno {report_data['annoRiferimento']} "
            if report_data['meseRiferimento']: testo += f"- Mese {report_data['meseRiferimento']}"
            testo += "\n\n--- DATI AGGREGATI ---\n"
            
            for chiave, valore in report_data['datiAggregati'].items():
                if "Fatturato" in report_data['tipoReport']:
                    testo += f"{chiave}: {valore:.2f} €\n"
                else:
                    testo += f"{chiave}: {valore}\n"

            QMessageBox.information(self, "Dettagli Report", testo)

    def esporta_dati(self, formato: str):
        id_report = self.get_id_selezionato()
        if not id_report: return
        
        successo = self.gestore.esportaReport(id_report, formato)
        if successo:
            QMessageBox.information(self, "Esportazione Completata", f"Il report è stato esportato in {formato}.\n(Controlla il terminale per la simulazione)")