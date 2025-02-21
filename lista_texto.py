import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QFileDialog, QTextEdit, QHBoxLayout, QDialog, QMainWindow)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt
from pymongo import MongoClient
from export_utils import save_as_pdf, save_as_txt
import os
from datetime import datetime
from chat import obtener_respuesta

# Direcciones de iconos
icon_path_pdf = os.path.join(os.path.dirname(__file__), "images", "pdf_icon.png")
icon_path_txt = os.path.join(os.path.dirname(__file__), "images", "txt_icon.png")
icon_path_ia = os.path.join(os.path.dirname(__file__), "images", "ia_icon.png")

class DetailWindow(QMainWindow):
    def __init__(self, nombre, texto, fecha, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalle del Texto")
        self.setGeometry(200, 200, 500, 350)

        # Layout principal
        layout = QVBoxLayout()

        # Etiquetas con los detalles del documento
        self.name_label = QLabel(f"Nombre: {nombre}", self)
        self.name_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
            padding-bottom: 5px;
        """)

        self.date_label = QLabel(f"Fecha: {fecha}", self)
        self.date_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
            padding-bottom: 10px;
        """)

        # Etiqueta adicional para algún mensaje informativo
        self.info_label = QLabel("Información adicional o descripción:", self)
        self.info_label.setStyleSheet("""
            font-size: 14px;
            color: #444;
            font-weight: normal;
            padding-bottom: 10px;
        """)

        # Área de texto que contiene el texto detallado
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)
        self.text_display.setText(texto)

        # Botones de acción
        button_layout = QHBoxLayout()

        self.pdf_button = QPushButton("Exportar PDF", self)
        self.pdf_button.setIcon(QIcon(icon_path_pdf))
        self.pdf_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white;
                border: 1px solid #4CAF50;
                padding: 8px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        self.pdf_button.clicked.connect(lambda: self.export_pdf(nombre, texto))
        button_layout.addWidget(self.pdf_button)

        self.txt_button = QPushButton("Exportar TXT", self)
        self.txt_button.setIcon(QIcon(icon_path_txt))
        self.txt_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white;
                border: 1px solid #2196F3;
                padding: 8px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.txt_button.clicked.connect(lambda: self.export_txt(nombre, texto))
        button_layout.addWidget(self.txt_button)

        self.ia_button = QPushButton("Generar Resumen IA", self)
        self.ia_button.setIcon(QIcon(icon_path_ia))
        self.ia_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800; 
                color: white;
                border: 1px solid #FF9800;
                padding: 8px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FB8C00;
            }
        """)
        self.ia_button.clicked.connect(lambda: self.ventana_ia(texto))
        button_layout.addWidget(self.ia_button)

        # Ajustar el tamaño de los botones proporcionalmente
        button_layout.setStretch(0, 1)
        button_layout.setStretch(1, 1)
        button_layout.setStretch(2, 1)

        layout.addWidget(self.name_label)
        layout.addWidget(self.date_label)
        layout.addWidget(self.info_label)  # Etiqueta adicional
        layout.addWidget(self.text_display)
        layout.addLayout(button_layout)
        
        # Ventana con QMainWindow
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Estilo de la ventana
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
                border: 1px solid #ccc;  # Bordes tradicionales
            }
        """)

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

        # Obtener el resumen de la IA
        summary = obtener_respuesta(f"Dame una explicación sobre: {texto}")

        # Crear ventana para el resumen generado
        self.new_window = QWidget()
        self.new_window.setWindowTitle("Resumen Generado por IA")
        self.new_window.setGeometry(200, 200, 500, 350)

        # Layout principal (similar a DetailWindow)
        layout = QVBoxLayout()

        # Etiqueta de información
        self.info_label = QLabel("Resumen generado por la IA:", self.new_window)
        self.info_label.setStyleSheet("""
            font-size: 14px;
            color: #444;
            font-weight: normal;
            padding-bottom: 10px;
        """)
        
        # Área de texto para mostrar el resumen generado
        self.text_display = QTextEdit(self.new_window)
        self.text_display.setReadOnly(True)
        self.text_display.setText(summary)
        self.text_display.setStyleSheet("""
            background-color: #fafafa;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
            padding: 10px;
        """)

        # Botones de acción (Estilo similar a los botones de exportación)
        button_layout = QHBoxLayout()

        # Botón de Cerrar
        close_button = QPushButton("Cerrar", self.new_window)
        close_button.clicked.connect(self.new_window.close)
        button_layout.addWidget(close_button)

        # Ajustar el tamaño de los botones proporcionalmente
        button_layout.setStretch(0, 1)

        # Agregar elementos al layout
        layout.addWidget(self.info_label)
        layout.addWidget(self.text_display)
        layout.addLayout(button_layout)

        # Configurar el layout de la ventana
        self.new_window.setLayout(layout)
        self.new_window.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;  # Fondo suave
                font-family: Arial, sans-serif;
            }
        """)
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
        self.page_size = 14

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
        self.search_button.clicked.connect(self.search_data)
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

        # Aplicar estilos
        self.apply_styles()

        # Cargar datos iniciales
        self.load_data()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                padding: 5px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #4CAF50; 
                color: white;
                border: none;
                padding: 12px 24px; 
                border-radius: 10px; 
                font-size: 16px; 
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #1e7e34; 
            }
            QPushButton:pressed {
                background-color: #155724;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #e0e0e0;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
                padding: 5px;
            }
        """)

    def search_data(self):
        """Realiza una búsqueda y restablece la página a 0"""
        self.page = 0
        self.load_data()

    def load_data(self):
        """Carga y muestra los datos paginados desde MongoDB"""
        query = {"nombre": {"$regex": self.search_input.text(), "$options": "i"}} if self.search_input.text() else {}
        cursor = self.collection.find(query).sort("fecha_subida", -1).skip(self.page * self.page_size).limit(self.page_size)
        
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
        fecha_raw = doc.get("fecha_subida", None)  # Asegúrate de obtener 'fecha_subida'
        
        # Verifica si la fecha es un objeto datetime y formatea la fecha correctamente
        if isinstance(fecha_raw, datetime):
            fecha = fecha_raw.strftime("%d/%m/%Y %H:%M")  # Formato: Día/Mes/Año Hora:Minuto
        else:
            fecha = "Fecha inválida"

        self.detail_window = DetailWindow(nombre, texto, fecha, self)
        self.detail_window.show()

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MongoDBViewer()
    viewer.show()
    sys.exit(app.exec())