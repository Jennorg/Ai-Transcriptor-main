import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
project_root = Path(__file__).parent.parent.parent
config_path = project_root / "config" / ".env"
if config_path.exists():
    load_dotenv(config_path)

class Config:
    """Configuración centralizada de la aplicación."""
    
    # API Keys
    ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')
    GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')
    
    # MongoDB
    MONGODB_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
    MONGODB_DATABASE_NAME = os.getenv('MONGODB_DATABASE_NAME', 'ai_transcriptor')
    MONGODB_COLLECTION_NAME = os.getenv('MONGODB_COLLECTION_NAME', 'transcriptions')
    
    # Audio
    AUDIO_SAMPLE_RATE = int(os.getenv('AUDIO_SAMPLE_RATE', '16000'))
    AUDIO_CHANNELS = int(os.getenv('AUDIO_CHANNELS', '1'))
    DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'es')
    
    # Paths
    PROJECT_ROOT = project_root
    ASSETS_PATH = project_root / "assets"
    AUDIO_PATH = ASSETS_PATH / "audio"
    EXPORTS_PATH = ASSETS_PATH / "exports"
    IMAGES_PATH = ASSETS_PATH / "images"
