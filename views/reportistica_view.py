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

        # --- SEZIONE SUPERIORE: Generazione Nuovi Report ---
        group_genera = QGroupBox("Generazione Nuovo Report")
        layout_genera = QHBoxLayout()

        self.combo_tipo_genera = QComboBox()
        self.combo_tipo_genera.addItems([
            "Pazienti", "Fatturato Globale", "Fatturato Prestazione", 
            "Fatturato Medico", "Statistico Prestazioni"
        ])
        layout_genera.addWidget(QLabel("Tipo:"))
        layout_genera.addWidget(self.combo_tipo_genera)

        self.spin_anno_genera = QSpinBox()
        self.spin_anno_genera.setRange(2020, 2030)
        self.spin_anno_genera.setValue(2026)
        layout_genera.addWidget(QLabel("Anno:"))
        layout_genera.addWidget(self.spin_anno_genera)

        self.combo_mese_genera = QComboBox()
        self.combo_mese_genera.addItem("Tutti i mesi (Annuale)", 0)
        for m in range(1, 13):
            self.combo_mese_genera.addItem(f"Mese {m}", m)
        layout_genera.addWidget(QLabel("Mese:"))
        layout_genera.addWidget(self.combo_mese_genera)

        btn_genera = QPushButton("Genera Report")
        btn_genera.setStyleSheet("background-color: #27AE60; color: white; font-weight: bold;")
        btn_genera.clicked.connect(self.genera_report)
        layout_genera.addWidget(btn_genera)
        
        group_genera.setLayout(layout_genera)
        layout.addWidget(group_genera)


        # --- SEZIONE CENTRALE: Ricerca e Filtri (RF25) ---
        group_ricerca = QGroupBox("Archivio Report Generati")
        layout_ricerca_main = QVBoxLayout()
        
        layout_filtri = QHBoxLayout()
        self.combo_tipo_filtro = QComboBox()
        self.combo_tipo_filtro.addItems([
            "Tutti", "Pazienti", "Fatturato Globale", 
            "Fatturato Prestazione", "Fatturato Medico", "Statistico Prestazioni"
        ])
        
        self.combo_anno_filtro = QComboBox()
        self.combo_anno_filtro.addItem("Tutti gli anni", 0) # Il testo che vede l'utente e il valore 0 che va al DB
        for y in range(2020, 2031): # Genera gli anni dal 2020 al 2030
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

        # --- SEZIONE INFERIORE: Azioni (Visualizza / Esporta) ---
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

    def genera_report(self):
        tipo = self.combo_tipo_genera.currentText()
        anno = self.spin_anno_genera.value()
        mese = self.combo_mese_genera.currentData() # Recupera l'intero nascosto (0-12)

        if tipo == "Pazienti":
            self.gestore.generaReportPazienti(anno, mese)
        elif tipo == "Fatturato Globale":
            self.gestore.generaReportFatturatoGlobale(anno, mese)
        elif tipo == "Fatturato Medico":
            self.gestore.generaReportFatturatoMedico(anno, mese)
        elif tipo == "Fatturato Prestazione":
            self.gestore.generaReportFatturatoPrestazione(anno, mese)
        elif tipo == "Statistico Prestazioni":
            self.gestore.generaReportStatisticoPrestazioni(anno, mese)

        QMessageBox.information(self, "Successo", f"Report '{tipo}' generato correttamente!")
        self.ricerca_report() # Aggiorna la tabella per mostrare il nuovo report

    def ricerca_report(self):
        tipo = self.combo_tipo_filtro.currentText()
        anno = self.combo_anno_filtro.currentData()
        mese = self.combo_mese_filtro.currentData()

        # Richiamo il metodo corretto del Controller (allineato all'UML)
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
            # Formattiamo il dizionario JSON in un testo leggibile
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