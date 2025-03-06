#!/usr/bin/env python3
import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, 
    QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel, QTextEdit, QHeaderView, QLineEdit, QInputDialog
)
from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtGui import QPixmap, QIcon
import getpass
import subprocess

if os.geteuid() != 0:
    print("Requires root access, requesting permission...")
    script_path = os.path.abspath(__file__)
    os.execvp("pkexec", ["pkexec", "env", f"DISPLAY={os.environ['DISPLAY']}", f"XAUTHORITY={os.environ['XAUTHORITY']}", "python3", script_path] + sys.argv[1:])
    sys.exit(0)

CONFIG_FILE = "yogzsp-program.json"
RUN_SCRIPT = "/usr/local/bin/run_wine.sh"


class programLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.programs = self.load_programs()
        self.update_program_list()
    
    def initUI(self):
        self.setWindowTitle("Yogzsp - Wine Launcher")
        self.setGeometry(200, 200, 900, 500)
        
        self.main_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        
        # program List Table
        self.program_table = QTableWidget()
        self.program_table.setColumnCount(4)
        self.program_table.setHorizontalHeaderLabels(["Icon", "Name", "File Name", "Path"])
        self.program_table.setColumnWidth(0, 50)
        self.program_table.setColumnWidth(1, 100)
        self.program_table.setColumnWidth(2, 200)
        self.program_table.setColumnWidth(3, 200)
        self.program_table.setColumnWidth(4, 300)
        self.program_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.program_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.program_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.program_table.cellDoubleClicked.connect(self.run_program)
        self.program_table.itemSelectionChanged.connect(self.update_buttons)
        
        # Buttons
        self.add_program_btn = QPushButton("Add Program")
        self.run_program_btn = QPushButton("Run Program")
        self.modify_program_btn = QPushButton("Modify Program")
        self.remove_program_btn = QPushButton("Remove Program")
        self.open_winecfg_btn = QPushButton("Open Winecfg")
        
        self.run_program_btn.setEnabled(False)
        self.modify_program_btn.setEnabled(False)
        self.remove_program_btn.setEnabled(False)
        
        self.button_layout.addWidget(self.add_program_btn)
        self.button_layout.addWidget(self.run_program_btn)
        self.button_layout.addWidget(self.modify_program_btn)
        self.button_layout.addWidget(self.remove_program_btn)
        self.button_layout.addWidget(self.open_winecfg_btn)
        
        # Log Output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("program log output will be displayed here...")
        
        self.main_layout.addWidget(self.program_table)
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addWidget(QLabel("Log:"))
        self.main_layout.addWidget(self.log_output)
        
        self.setLayout(self.main_layout)
        
        self.add_program_btn.clicked.connect(self.add_program)
        self.run_program_btn.clicked.connect(self.run_program)
        self.modify_program_btn.clicked.connect(self.modify_program_location)
        self.remove_program_btn.clicked.connect(self.remove_program)
        self.open_winecfg_btn.clicked.connect(self.open_winecfg)
    
    def log(self, message):
        self.log_output.append(message)

    def remove_program(self):
        selected = self.program_table.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            program_name = self.program_table.item(row, 1).text()  # Ambil program Name, bukan File Name
            
            if program_name in self.programs:
                del self.programs[program_name]  # Hapus program dari dictionary
                self.save_programs()
                self.update_program_list()
                self.update_buttons()
                self.log(f"Removed Program: {program_name}")
            else:
                QMessageBox.warning(self, "Error", f"program '{program_name}' tidak ditemukan dalam daftar!")

        else:
            QMessageBox.warning(self, "Error", "Please select a Program to remove!")
    
    def load_programs(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}
    
    def save_programs(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.programs, f, indent=4)
    
    def update_program_list(self):
        self.program_table.setRowCount(0)
        icon_size = 64  # Ukuran ikon yang diinginkan

        for idx, (program_name, program_data) in enumerate(self.programs.items(), start=1):
            row = self.program_table.rowCount()
            self.program_table.insertRow(row)

            # Membuat QWidget container untuk menempatkan QLabel
            widget_container = QWidget()
            layout = QVBoxLayout(widget_container)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Pusatkan isi widget

            # QLabel untuk ikon
            icon_label = QLabel()
            icon_label.setFixedSize(icon_size, icon_size)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            if os.path.exists(program_data.get("icon", "")):
                pixmap = QPixmap(program_data["icon"])
            else:
                pixmap = QPixmap("icon_placeholder.png")  # Placeholder jika tidak ada ikon

            # Skalakan gambar agar fit dalam ukuran ikon
            pixmap = pixmap.scaled(icon_size, icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)

            # Tambahkan QLabel ke dalam layout
            layout.addWidget(icon_label)
            widget_container.setLayout(layout)

            # Set widget container ke dalam tabel
            self.program_table.setCellWidget(row, 0, widget_container)

            # Atur tinggi baris agar sesuai dengan ukuran ikon
            self.program_table.setRowHeight(row, icon_size + 10)  # Tambah sedikit padding

            # Isi kolom lainnya
            self.program_table.setItem(row, 1, QTableWidgetItem(program_data["name"]))
            self.program_table.setItem(row, 2, QTableWidgetItem(os.path.basename(program_data["path"])))
            self.program_table.setItem(row, 3, QTableWidgetItem(program_data["path"]))

        # Atur ukuran kolom agar menyesuaikan konten
        self.program_table.resizeColumnsToContents()
        self.program_table.resizeRowsToContents()
        self.log("program list updated.")

    
    def update_buttons(self):
        selected = self.program_table.selectionModel().selectedRows()
        enabled = len(selected) > 0
        self.run_program_btn.setEnabled(enabled)
        self.modify_program_btn.setEnabled(enabled)
        self.remove_program_btn.setEnabled(enabled)
    
    def add_program(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Program Executable", "/home/", "Executable Files (*.exe)")
        if file_path:
            program_name, ok = QInputDialog.getText(self, "Program Name", "Enter Program Name:")
            if ok and program_name:
                icon_path, _ = QFileDialog.getOpenFileName(self, "Select Program Icon (Optional)", "", "Images (*.png *.jpg *.ico)")
                
                self.programs[program_name] = {"name": program_name, "path": file_path, "icon": icon_path if icon_path else ""}
                self.save_programs()
                self.update_program_list()
                self.log(f"Added Program: {program_name}")
    
    def run_program(self):
        selected = self.program_table.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            program_path = self.program_table.item(row, 3).text()
            
            if not os.path.exists(RUN_SCRIPT):
                QMessageBox.critical(self, "Error", "Missing run_wine.sh script!")
                return
            
            # Menjalankan script bash dengan path program sebagai argumen
            process = QProcess(self)
            process.start(RUN_SCRIPT, [program_path])
            
            self.log(f"Running: {program_path}")
        else:
            QMessageBox.warning(self, "Error", "Please select a Program to run!")

    
    def modify_program_location(self):
        selected = self.program_table.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            program_name = self.program_table.item(row, 2).text()
            file_path, _ = QFileDialog.getOpenFileName(self, "Select New Program Executable", "/home/", "Executable Files (*.exe)")
            if file_path:
                icon_path, _ = QFileDialog.getOpenFileName(self, "Select New Program Icon (Optional)", "", "Images (*.png *.jpg *.ico)")
                
                self.programs[program_name]["path"] = file_path
                if icon_path:
                    self.programs[program_name]["icon"] = icon_path
                
                self.save_programs()
                self.update_program_list()
                self.log(f"program modified : {program_name}")
        else:
            QMessageBox.warning(self, "Error", "Please select a Program to modify!")
    
    def open_winecfg(self):
        process = QProcess(self)
        process.start("winecfg")
        self.log("Opened Winecfg")

if __name__ == "__main__":

    app = QApplication(sys.argv)
    launcher = programLauncher()
    launcher.show()
    sys.exit(app.exec())
