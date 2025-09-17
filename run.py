import sys
import os
from pathlib import Path

def main():
    """Función principal alternativa."""
    # Agregar src al path
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    
    # Cargar configuración
    config_path = project_root / "config" / ".env"
    if config_path.exists():
        from dotenv import load_dotenv
        load_dotenv(config_path)
    
    try:
        from PySide6.QtWidgets import QApplication
        from ui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName("AI Transcriptor")
        app.setApplicationVersion("2.0.0")
        
        window = MainWindow()
        window.show()
        
        print("🚀 AI Transcriptor iniciado correctamente")
        print("📱 Interfaz gráfica abierta")
        
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Soluciones:")
        print("   1. Asegúrate de que el entorno virtual esté activado")
        print("   2. Ejecuta: pip install -r requirements.txt")
        print("   3. Verifica que config/.env esté configurado")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
