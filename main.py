import sys
import os
from pathlib import Path

# Agregar el directorio src al path para imports
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Configurar variables de entorno
config_path = project_root / "config" / ".env"
if config_path.exists():
    from dotenv import load_dotenv
    load_dotenv(config_path)

def main():
    """Función principal de la aplicación."""
    try:
        # Imports absolutos desde src
        from ui.main_window import MainWindow
        from PySide6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        app.setApplicationName("AI Transcriptor")
        app.setApplicationVersion("2.0.0")
        
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"Error al importar módulos: {e}")
        print("Asegúrate de que todas las dependencias estén instaladas.")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
