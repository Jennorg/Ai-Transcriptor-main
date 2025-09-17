import os
from pymongo import MongoClient
from PySide6.QtWidgets import QInputDialog, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de MongoDB desde variables de entorno
MONGODB_CONNECTION_STRING = "mongodb+srv://tendencias:1234@transcripciones.2bftm.mongodb.net/?retryWrites=true&w=majority&appName=Transcripciones"
MONGODB_DATABASE_NAME = "Transcripcion"
MONGODB_COLLECTION_NAME = "Texto_de_Transcripcion"

# Conectar a MongoDB
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client[MONGODB_DATABASE_NAME]
collection = db[MONGODB_COLLECTION_NAME]

def save_transcription_to_mongodb(transcription_name, transcription_text, mode="monologo"):
    """Guarda la transcripción en MongoDB con un nombre ingresado por el usuario."""
    
    if not transcription_name.strip():
        print("Error: El nombre de la transcripción no puede estar vacío.")
        return False
        
    try:
        # Crear documento para MongoDB
        document = {
            "name": transcription_name,
            "transcription": transcription_text,
            "timestamp": datetime.now(),
            "language": "es",
            "mode": mode # Guardar el modo de transcripción
        }
        
        # Insertar en MongoDB
        result = collection.insert_one(document)
        
        if result.inserted_id:
            print(f"Transcripción \'{transcription_name}\' guardada en MongoDB con ID: {result.inserted_id}")
            return True
        else:
            print("Error: No se pudo guardar la transcripción en MongoDB.")
            return False
            
    except Exception as e:
        print(f"Error al guardar en MongoDB: {str(e)}")
        return False

def get_all_transcriptions():
    """Obtiene todas las transcripciones de MongoDB."""
    try:
        transcriptions = list(collection.find().sort("timestamp", -1))
        return transcriptions
    except Exception as e:
        print(f"Error al obtener transcripciones: {str(e)}")
        return []

def delete_transcription(transcription_id):
    """Elimina una transcripción de MongoDB."""
    try:
        from bson import ObjectId
        result = collection.delete_one({"_id": ObjectId(transcription_id)})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error al eliminar transcripción: {str(e)}")
        return False

def search_transcriptions(query):
    """Busca transcripciones por nombre o contenido."""
    try:
        # Buscar por nombre o contenido de transcripción
        search_filter = {
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"transcription": {"$regex": query, "$options": "i"}}
            ]
        }
        transcriptions = list(collection.find(search_filter).sort("timestamp", -1))
        return transcriptions
    except Exception as e:
        print(f"Error al buscar transcripciones: {str(e)}")
        return []
