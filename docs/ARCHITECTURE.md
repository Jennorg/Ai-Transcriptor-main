# Arquitectura del Proyecto AI Transcriptor

## Estructura de Directorios

```
Ai-Transcriptor-main/
├── main.py                     # Punto de entrada principal
├── src/                        # Código fuente principal
│   ├── __init__.py
│   ├── core/                   # Lógica central de la aplicación
│   │   ├── __init__.py
│   │   ├── config.py          # Configuración centralizada
│   │   └── audio_recorder.py  # Grabación y transcripción de audio
│   ├── ui/                     # Interfaz de usuario
│   │   ├── __init__.py
│   │   ├── main_window.py     # Ventana principal
│   │   └── transcription_viewer.py  # Visor de transcripciones
│   ├── services/               # Servicios externos
│   │   ├── __init__.py
│   │   ├── ai_service.py      # Servicio de IA (Google Gemini)
│   │   └── database_manager.py # Gestión de MongoDB
│   ├── utils/                  # Utilidades
│   │   ├── __init__.py
│   │   └── export_utils.py    # Exportación de archivos
│   └── models/                 # Modelos de datos
│       ├── __init__.py
│       └── transcription.py   # Modelo de transcripción
├── config/                     # Configuración
│   ├── .env                   # Variables de entorno
│   └── .env.example          # Plantilla de variables
├── assets/                     # Recursos
│   ├── images/                # Iconos e imágenes
│   ├── audio/                 # Archivos de audio
│   └── exports/               # Archivos exportados
├── tests/                      # Pruebas unitarias
├── docs/                       # Documentación
│   └── ARCHITECTURE.md        # Este archivo
├── requirements.txt            # Dependencias
├── .gitignore                 # Archivos a ignorar
└── README.md                  # Documentación principal
```

## Componentes Principales

### Core (Lógica Central)
- **config.py**: Configuración centralizada y validación
- **audio_recorder.py**: Grabación de audio y transcripción con AssemblyAI

### UI (Interfaz de Usuario)
- **main_window.py**: Ventana principal con todos los controles
- **transcription_viewer.py**: Visor de historial de transcripciones

### Services (Servicios Externos)
- **ai_service.py**: Integración con Google Generative AI
- **database_manager.py**: Operaciones con MongoDB

### Utils (Utilidades)
- **export_utils.py**: Exportación a PDF y TXT

### Models (Modelos de Datos)
- **transcription.py**: Estructura de datos para transcripciones

## Flujo de la Aplicación

1. **Inicio**: `main.py` carga la configuración y lanza la interfaz
2. **Grabación**: Usuario graba audio usando `audio_recorder.py`
3. **Transcripción**: Audio se envía a AssemblyAI para transcripción
4. **Almacenamiento**: Transcripción se guarda en MongoDB
5. **Visualización**: Usuario puede ver historial y exportar transcripciones

## Beneficios de esta Arquitectura

- ✅ **Separación de responsabilidades**: Cada módulo tiene una función específica
- ✅ **Escalabilidad**: Fácil agregar nuevas funcionalidades
- ✅ **Mantenibilidad**: Código organizado y fácil de mantener
- ✅ **Testabilidad**: Cada componente se puede probar independientemente
- ✅ **Reutilización**: Componentes pueden ser reutilizados en otros proyectos
- ✅ **Configuración centralizada**: Todas las configuraciones en un lugar
