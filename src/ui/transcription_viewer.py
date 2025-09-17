import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QFileDialog, QTextEdit, QHBoxLayout, QDialog, QMainWindow, QFrame, QMessageBox)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt, QSize, QThread, QObject, Signal, QTimer # Added QTimer
from services.database_manager import get_all_transcriptions, delete_transcription, search_transcriptions, collection # Importar la colección
from utils.export_utils import save_as_pdf, save_as_txt
import os
# import time # Not strictly needed if not simulating delay
from datetime import datetime
from services.ai_service import obtener_respuesta
from fpdf import FPDF # Added for PDF export

# Direcciones de iconos
icon_path_pdf = os.path.join(os.path.dirname(__file__), "images", "pdf_icon.png")
icon_path_txt = os.path.join(os.path.dirname(__file__), "images", "txt_icon.png")
icon_path_ia = os.path.join(os.path.dirname(__file__), "images", "ia_icon.png")
icon_path_search = os.path.join(os.path.dirname(__file__), "images", "search_icon.png")
icon_path_refresh = os.path.join(os.path.dirname(__file__), "images", "refresh_icon.png")

class AIWorker(QObject):
    result_ready = Signal(str)
    error_occurred = Signal(str)
    finished = Signal() # Add this line

    def __init__(self, text_to_summarize, parent=None):
        super().__init__(parent)
        self.text_to_summarize = text_to_summarize

    def run(self):
        try:
            # Simulate a delay for network request
            # time.sleep(2) 
            summary = obtener_respuesta(f"Dame una explicación sobre: {self.text_to_summarize}")
            self.result_ready.emit(summary)
        except Exception as e:
            self.error_occurred.emit(f"Error al obtener respuesta de la IA: {str(e)}")
        finally:
            self.finished.emit() # Emit finished signal

