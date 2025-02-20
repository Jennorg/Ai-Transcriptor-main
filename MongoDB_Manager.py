from pymongo import MongoClient
from PySide6.QtWidgets import QInputDialog, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from datetime import datetime

# Configuración de MongoDB Atlas
MONGO_URI = "mongodb+srv://tendencias:1234@Transcripciones.2bftm.mongodb.net/?retryWrites=true&w=majority&appName=Transcripciones"
client = MongoClient(MONGO_URI)
db = client["Transcripcion"]
collection = db["Texto_de_Transcripcion"]

def save_transcription_to_mongodb(parent, transcription):
    """Guarda la transcripción en MongoDB con un nombre ingresado por el usuario."""
    
    # Crear un QDialog personalizado para aplicar estilos
    dialog = QDialog(parent)
    dialog.setWindowTitle("Guardar Texto")
    dialog.setStyleSheet("""
        QDialog {
            background-color: #f0f0f0;
            font-family: "Arial";
            font-size: 14px;
        }
        QLabel {
            color: #333;
        }
        QLineEdit {
            border: 1px solid #c0c0c0;
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
            color: #000;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #367c39;
        }
    """)

    layout = QVBoxLayout(dialog)
    label = QLabel("Ingrese el nombre del texto:")
    line_edit = QLineEdit()
    layout.addWidget(label)
    layout.addWidget(line_edit)

    button_layout = QHBoxLayout()
    ok_button = QPushButton("Aceptar")
    button_layout.addWidget(ok_button)
    layout.addLayout(button_layout)

    def accept():
        dialog.accept()

    ok_button.clicked.connect(accept)

    if dialog.exec() == QDialog.Accepted and line_edit.text().strip():
        name = line_edit.text().strip()
        try:
            document = {
                "nombre": name, 
                "texto": transcription,
                "fecha_subida": datetime.now() 
                } 
            collection.insert_one(document)
            print(f"Texto '{name}' guardado en MongoDB")
        except Exception as e:
            print(f"Error al guardar en MongoDB: {e}")
    else:
        print("Operación cancelada o nombre vacío.")
