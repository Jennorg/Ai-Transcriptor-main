import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Función principal de instalación."""
    print("🚀 Instalando AI Transcriptor...")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        sys.exit(1)
    
    print(f"✅ Python {sys.version} detectado")
    
    # Crear entorno virtual si no existe
    venv_path = Path("venv")
    if not venv_path.exists():
        if not run_command("python -m venv venv", "Creando entorno virtual"):
            sys.exit(1)
    
    # Activar entorno virtual e instalar dependencias
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Linux/macOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Instalar dependencias
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Instalando dependencias"):
        sys.exit(1)
    
    # Crear directorios necesarios
    directories = [
        "assets/audio",
        "assets/exports", 
        "assets/images",
        "tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directorio {directory} creado")
    
    # Verificar archivo de configuración
    config_file = Path("config/.env")
    if not config_file.exists():
        example_file = Path("config/.env.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, config_file)
            print("✅ Archivo de configuración creado desde plantilla")
            print("⚠️  IMPORTANTE: Edita config/.env con tus API keys")
        else:
            print("❌ No se encontró el archivo de plantilla de configuración")
    
    print("\n🎉 Instalación completada!")
    print("\n📋 Próximos pasos:")
    print("1. Edita config/.env con tus API keys")
    print("2. Ejecuta: python main.py")
    print("\n📚 Documentación: docs/ARCHITECTURE.md")

if __name__ == "__main__":
    main()