class DetailWindow(QMainWindow):
    def __init__(self, parent=None, transcription_data=None):
        super().__init__(parent)
        self.transcription_data = transcription_data if transcription_data else {}
        
        self.setWindowTitle("Detalles de Transcripción")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
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
        """)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Extraer datos de self.transcription_data, manejando nombres de campo antiguos y nuevos
        name = self.transcription_data.get("name", self.transcription_data.get("nombre", "Sin nombre"))
        transcription_text = self.transcription_data.get("transcription", self.transcription_data.get("texto", "No hay transcripción para mostrar."))
        timestamp_raw = self.transcription_data.get("timestamp", self.transcription_data.get("fecha_subida", None))
        language = self.transcription_data.get("language", "es")
        mode = self.transcription_data.get("mode", "monologo") # Asumiendo un modo por defecto si no está presente

        # Formatear la fecha
        formatted_timestamp = "Fecha no disponible"
        if timestamp_raw:
            try:
                formatted_timestamp = timestamp_raw.strftime("%Y-%m-%d %H:%M")
            except Exception:
                formatted_timestamp = "Fecha inválida"

        # Título
        title_label = QLabel(name)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Detalles (timestamp, language, mode)
        details_layout = QHBoxLayout()
        timestamp_label = QLabel(formatted_timestamp)
        language_label = QLabel(f"Idioma: {language.upper()}")
        mode_label = QLabel(f"Modo: {mode.capitalize()}")
        
        details_layout.addWidget(timestamp_label)
        details_layout.addWidget(language_label)
        details_layout.addWidget(mode_label)
        details_layout.setAlignment(Qt.AlignLeft)
        main_layout.addLayout(details_layout)

        # Área de texto de la transcripción (original)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(transcription_text)
        main_layout.addWidget(self.text_edit)

        # Nuevos elementos para la respuesta de IA en la misma ventana
        self.ai_response_text_edit = QTextEdit()
        self.ai_response_text_edit.setReadOnly(True)
        self.ai_response_text_edit.hide() # Oculto por defecto
        main_layout.addWidget(self.ai_response_text_edit)

        self.ai_loading_label = QLabel("Procesando IA...")
        self.ai_loading_label.setAlignment(Qt.AlignCenter)
        self.ai_loading_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        self.ai_loading_label.hide() # Oculto por defecto
        main_layout.addWidget(self.ai_loading_label)

        # Botones de acción
        action_layout = QHBoxLayout()
        export_pdf_button = QPushButton("Exportar PDF")
        export_pdf_button.clicked.connect(lambda: self.export_to_pdf(name, transcription_text))
        export_txt_button = QPushButton("Exportar TXT")
        export_txt_button.clicked.connect(lambda: self.export_to_txt(name, transcription_text))
        self.chat_ia_button = QPushButton("Chat IA") # Nuevo botón para chat IA, make it a member variable
        self.chat_ia_button.clicked.connect(lambda: self.start_ai_worker(transcription_text)) # Connect to new method
        
        self.back_to_transcription_button = QPushButton("Volver a Transcripción")
        self.back_to_transcription_button.hide() # Oculto por defecto
        self.back_to_transcription_button.clicked.connect(self._show_original_transcription)

        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.close)

        action_layout.addWidget(export_pdf_button)
        action_layout.addWidget(export_txt_button)
        action_layout.addWidget(self.chat_ia_button) # Use self.chat_ia_button
        action_layout.addWidget(self.back_to_transcription_button)
        action_layout.addStretch()
        action_layout.addWidget(close_button)
        main_layout.addLayout(action_layout)

        # Configurar el timer para la animación de carga
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._update_loading_animation)
        self.ellipsis_count = 0

    def _update_loading_animation(self):
        self.ellipsis_count = (self.ellipsis_count + 1) % 4
        self.ai_loading_label.setText("Procesando IA" + "." * self.ellipsis_count)

    def start_ai_worker(self, text_to_summarize):
        self.chat_ia_button.setEnabled(False) # Disable button during processing
        
        # Ocultar la transcripción original y mostrar la animación de carga
        self.text_edit.hide()
        self.ai_response_text_edit.hide() # Asegurarse de que el área de respuesta esté oculta
        self.back_to_transcription_button.hide()
        self.ai_loading_label.show()
        self.animation_timer.start(500) # Iniciar animación cada 500 ms

        self.thread = QThread()
        self.worker = AIWorker(text_to_summarize)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.result_ready.connect(self.on_ai_result_ready)
        self.worker.error_occurred.connect(self.on_ai_error)
        self.worker.finished.connect(self.thread.quit) # Ensure worker finishes before thread quits
        self.worker.finished.connect(self.worker.deleteLater) # Clean up worker
        self.thread.finished.connect(self.thread.deleteLater) # Clean up thread

        self.thread.start()

    def on_ai_result_ready(self, summary):
        self.animation_timer.stop() # Detener animación
        self.ai_loading_label.hide() # Ocultar label de animación
        self.chat_ia_button.setEnabled(True) # Re-enable chat button
        
        self.ai_response_text_edit.setText(summary)
        self.ai_response_text_edit.show() # Mostrar el resultado de la IA
        self.back_to_transcription_button.show() # Mostrar el botón para volver

    def on_ai_error(self, error_message):
        self.animation_timer.stop() # Detener animación
        self.ai_loading_label.hide() # Ocultar label de animación
        self.chat_ia_button.setEnabled(True) # Re-enable chat button
        
        self.ai_response_text_edit.setText(f"Error: {error_message}")
        self.ai_response_text_edit.show() # Mostrar el error en el área de respuesta
        self.back_to_transcription_button.show() # Mostrar el botón para volver

        QMessageBox.critical(self, "Error de IA", error_message)

    def _show_original_transcription(self):
        self.ai_response_text_edit.hide()
        self.back_to_transcription_button.hide()
        self.text_edit.show()
        # self.chat_ia_button.setEnabled(True) # Not strictly necessary as it's already enabled after AI response

    def export_to_pdf(self, nombre, texto):
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", f"{nombre}.pdf", "Archivos PDF (*.pdf)")
        if file_name:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, texto.encode('latin-1', 'replace').decode('latin-1'))
                pdf.output(file_name)
                QMessageBox.information(self, "Éxito", "Transcripción exportada a PDF exitosamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar a PDF: {e}")

    def export_to_txt(self, nombre, texto):
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar TXT", f"{nombre}.txt", "Archivos de Texto (*.txt)")
        if file_name:
            try:
                with open(file_name, "w", encoding="utf-8") as file:
                    file.write(texto)
                QMessageBox.information(self, "Éxito", "Transcripción exportada a TXT exitosamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar a TXT: {e}")

    def ventana_ia(self, texto):
        # Lógica para la ventana de IA (similar a la que ya tenías)
        if not isinstance(texto, str):
            texto = str(texto)

        texto = texto.strip()

        # Obtener el resumen de la IA
        summary = obtener_respuesta(f"Dame una explicación sobre: {texto}")

        # Crear ventana para el resumen generado
        new_window = QDialog(self) # Usar QDialog y pasar self como parent
        new_window.setWindowTitle("Resumen Generado por IA")
        new_window.setGeometry(250, 250, 500, 350)
        new_window.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                border-radius: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #333;
                font-size: 14px;
                margin: 10px;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
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
        """)

        layout = QVBoxLayout(new_window) # Pasar new_window como parent al layout

        info_label = QLabel("Resumen generado por la IA:")
        layout.addWidget(info_label)

        text_display = QTextEdit()
        text_display.setReadOnly(True)
        text_display.setText(summary)
        layout.addWidget(text_display)

        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(new_window.close)
        layout.addWidget(close_button)

        new_window.exec() # Mostrar como diálogo modal


