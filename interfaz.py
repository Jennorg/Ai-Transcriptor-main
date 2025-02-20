# interfaz_pyside.py
import sys
from PySide6.QtWidgets import (QApplication, QWidget, QLabel,
                            QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy, QMessageBox)
import Transcripcion_con_Assembly
from lista_texto import MongoDBViewer  # Importa MongoDBViewer

class AudioRecorderUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ai Interpreter")
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: "Arial";
            }

            /* Sidebar styles */
            QFrame#sidebar {
                background-color: #e0e0e0;
                border-right: 1px solid #c0c0c0;
                padding: 20px;
                width: 200px; 
                min-width: 200px;
                max-width: 200px;
            }

            QPushButton#sidebarButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 16px;
                margin-bottom: 10px;
                width: 100%; 
                text-align: left; 
            }

            QPushButton#sidebarButton:hover {
                background-color: #45a049;
            }

            QPushButton#sidebarButton:pressed {
                background-color: #367c39;
            }

            QPushButton#recordStopButton {
                background-color: #f44336; 
                color: white;
                border: none;
                padding: 15px 25px; 
                border-radius: 25px; 
                font-size: 18px;
                margin-top: 20px; 
                width: 100%;
                max-width: 100%; 
            }

            QPushButton#recordStopButton:hover {
                background-color: #d32f2f; 
            }

            QPushButton#recordStopButton:pressed {
                background-color: #b71c1c;
            }


            /* Main content styles */
            QWidget#main_content {
                padding: 20px;
            }

            QLabel {
                color: #333;
                font-size: 16px;
                margin-bottom: 10px;
            }

            QLabel#transcriptionLabel {
                font-size: 14px;
                font-family: monospace;
                background-color: #ffffff; 
                border: 1px solid #c0c0c0;
                padding: 10px;
                border-radius: 5px;
                min-height: 150px; 
                word-wrap: break-word;
            }
        """)

        # Main layout: Horizontal layout for sidebar and main content
        main_layout = QHBoxLayout(self)

        # Sidebar Frame
        sidebar_frame = QFrame(self)
        sidebar_frame.setObjectName("sidebar") # For CSS styling
        sidebar_layout = QVBoxLayout(sidebar_frame)

        # Sidebar Buttons (Upload and Transcribe at the top)
        self.upload_button = QPushButton("Subir Archivo")
        self.upload_button.setObjectName("sidebarButton") # For CSS Styling
        self.transcribe_button = QPushButton("Transcribir")
        self.transcribe_button.setObjectName("sidebarButton") # For CSS Styling
        self.list_texts_button = QPushButton("Listar Textos")  # Nuevo botón
        self.list_texts_button.setObjectName("sidebarButton")  # For CSS Styling

        sidebar_layout.addWidget(self.upload_button)
        sidebar_layout.addWidget(self.transcribe_button)
        sidebar_layout.addWidget(self.list_texts_button)  # Añadir el nuevo botón
        sidebar_layout.addStretch() # Add vertical space to push buttons upwards

        # Record and Stop Buttons at the bottom of sidebar
        self.record_button = QPushButton("Grabar")
        self.record_button.setObjectName("recordStopButton") # For CSS Styling
        self.stop_button = QPushButton("Detener")
        self.stop_button.setObjectName("recordStopButton") # For CSS Styling

        sidebar_layout.addWidget(self.record_button)
        sidebar_layout.addWidget(self.stop_button)

        sidebar_frame.setLayout(sidebar_layout) # Set layout for sidebar frame
        main_layout.addWidget(sidebar_frame) # Add sidebar to main layout

        # Main Content Area (Right side - for status and transcription)
        main_content_widget = QWidget(self)
        main_content_widget.setObjectName("main_content") # For CSS styling
        main_content_layout = QVBoxLayout(main_content_widget)

        # Status and File Labels in the middle content area
        self.status_label = QLabel("Estado: Listo")
        self.audio_file_label = QLabel("No se ha subido archivo")

        main_content_layout.addWidget(self.status_label)
        main_content_layout.addWidget(self.audio_file_label)

        # Transcription Label (takes more space)
        self.transcription_label = QLabel("Transcripción: No disponible")
        self.transcription_label.setObjectName("transcriptionLabel") # For CSS styling
        self.transcription_label.setWordWrap(True) # Enable word wrap for long transcriptions
        self.transcription_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # Allow vertical expansion

        main_content_layout.addWidget(self.transcription_label)

        main_content_widget.setLayout(main_content_layout) # Set layout for main content widget
        main_layout.addWidget(main_content_widget) # Add main content to main layout

        self.setLayout(main_layout) # Set main layout for the window

        # Crear instancia de AudioRecorder
        self.recorder = Transcripcion_con_Assembly.AudioRecorder(self, self.status_label, self.audio_file_label, self.transcription_label)

        # Conectar señales de los botones a las funciones
        self.record_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.upload_button.clicked.connect(self.upload_audio)
        self.transcribe_button.clicked.connect(self.transcribe_audio)
        self.list_texts_button.clicked.connect(self.open_list_texts)  # Conectar el nuevo botón

        self.showMaximized() # Maximize the window on startup

    def start_recording(self):
        self.recorder.start_recording()
        self.status_label.setText("Estado: Grabando...")

    def stop_recording(self):
        self.recorder.stop_recording()
        self.status_label.setText("Estado: Listo")

    def upload_audio(self):
        self.recorder.upload_audio()

    def transcribe_audio(self):
        # Llamar a la función de transcripción
        self.recorder.transcribe_audio()

    def open_list_texts(self):
        self.list_texts_window = MongoDBViewer()
        self.list_texts_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = AudioRecorderUI()
    ui.show()
    sys.exit(app.exec())