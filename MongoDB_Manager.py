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
        QPushButton#cancel {
            background-color: #f44336;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 14px;
        }
        QPushButton#cancel:hover {
            background-color: #e53935;
        }
        QPushButton#cancel:pressed {
            background-color: #d32f2f;
        }
    """)

    layout = QVBoxLayout(dialog)
    label = QLabel("Ingrese el nombre del texto:")
    line_edit = QLineEdit()
    layout.addWidget(label)
    layout.addWidget(line_edit)

    button_layout = QHBoxLayout()
    ok_button = QPushButton("Aceptar")
    cancel_button = QPushButton("Cancelar")
    cancel_button.setObjectName("cancel")
    button_layout.addWidget(ok_button)
    button_layout.addWidget(cancel_button)
    layout.addLayout(button_layout)

    def accept():
        dialog.accept()

    def reject():
        dialog.reject()

    ok_button.clicked.connect(accept)
    cancel_button.clicked.connect(reject)

    if dialog.exec() == QDialog.Accepted:
        name = line_edit.text().strip() or "Sin nombre"
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
        print("Operación cancelada.")
