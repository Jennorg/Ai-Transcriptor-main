# audiorecorder.py
import sounddevice as sd
import wavio
import assemblyai as aai
from PySide6.QtWidgets import (QFileDialog,QMessageBox)
from PySide6.QtCore import QTimer  # ¡Importante añadir esta línea!
from pymongo import MongoClient  
from MongoDB_Manager import save_transcription_to_mongodb

# Configuración de la API Key de AssemblyAI
aai.settings.api_key = "ad5c91f0f3164e0290ad3f4a21c3c0c7"  # Reemplaza con tu API Key real

# Configuración global para transcripciones en español
transcription_config = aai.TranscriptionConfig(language_code="es")  # "es" para español

import numpy as np # Asegúrate de importar numpy

class AudioRecorder:
    def __init__(self, master, status_label, audio_file_label, transcription_label) :
        self.master = master # 'master' será la ventana principal de PySide6
        self.is_recording = False
        self.audio_file = None
        self.audio_file_path = None
        self.fs = 44100
        self.audio_data = []
        self.modo_transcripcion = None

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
                    print(status)
                self.audio_data.append(indata.copy())

            # Iniciar la grabación continua utilizando callback
            try:
                self.stream = sd.InputStream(samplerate=self.fs, channels=2, dtype='int16', callback=callback)
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
            wavio.write("grabacion.wav", full_audio, self.fs, sampwidth=2)  # Guardar el archivo
            print("Grabación guardada como 'grabacion.wav'")
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
            self.audio_file_label.setText(f"Archivo seleccionado: {file_path.split('/')[-1]}") # Usar setText para QLabel en PySide6
            print(f"Archivo cargado: {file_path}")
        else:
            self.audio_file_label.setText("No se ha seleccionado un archivo") # Usar setText para QLabel en PySide6
            print("No se seleccionó archivo")

    def transcribe_audio(self):
        if not self.audio_file_path:
            self.transcription_label.setText("No hay archivo para transcribir") # Usar setText para QLabel en PySide6
            return
        
        #  Mostrar ventana emergente para elegir el modo de transcripción
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Modo de Transcripción")
        msg_box.setText("¿Cómo deseas transcribir el audio?")

        # Agregar botones personalizados
        button_monologo = msg_box.addButton("Como monólogo", QMessageBox.AcceptRole)
        button_dialogo = msg_box.addButton("Como diálogo", QMessageBox.RejectRole)

        msg_box.exec()

        # Determinar qué opción eligió el usuario
        if msg_box.clickedButton() == button_monologo:
            self.modo_transcripcion = "monologo"
        elif msg_box.clickedButton() == button_dialogo:
            self.modo_transcripcion = "dialogo"
        else:
            self.transcription_label.setText("No se seleccionó un modo de transcripción.")
            return  #  No continuar si no se eligió un modo

        # Subir archivo a AssemblyAI
        transcript_text = self.transcribe_with_assemblyai(self.audio_file_path)

        if transcript_text:
            self.transcription_label.setText(f"Transcripción: {transcript_text}") # Usar setText para QLabel en PySide6
            # Guardar la transcripción en un archivo .txt
            self.save_transcription_to_file(transcript_text)
        else:
            self.transcription_label.setText("Error al transcribir el archivo") # Usar setText para QLabel en PySide6

    def transcribe_with_assemblyai(self, file_path):
        try:
            # Configurar transcripción según el modo seleccionado
            if self.modo_transcripcion == "dialogo":
                config = aai.TranscriptionConfig(language_code="es", speaker_labels=True)  # Habilitar etiquetas de hablantes
            else:
                config = aai.TranscriptionConfig(language_code="es", speaker_labels=False)  # Deshabilitar etiquetas de hablantes

            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(file_path, config=config)

            if transcript.status == aai.TranscriptStatus.error:
                print(f"Error en la transcripción: {transcript.error}")
                return None

            print("Transcripción completada exitosamente.")

            if self.modo_transcripcion == "dialogo":
                if not transcript.utterances:  # Verifica si utterances es None o vacío
                    print("No se encontraron etiquetas de hablantes en la transcripción.")
                    return transcript.text  # Devuelve el texto normal si no hay hablantes
                transcribed_text = self.format_speaker_labels(transcript.utterances)
                save_transcription_to_mongodb(self.master, transcribed_text)
                return transcribed_text
            else:
                save_transcription_to_mongodb(self.master, transcript.text)
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