from pymongo import MongoClient
from PySide6.QtWidgets import QInputDialog  
from datetime import datetime

# Configuración de MongoDB Atlas
MONGO_URI = "mongodb+srv://tendencias:1234@Transcripciones.2bftm.mongodb.net/?retryWrites=true&w=majority&appName=Transcripciones"
client = MongoClient(MONGO_URI)
db = client["Transcripcion"]
collection = db["Texto_de_Transcripcion"]

def save_transcription_to_mongodb(parent, transcription):
    """Guarda la transcripción en MongoDB con un nombre ingresado por el usuario."""
    name, ok = QInputDialog.getText(parent, "Guardar Texto", "Ingrese el nombre del texto:")
    
    if ok and name.strip():
        try:
            document = {
                "nombre": name.strip(), 
                "texto": transcription,
                "fecha_subida": datetime.now() 
                } 
            collection.insert_one(document)
            print(f"Texto '{name}' guardado en MongoDB")
        except Exception as e:
            print(f"Error al guardar en MongoDB: {e}")
    else:
        print("Operación cancelada o nombre vacío.")
