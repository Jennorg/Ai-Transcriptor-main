# AI Transcriptor

Una aplicación de transcripción de audio a texto con interfaz gráfica desarrollada en Python, que utiliza AssemblyAI para la transcripción y Google Generative AI para funcionalidades de chat.

## 🚀 Características

- **Grabación de Audio**: Graba audio directamente desde el micrófono
- **Transcripción Automática**: Convierte audio a texto usando AssemblyAI
- **Almacenamiento en Base de Datos**: Guarda las transcripciones en MongoDB
- **Exportación**: Exporta transcripciones como PDF o archivos de texto
- **Chat con IA**: Funcionalidad de chat usando Google Generative AI
- **Interfaz Gráfica**: Interfaz intuitiva desarrollada con PySide6
- **Soporte para Español**: Configurado para transcripciones en español
- **Arquitectura Escalable**: Estructura de carpetas profesional y modular

## 📁 Estructura del Proyecto

```
Ai-Transcriptor-main/
├── main.py                     # Punto de entrada principal
├── src/                        # Código fuente principal
│   ├── core/                   # Lógica central
│   │   ├── config.py          # Configuración centralizada
│   │   └── audio_recorder.py  # Grabación y transcripción
│   ├── ui/                     # Interfaz de usuario
│   │   ├── main_window.py     # Ventana principal
│   │   └── transcription_viewer.py  # Visor de transcripciones
│   ├── services/               # Servicios externos
│   │   ├── ai_service.py      # Google Generative AI
│   │   └── database_manager.py # MongoDB
│   ├── utils/                  # Utilidades
│   │   └── export_utils.py    # Exportación
│   └── models/                 # Modelos de datos
│       └── transcription.py   # Modelo de transcripción
├── config/                     # Configuración
│   ├── .env                   # Variables de entorno
│   └── .env.example          # Plantilla
├── assets/                     # Recursos
│   ├── images/                # Iconos
│   ├── audio/                 # Archivos de audio
│   └── exports/               # Archivos exportados
├── tests/                      # Pruebas
├── docs/                       # Documentación
└── requirements.txt            # Dependencias
```

## 🛠️ Instalación

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd Ai-Transcriptor-main
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # En Linux/macOS
# o
venv\Scripts\activate     # En Windows
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```bash
# Copiar plantilla
cp config/.env.example config/.env

# Editar con tus API keys
nano config/.env
```

## 🔐 Configuración de Variables de Entorno

### Variables Disponibles

```env
# API Keys
ASSEMBLYAI_API_KEY=tu_assemblyai_api_key_aqui
GOOGLE_AI_API_KEY=tu_google_ai_api_key_aqui

# MongoDB
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/
MONGODB_DATABASE_NAME=ai_transcriptor
MONGODB_COLLECTION_NAME=transcriptions

# Configuración de la aplicación
DEFAULT_LANGUAGE=es
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
```

### Obtener API Keys

#### AssemblyAI

1. Ve a [AssemblyAI](https://www.assemblyai.com/)
2. Crea una cuenta gratuita
3. Copia tu API key desde el dashboard
4. Pégala en el archivo `config/.env`

#### Google Generative AI

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una API key
3. Pégala en el archivo `config/.env`

## 🎯 Uso

### Ejecutar la Aplicación

```bash
# Método recomendado (nueva estructura)
python main.py
# O alternativamente:
python run.py

# Método alternativo (estructura anterior)
python src/ui/main_window.py
```

### Funcionalidades Principales

1. **Grabar Audio**

   - Haz clic en el botón de grabación
   - Habla al micrófono
   - Detén la grabación cuando termines

2. **Transcribir Audio**

   - La transcripción se realiza automáticamente
   - El texto aparecerá en la interfaz

3. **Guardar Transcripción**

   - Las transcripciones se guardan automáticamente en MongoDB
   - También puedes exportar como PDF o TXT

4. **Ver Historial**

   - Accede al historial de transcripciones
   - Filtra y busca transcripciones anteriores

5. **Chat con IA**
   - Interactúa con las transcripciones usando IA
   - Obtén resúmenes, análisis o respuestas

## 📦 Dependencias

### Python Packages

- `sounddevice` - Grabación de audio
- `wavio` - Manejo de archivos de audio
- `assemblyai` - Servicio de transcripción
- `PySide6` - Interfaz gráfica
- `pymongo` - Cliente de MongoDB
- `numpy` - Operaciones numéricas
- `fpdf2` - Generación de PDFs
- `google-generativeai` - API de Google Generative AI
- `python-dotenv` - Manejo de variables de entorno

### Dependencias del Sistema

- `portaudio19-dev` - Biblioteca de audio
- `python3-pyaudio` - Bindings de Python para PortAudio

## 🔧 Solución de Problemas

### Error: "PortAudio library not found"

```bash
# Instalar PortAudio
sudo apt install -y portaudio19-dev python3-pyaudio

# Reinstalar sounddevice
pip uninstall sounddevice -y
pip install sounddevice
```

### Error: "ModuleNotFoundError"

```bash
# Instalar todas las dependencias
pip install -r requirements.txt
```

### Problemas con la Interfaz Gráfica

- Asegúrate de tener un servidor X11 ejecutándose (Linux)
- En Windows, instala Microsoft Visual C++ Redistributable

### Problemas de Audio

- Verifica que el micrófono esté conectado y funcionando
- Comprueba los permisos de audio en tu sistema
- En Linux, asegúrate de que el usuario esté en el grupo `audio`

## 🚨 Advertencias

- Las advertencias de QPainter en la consola son normales y no afectan la funcionalidad
- Asegúrate de tener una conexión a internet para usar AssemblyAI y Google Generative AI
- Las API keys son sensibles, no las compartas públicamente

## 📝 Notas de Desarrollo

- La aplicación está configurada para transcripciones en español
- Se puede modificar el idioma en la configuración
- La interfaz es responsive y se adapta a diferentes tamaños de pantalla
- Arquitectura modular permite fácil extensión y mantenimiento

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa la sección de solución de problemas
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

---

**Desarrollado con ❤️ usando Python, PySide6, AssemblyAI y Google Generative AI**