class MongoDBViewer(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historial de Transcripciones")
        self.setGeometry(150, 150, 900, 700)

        self.collection = collection  # Asignar la colección importada

        # Variables de paginación
        self.page = 0
        self.page_size = 14

        self.init_ui() # Llamar a init_ui después de inicializar la colección

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignCenter)
        title_label = QLabel("Historial de Transcripciones")
        title_label.setObjectName("HeaderTitle")
        header_layout.addWidget(title_label)
        main_layout.addWidget(header_frame)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar transcripciones por nombre o contenido...")
        self.search_button = QPushButton("Buscar")
        self.search_button.setIcon(QIcon(icon_path_search))
        self.search_button.setIconSize(QSize(20, 20))

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        main_layout.addLayout(search_layout)

        self.result_list = QListWidget()
        self.result_list.setFont(QFont('Segoe UI', 12))
        main_layout.addWidget(self.result_list)

        pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton("Anterior")
        self.prev_button.setIcon(QIcon(icon_path_refresh)) 
        self.prev_button.setIconSize(QSize(20, 20))
        self.page_label = QLabel("Página 1 de X")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.next_button = QPushButton("Siguiente")
        self.next_button.setIcon(QIcon(icon_path_refresh))
        self.next_button.setIconSize(QSize(20, 20))

        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)
        main_layout.addLayout(pagination_layout)

        self.search_input.returnPressed.connect(self.search_data) # Buscar al presionar Enter
        self.search_button.clicked.connect(self.search_data)
        self.result_list.itemDoubleClicked.connect(self.show_details)
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)

        self.load_transcriptions()
        self.apply_styles() # Aplicar estilos al final de la inicialización de la UI

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame#HeaderFrame {
                background-color: #4CAF50; /* Fondo verde para el título */
                color: white;
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 15px;
            }
            QLabel#HeaderTitle {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background-color: transparent; /* Quitar fondo gris */
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                color: #333;
            }
            QLineEdit:focus {
                border-color: #3498db;
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
            QListWidget {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #e0f2f7;
                color: #2c3e50;
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
        """)

    def search_data(self):
        self.page = 0
        self.load_transcriptions()

    def load_transcriptions(self):
        query_text = self.search_input.text().strip()
        query_filter = {}
        if query_text:
            query_filter = {
                "$or": [
                    {"name": {"$regex": query_text, "$options": "i"}},
                    {"transcription": {"$regex": query_text, "$options": "i"}}
                ]
            }
        
        total_documents = self.collection.count_documents(query_filter)
        total_pages = (total_documents + self.page_size - 1) // self.page_size
        
        if self.page < 0: self.page = 0
        if self.page >= total_pages and total_pages > 0: self.page = total_pages - 1
        if total_pages == 0: self.page = 0

        cursor = self.collection.find(query_filter).sort("timestamp", -1).skip(self.page * self.page_size).limit(self.page_size)
        
        self.result_list.clear()
        self.current_page_results = []

        for doc in cursor:
            self.current_page_results.append(doc)
            name = doc.get("name", doc.get("nombre", "Sin nombre")) # Check for 'name' or 'nombre'
            timestamp_raw = doc.get("timestamp", doc.get("fecha_subida", None)) # Check for 'timestamp' or 'fecha_subida'
            mode = doc.get("mode", "monologo") # Default mode for older entries

            # Formatear la fecha para la visualización en la lista
            formatted_timestamp = "Fecha inválida"
            if isinstance(timestamp_raw, datetime):
                formatted_timestamp = timestamp_raw.strftime("%Y-%m-%d %H:%M")

            item_text = f"[{formatted_timestamp}] - {name} ({mode.capitalize()})"
            item = QListWidgetItem(item_text)
            self.result_list.addItem(item)

        self.prev_button.setEnabled(self.page > 0)
        self.next_button.setEnabled(self.page < total_pages - 1)
        self.page_label.setText(f"Página {self.page + 1} de {total_pages if total_pages > 0 else 1}")

    def next_page(self):
        self.page += 1
        self.load_transcriptions()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.load_transcriptions()

    def show_details(self, item):
        index = self.result_list.row(item)
        if 0 <= index < len(self.current_page_results):
            doc = self.current_page_results[index]
            
            # Asegurarse de usar los nombres de campo correctos
            name = doc.get("name", doc.get("nombre", "Sin nombre"))
            transcription_text = doc.get("transcription", doc.get("texto", "Sin texto")) # Usar "transcription"
            timestamp_raw = doc.get("timestamp", doc.get("fecha_subida", None))
            language = doc.get("language", "es")
            mode = doc.get("mode", "monologo")

            # Crear un objeto ficticio para DetailWindow si no se usa un modelo de datos real
            class TempTranscription:
                def __init__(self, name, text, timestamp, language, mode):
                    self.name = name
                    self.text = text
                    self.timestamp = timestamp
                    self.language = language
                    self.mode = mode
            
            transcription_obj = TempTranscription(name, transcription_text, timestamp_raw, language, mode)
            
            self.detail_window = DetailWindow(self, transcription_data=doc) # Pasar el diccionario completo
            self.detail_window.show()

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MongoDBViewer()
    viewer.show()
    sys.exit(app.exec())