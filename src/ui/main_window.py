import sys
import os
from PySide6.QtWidgets import (QApplication, QWidget, QLabel,
                            QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy, QMessageBox, QFileDialog, QDialog, QLineEdit)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, Qt
from PySide6.QtCore import QSize, QTimer, QThread, QObject, Signal
from pathlib import Path

# Imports relativos desde la nueva estructura
from core.audio_recorder import AudioRecorder
from ui.transcription_viewer import MongoDBViewer

# Direcciones de iconos
project_root = Path(__file__).parent.parent.parent
icon_path_upload = project_root / "assets" / "images" / "upload.png"
icon_path_transcribe = project_root / "assets" / "images" / "transcription.png"
icon_path_list = project_root / "assets" / "images" / "list.png"
icon_path_record = project_root / "assets" / "images" / "rec-button.png"
icon_path_stop = project_root / "assets" / "images" / "stop-button.png"

def colorize_icon(icon_path, color):
    pixmap = QPixmap(icon_path)
    painter = QPainter(pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), color)
    painter.end()
    return QIcon(pixmap)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.audio_recorder = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("AI Transcriptor")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title_label = QLabel("AI Transcriptor")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Sección de grabación
        recording_frame = QFrame()
        recording_frame.setFrameStyle(QFrame.Box)
        recording_frame.setStyleSheet("QFrame { border: 2px solid #3498db; border-radius: 10px; padding: 15px; }")
        recording_layout = QVBoxLayout()

        recording_title = QLabel("Grabación de Audio")
        recording_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        recording_layout.addWidget(recording_title)

        # Botones de grabación
        button_layout = QHBoxLayout()
        
        self.record_button = QPushButton("🎤 Grabar Audio")
        self.record_button.clicked.connect(self.start_recording)
        
        self.stop_button = QPushButton("⏹️ Detener")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.record_button)
        button_layout.addWidget(self.stop_button)
        recording_layout.addLayout(button_layout)

        # Estado de grabación
        self.status_label = QLabel("Listo para grabar")
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        recording_layout.addWidget(self.status_label)

        recording_frame.setLayout(recording_layout)
        main_layout.addWidget(recording_frame)

        # Sección de transcripción
        transcription_frame = QFrame()
        transcription_frame.setFrameStyle(QFrame.Box)
        transcription_frame.setStyleSheet("QFrame { border: 2px solid #e74c3c; border-radius: 10px; padding: 15px; }")
        transcription_layout = QVBoxLayout()

        transcription_title = QLabel("Transcripción")
        transcription_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        transcription_layout.addWidget(transcription_title)

        # Botones de transcripción
        transcription_buttons_layout = QHBoxLayout()
        
        self.transcribe_button = QPushButton("📝 Transcribir Audio")
        self.transcribe_button.clicked.connect(self.transcribe_audio)
        self.transcribe_button.setEnabled(False)
        
        self.upload_button = QPushButton("📁 Subir Archivo")
        self.upload_button.clicked.connect(self.upload_audio_file)
        
        transcription_buttons_layout.addWidget(self.transcribe_button)
        transcription_buttons_layout.addWidget(self.upload_button)
        transcription_layout.addLayout(transcription_buttons_layout)

        # Archivo de audio
        self.audio_file_label = QLabel("Ningún archivo seleccionado")
        self.audio_file_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        transcription_layout.addWidget(self.audio_file_label)

        # Spinner de carga
        self.spinner_label = QLabel("")
        self.spinner_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
            }
        """)
        self.spinner_label.setAlignment(Qt.AlignCenter)
        self.spinner_label.hide()  # Ocultar inicialmente
        transcription_layout.addWidget(self.spinner_label)

        # Resultado de transcripción
        self.transcription_label = QLabel("La transcripción aparecerá aquí...")
        self.transcription_label.setStyleSheet("""
            background-color: white;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            padding: 10px;
            min-height: 100px;
            word-wrap: break-word;
        """)
        self.transcription_label.setWordWrap(True)
        transcription_layout.addWidget(self.transcription_label)

        transcription_frame.setLayout(transcription_layout)
        main_layout.addWidget(transcription_frame)

        # Botones de acción
        action_layout = QHBoxLayout()
        
        self.view_history_button = QPushButton("📋 Ver Historial")
        self.view_history_button.clicked.connect(self.view_history)
        
        action_layout.addWidget(self.view_history_button)
        main_layout.addLayout(action_layout)

        self.setLayout(main_layout)

    def start_recording(self):
        if not self.audio_recorder:
            self.audio_recorder = AudioRecorder(
                self, self.status_label, self.audio_file_label, self.transcription_label
            )
        
        self.audio_recorder.start_recording()
        self.record_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_recording(self):
        if self.audio_recorder:
            self.audio_recorder.stop_recording()
            self.record_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.transcribe_button.setEnabled(True)

    def upload_audio_file(self):
        """Permite al usuario subir un archivo de audio."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de audio",
            "",
            "Archivos de audio (*.wav *.mp3 *.m4a *.flac *.ogg *.aac *.wma);;Todos los archivos (*)"
        )
        
        if file_path:
            # Crear el audio_recorder si no existe
            if not self.audio_recorder:
                self.audio_recorder = AudioRecorder(
                    self, self.status_label, self.audio_file_label, self.transcription_label
                )
            
            # Establecer el archivo de audio
            self.audio_recorder.audio_file_path = file_path
            self.audio_file_label.setText(f"Archivo: {os.path.basename(file_path)}")
            self.transcribe_button.setEnabled(True)
            
            QMessageBox.information(self, "Archivo Cargado", f"Archivo cargado exitosamente: {os.path.basename(file_path)}")

    def get_transcription_mode(self):
        """Muestra un diálogo para que el usuario seleccione el modo de transcripción."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Modo de Transcripción")
        dialog.setModal(True)
        dialog.resize(400, 200)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                border-radius: 10px;
            }
            QLabel {
                color: #333;
                font-size: 14px;
                margin: 10px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                margin: 10px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title_label = QLabel("Selecciona el modo de transcripción:")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        button_monologo = QPushButton("Monologo")
        button_dialogo = QPushButton("Dialogo")
        
        button_layout.addWidget(button_monologo)
        button_layout.addWidget(button_dialogo)
        layout.addLayout(button_layout)

        self.selected_transcription_mode = None

        def select_monologo():
            self.selected_transcription_mode = "monologo"
            dialog.accept()

        def select_dialogo():
            self.selected_transcription_mode = "dialogo"
            dialog.accept()

        button_monologo.clicked.connect(select_monologo)
        button_dialogo.clicked.connect(select_dialogo)

        dialog.setLayout(layout)
        result = dialog.exec()
        
        if result == QDialog.Accepted and self.selected_transcription_mode:
            return self.selected_transcription_mode
        else:
            return None

    def start_spinner(self, message="Transcribiendo..."):
        """Inicia el spinner de carga."""
        self.spinner_label.setText(f"⏳ {message}")
        self.spinner_label.show()
        self.transcribe_button.setEnabled(False)
        self.upload_button.setEnabled(False)
        self.record_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        # Crear un timer para animar el spinner
        self.spinner_timer = QTimer()
        self.spinner_timer.timeout.connect(self.update_spinner)
        self.spinner_timer.start(500)  # Actualizar cada 500ms
        self.spinner_dots = 0

    def update_spinner(self):
        """Actualiza la animación del spinner."""
        self.spinner_dots = (self.spinner_dots + 1) % 4
        dots = "." * self.spinner_dots
        current_text = self.spinner_label.text()
        if "⏳" in current_text:
            base_message = current_text.split("⏳")[1].split("...")[0].strip()
            self.spinner_label.setText(f"⏳ {base_message}{dots}")

    def stop_spinner(self):
        """Detiene el spinner de carga."""
        if hasattr(self, 'spinner_timer'):
            self.spinner_timer.stop()
        self.spinner_label.hide()
        self.transcribe_button.setEnabled(True)
        self.upload_button.setEnabled(True)
        self.record_button.setEnabled(True)

    def transcribe_audio(self):
        """Inicia el proceso de transcripción con spinner."""
        if not self.audio_recorder or not self.audio_recorder.audio_file_path:
            QMessageBox.warning(self, "Error", "No hay archivo de audio para transcribir.")
            return

        # Iniciar spinner
        self.start_spinner("Transcribiendo audio")
        
        # Obtener el modo de transcripción del usuario
        transcription_mode = self.get_transcription_mode()
        if not transcription_mode:
            self.stop_spinner() # Detener spinner si el usuario cancela
            self.transcription_label.setText("Transcripción cancelada")
            QMessageBox.information(self, "Cancelado", "Transcripción cancelada por el usuario.")
            return

        # Ejecutar transcripción en un hilo separado para no bloquear la UI
        class TranscriptionWorker(QObject):
            finished = Signal(str, str) # Emitir texto y modo
            error = Signal(str)
            
            def __init__(self, audio_recorder, transcription_mode):
                super().__init__()
                self.audio_recorder = audio_recorder
                self.transcription_mode = transcription_mode
            
            def run(self):
                try:
                    # Pasar el modo de transcripción seleccionado
                    transcript_text = self.audio_recorder.transcribe_audio(self.transcription_mode)
                    if transcript_text:
                        self.finished.emit(transcript_text, self.transcription_mode) # Emitir el texto y el modo
                    else:
                        self.error.emit("Error en la transcripción")
                except Exception as e:
                    self.error.emit(f"Error: {str(e)}")
        
        # Crear y configurar el worker
        self.transcription_worker = TranscriptionWorker(self.audio_recorder, transcription_mode)
        self.transcription_thread = QThread()
        
        self.transcription_worker.moveToThread(self.transcription_thread)
        self.transcription_thread.started.connect(self.transcription_worker.run)
        self.transcription_worker.finished.connect(self.on_transcription_finished)
        self.transcription_worker.error.connect(self.on_transcription_error)
        self.transcription_worker.finished.connect(self.transcription_thread.quit)
        self.transcription_worker.error.connect(self.transcription_thread.quit)
        self.transcription_thread.finished.connect(self.transcription_thread.deleteLater)
        
        # Conectar la señal save_requested al método en el hilo principal
        self.save_requested.connect(self.prompt_for_save_and_save_transcription)
        
        # Iniciar el hilo
        self.transcription_thread.start()

    # Nueva señal para activar el guardado desde el hilo principal
    save_requested = Signal(str, str, str) # transcription_text, transcription_mode, audio_file_path

    def on_transcription_finished(self, transcription_text, transcription_mode):
        """Maneja la finalización exitosa de la transcripción."""
        self.stop_spinner()
        QMessageBox.information(self, "Éxito", "Transcripción completada")
        self.transcription_label.setText(f"Transcripción: {transcription_text}")
        
        # Emitir señal para pedir guardar en la BD
        self.save_requested.emit(transcription_text, transcription_mode, self.audio_recorder.audio_file_path)

    def on_transcription_error(self, error_message):
        """Maneja errores en la transcripción."""
        self.stop_spinner()
        QMessageBox.critical(self, "Error", error_message)
        self.transcription_label.setText("Error en la transcripción")

    def prompt_for_save_and_save_transcription(self, transcription_text, transcription_mode, audio_file_path):
        from services.database_manager import save_transcription_to_mongodb
        
        # Crear un QDialog personalizado para aplicar estilos
        dialog = QDialog(self)
        dialog.setWindowTitle("Guardar Transcripción")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                border-radius: 10px;
            }
            QLabel {
                color: #333;
                font-size: 14px;
                margin: 10px;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                margin: 5px;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Guardar Transcripción")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Campo de nombre
        name_label = QLabel("Nombre para la transcripción:")
        layout.addWidget(name_label)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Ej: Reunión del 15 de enero")
        name_input.setText(os.path.basename(audio_file_path).split('.')[0] if audio_file_path else "")
        layout.addWidget(name_input)
        
        # Botones
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Guardar")
        cancel_button = QPushButton("Cancelar")
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # Conectar botones
        save_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        # Mostrar diálogo
        if dialog.exec() == QDialog.Accepted:
            name = name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Error", "Por favor ingresa un nombre para la transcripción.")
                self.prompt_for_save_and_save_transcription(transcription_text, transcription_mode, audio_file_path) # Volver a pedir nombre
                return
            
            if save_transcription_to_mongodb(name, transcription_text, transcription_mode):
                QMessageBox.information(self, "Éxito", f"Transcripción guardada como: {name}")
            else:
                QMessageBox.critical(self, "Error", "No se pudo guardar la transcripción en MongoDB.")
        else:
            QMessageBox.information(self, "Cancelado", "Guardado de transcripción cancelado.")

    def view_history(self):
        try:
            self.history_window = MongoDBViewer(self)
            self.history_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el historial: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
