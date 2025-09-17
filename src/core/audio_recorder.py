import os
import sounddevice as sd
import wavio
import assemblyai as aai
from PySide6.QtWidgets import (QFileDialog, QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout)
from PySide6.QtCore import QTimer, Qt
from pymongo import MongoClient  
from dotenv import load_dotenv
import numpy as np

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de la API Key de AssemblyAI desde variables de entorno
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')
HAS_VALID_API_KEY = False

# Solo configurar la API si es válida
if ASSEMBLYAI_API_KEY and ASSEMBLYAI_API_KEY != "test_key_placeholder":
    try:
        aai.settings.api_key = ASSEMBLYAI_API_KEY
        HAS_VALID_API_KEY = True
        print("API Key de AssemblyAI configurada correctamente")
    except Exception as e:
        print(f"Error al configurar API Key: {e}")
        HAS_VALID_API_KEY = False
else:
    print("ADVERTENCIA: API Key de AssemblyAI no está configurada o es inválida")
    HAS_VALID_API_KEY = False

# Configuración global para transcripciones
DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'es')  # Por defecto español
transcription_config = aai.TranscriptionConfig(language_code=DEFAULT_LANGUAGE)

class AudioRecorder:
    def __init__(self, master, status_label, audio_file_label, transcription_label) :
        self.master = master # 'master' será la ventana principal de PySide6
        self.is_recording = False
        self.audio_file = None
        self.audio_file_path = None
        # Configuración de audio mejorada para reducir distorsión
        self.fs = 16000  # Sample rate más bajo para mejor calidad
        self.audio_data = []
        # self.modo_transcripcion = None  # Esto ya no se maneja aquí directamente

        # UI elements to update from class
        self.status_label = status_label  # QLabel para el estado
        self.audio_file_label = audio_file_label # QLabel para el nombre del archivo
        self.transcription_label = transcription_label # QLabel para la transcripción

    def start_recording(self):
        self.is_recording = True
        self.audio_data = []  # Reiniciar los datos de audio
        self.status_label.setText("Grabando...")  # Actualizar la etiqueta de estado
        self.record_audio()

    def record_audio(self):
        if self.is_recording:
            # Grabar audio de forma continua en fragmentos mientras is_recording sea True
            def callback(indata, frames, time, status):
                """Esta función se llama (por sounddevice) para cada bloque de audio grabado"""
                if status:
                    print(f"Status de audio: {status}")
                # Normalizar el audio para evitar distorsión
                max_val = np.max(np.abs(indata))
                if max_val > 0:
                    indata = indata / max_val * 0.8  # Reducir volumen al 80%
                self.audio_data.append(indata.copy())

            # Configuración de grabación mejorada
            try:
                # Usar mono (1 canal) y float32 para mejor calidad
                self.stream = sd.InputStream(
                    samplerate=self.fs, 
                    channels=1,  # Mono en lugar de estéreo
                    dtype='float32',  # Float32 en lugar de int16
                    callback=callback,
                    blocksize=1024  # Tamaño de bloque más pequeño
                )
                self.stream.start()
                self.status_label.setText("Grabando... (Grabación continua)") # Actualizar etiqueta para indicar grabación continua
            except Exception as e:
                print(f"Error al iniciar la grabación continua: {e}")
                self.is_recording = False # Detener el estado de grabación si hay un error
                self.status_label.setText("Error al grabar") # Actualizar etiqueta de estado a error

    def stop_recording(self):
        self.is_recording = False
        if hasattr(self, 'stream') and self.stream.active:
            self.stream.stop()
            self.stream.close()
        self.status_label.setText("Grabación detenida")
        self.save_audio()

    def save_audio(self):
        if self.audio_data:
            # Concatenar todos los fragmentos de audio
            full_audio = np.concatenate(self.audio_data, axis=0)
            
            # Convertir a int16 para wavio (que espera int16)
            # Normalizar y convertir
            max_val = np.max(np.abs(full_audio))
            if max_val > 0:
                full_audio = full_audio / max_val * 0.8  # Normalizar al 80%
            
            # Convertir a int16
            full_audio_int16 = (full_audio * 32767).astype(np.int16)
            
            # Guardar con configuración optimizada
            wavio.write("grabacion.wav", full_audio_int16, self.fs, sampwidth=2)
            print("Grabación guardada como 'grabacion.wav'")
            print(f"Tamaño del archivo: {len(full_audio_int16)} samples")
            print(f"Sample rate: {self.fs} Hz")
            print(f"Canales: 1 (mono)")
            print(f"Tipo de datos: int16")
            self.audio_file_path = "grabacion.wav"  # Establecer la ruta del archivo grabado

    def upload_audio(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.master,  # Pasar la ventana principal como parent
            "Subir archivo de audio",  # Título del diálogo
            "",  # Directorio inicial
            "Archivos de audio (*.wav *.mp3 *.ogg)"  # Filtro de archivos
        )
        
        if file_path:
            self.audio_file_path = file_path
            self.audio_file_label.setText(f"Archivo: {os.path.basename(file_path)}")
            return True
    
    def transcribe_audio(self, transcription_mode):
        """Método simplificado para transcripción."""
        if not self.audio_file_path:
            print("Error: No hay archivo de audio para transcribir")
            # QMessageBox.warning(self.master, "Error", "No hay archivo de audio para transcribir.") # Manejado en MainWindow
            return False

        # Verificar si hay API key válida
        if not HAS_VALID_API_KEY:
            # QMessageBox.warning(self.master, "API Key Requerida", "Para usar la funcionalidad de transcripción, necesitas configurar una API key válida de AssemblyAI en el archivo config/.env") # Manejado en MainWindow
            # self.transcription_label.setText("Error: API Key no configurada") # Manejado en MainWindow
            print("Error: API Key de AssemblyAI no configurada o es inválida.")
            return False

        print(f"Iniciando transcripcion en modo: {transcription_mode}")
        # Realizar la transcripción
        transcript_text = self.transcribe_with_assemblyai(self.audio_file_path, transcription_mode)

        if transcript_text:
            try:
                # Mostrar la transcripción en la interfaz
                self.transcription_label.setText(f"Transcripción: {transcript_text}")
                print(f"Transcripción mostrada en interfaz: {len(transcript_text)} caracteres")
            except Exception as e:
                print(f"Error al mostrar transcripción en interfaz: {e}")
            
            try:
                # Guardar la transcripción en un archivo .txt
                self.save_transcription_to_file(transcript_text)
                print("Archivo de transcripción guardado localmente")
            except Exception as e:
                print(f"Error al guardar archivo local: {e}")
            
            try:
                # Intentar guardar en MongoDB
                from services.database_manager import save_transcription_to_mongodb
                save_transcription_to_mongodb(self.master, transcript_text, transcription_mode) # Pasar modo a MongoDB
                print("Transcripción guardada en MongoDB")
            except Exception as e:
                print(f"Error al guardar en MongoDB: {e}")
                # No fallar si MongoDB tiene problemas
            
            return True
        else:
            # self.transcription_label.setText("Error al transcribir el archivo") # Manejado en MainWindow
            print("Error: No se obtuvo texto de transcripción")
            # QMessageBox.critical(self.master, "Error", "No se pudo transcribir el archivo de audio.") # Manejado en MainWindow
            return False


    def transcribe_with_assemblyai(self, file_path, transcription_mode):
        try:
            print(f"Iniciando transcripción de: {file_path}")
            print(f"Modo de transcripción: {transcription_mode}")
            
            # Configurar transcripción según el modo seleccionado
            if transcription_mode == "dialogo":
                config = aai.TranscriptionConfig(language_code="es", speaker_labels=True)
            else:
                config = aai.TranscriptionConfig(language_code="es", speaker_labels=False)

            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(file_path, config=config)

            if transcript.status == aai.TranscriptStatus.error:
                print(f"Error en la transcripción: {transcript.error}")
                return None

            print("Transcripción completada exitosamente.")
            print(f"DEBUG: transcript.text = {repr(transcript.text)}")
            print(f"DEBUG: transcript.text is None = {transcript.text is None}")
            print(f"Longitud del texto: {len(transcript.text) if transcript.text else 0}")

            if transcription_mode == "dialogo":
                if not transcript.utterances:
                    print("No se encontraron etiquetas de hablantes en la transcripción.")
                    print(f"Devolviendo texto normal: '{transcript.text}'")
                    return transcript.text
                print("Formateando con etiquetas de hablantes...")
                transcribed_text = self.format_speaker_labels(transcript.utterances)
                print(f"Texto formateado: '{transcribed_text}'")
                return transcribed_text
            else:
                print(f"Devolviendo texto para monólogo: '{transcript.text}'")
                return transcript.text
        except Exception as e:
            print(f"Error al transcribir: {e}")
            return None
            
    def format_speaker_labels(self, utterances):
        """
        Formatea la transcripción incluyendo etiquetas de hablantes.
        """
        formatted_text = ""
        for utterance in utterances:
            speaker = f"Locutor {utterance.speaker}:"
            formatted_text += f"{speaker} {utterance.text}\n"
        return formatted_text

    def save_transcription_to_file(self, transcription):
        with open("transcripcion.txt", "w") as file:
            file.write(transcription)
        print("Transcripción guardada en 'transcripcion.txt'")
