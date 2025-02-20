import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,QFileDialog, QTextEdit, QHBoxLayout)
from PySide6.QtGui import QIcon
from pymongo import MongoClient
from export_utils import save_as_pdf, save_as_txt
import os
from datetime import datetime
from chat import obtener_respuesta

#Direcciones de iconos

icon_path_pdf = os.path.join(os.path.dirname(__file__), "images", "pdf_icon.png")
icon_path_txt = os.path.join(os.path.dirname(__file__), "images", "txt_icon.png")
icon_path_ia = os.path.join(os.path.dirname(__file__), "images", "ia_icon.png")

class DetailWindow(QWidget):
# Ventana emergente para mostrar detalles de un documento
    def __init__(self, nombre, texto, fecha):
        super().__init__()
        self.setWindowTitle("Detalle del Texto")
        self.setGeometry(200, 200, 500, 350)
        
        layout = QVBoxLayout()
        
        self.name_label = QLabel(f"Nombre: {nombre}", self)
        self.date_label = QLabel(f"Fecha: {fecha}", self)
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)
        self.text_display.setText(texto)

        # Botones con iconos
        button_layout = QHBoxLayout()

        self.pdf_button = QPushButton()
        self.pdf_button.setIcon(QIcon(icon_path_pdf))
        self.pdf_button.clicked.connect(lambda: self.export_pdf(nombre, texto))
        button_layout.addWidget(self.pdf_button)

        self.txt_button = QPushButton()
        self.txt_button.setIcon(QIcon(icon_path_txt))
        self.txt_button.clicked.connect(lambda: self.export_txt(nombre, texto))
        button_layout.addWidget(self.txt_button)

        self.ia_button = QPushButton()
        self.ia_button.setIcon(QIcon(icon_path_ia))
        self.ia_button.clicked.connect(lambda: self.ventana_ia(texto))
        button_layout.addWidget(self.ia_button)

        layout.addWidget(self.name_label)
        layout.addWidget(self.date_label)
        layout.addWidget(self.text_display)
        layout.addLayout(button_layout)  # Agregar los botones al layout
        self.setLayout(layout)

    def export_pdf(self, nombre, texto):
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar como PDF", f"{nombre}.pdf", "PDF Files (*.pdf)")
        if file_path:
            save_as_pdf(file_path, nombre, texto)

    def export_txt(self, nombre, texto):
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar como TXT", f"{nombre}.txt", "Text Files (*.txt)")
        if file_path:
            save_as_txt(file_path, texto)

    def ventana_ia(self, texto):
        if not isinstance(texto, str):  
            texto = str(texto)  

        texto = texto.strip()

        summary = obtener_respuesta(f"Dame una explicación sobre: {texto}")

        self.new_window = QWidget()
        self.new_window.setWindowTitle("Resumen Generado por IA")
        self.new_window.setGeometry(250, 250, 400, 300)
        layout = QVBoxLayout()
        summary_label = QLabel(summary, self.new_window)
        layout.addWidget(summary_label)
        self.new_window.setLayout(layout)
        self.new_window.show()



class MongoDBViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MongoDB Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Conexión a MongoDB
        self.client = MongoClient("mongodb+srv://tendencias:1234@transcripciones.2bftm.mongodb.net/?retryWrites=true&w=majority&appName=Transcripciones")
        self.db = self.client["Transcripcion"]
        self.collection = self.db["Texto_de_Transcripcion"]

        # Variables de paginación
        self.page = 0
        self.page_size = 8

        # Widgets
        self.layout = QVBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Buscar por nombre...")
        self.search_button = QPushButton("Buscar", self)
        self.result_list = QListWidget(self)
        
        # Botones de paginación
        self.prev_button = QPushButton("Anterior", self)
        self.next_button = QPushButton("Siguiente", self)

        # Conectar señales
        self.search_button.clicked.connect(self.load_data)
        self.next_button.clicked.connect(self.next_page)
        self.prev_button.clicked.connect(self.prev_page)
        self.result_list.itemClicked.connect(self.show_details)

        # Agregar widgets al layout
        self.layout.addWidget(QLabel("Buscar en MongoDB:"))
        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.search_button)
        self.layout.addWidget(self.result_list)
        
        # Agregar los botones de paginación en un layout horizontal
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        self.layout.addLayout(nav_layout)
        
        self.setLayout(self.layout)

        # Cargar datos iniciales
        self.load_data()

    def load_data(self):
        """Carga y muestra los datos paginados desde MongoDB"""
        query = {"nombre": {"$regex": self.search_input.text(), "$options": "i"}} if self.search_input.text() else {}
        cursor = self.collection.find(query).skip(self.page * self.page_size).limit(self.page_size)
        
        self.result_list.clear()
        self.results = list(cursor)

        for doc in self.results:
            nombre = doc.get("nombre", "Sin nombre")
            fecha_raw = doc.get("fecha_subida", None)

            # Verificar si fecha_subida existe y formatearla
            if isinstance(fecha_raw, datetime):
                fecha = fecha_raw.strftime("%d/%m/%Y %H:%M")
            else:
                fecha = "Fecha inválida"

            item_text = f"{fecha} - {nombre}"
            item = QListWidgetItem(item_text)
            item.setData(3, doc)  # Guardamos el documento en los datos del item
            self.result_list.addItem(item)

        # Control de botones de paginación
        self.prev_button.setEnabled(self.page > 0)
        self.next_button.setEnabled(len(self.results) == self.page_size)

    def next_page(self):
        """Muestra la siguiente página de resultados"""
        self.page += 1
        self.load_data()

    def prev_page(self):
        """Muestra la página anterior de resultados"""
        if self.page > 0:
            self.page -= 1
            self.load_data()

    def show_details(self, item):
        """Muestra una ventana emergente con el nombre, texto y la fecha"""
        doc = item.data(3)
        nombre = doc.get("nombre", "Sin nombre")
        texto = doc.get("texto", "Sin texto")
        fecha = doc.get("fecha", "Sin fecha")
        
        self.detail_window = DetailWindow(nombre, texto, fecha)
        self.detail_window.show()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MongoDBViewer()
    viewer.show()
    sys.exit(app.exec())
