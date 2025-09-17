import os
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configura la clave API de Google Gemini desde variables de entorno
GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')
if not GOOGLE_AI_API_KEY:
    raise ValueError("GOOGLE_AI_API_KEY no está configurada en el archivo .env")

genai.configure(api_key=GOOGLE_AI_API_KEY)

# def list_gemini_models():
#     print("DEBUG: Listando modelos disponibles de Google Generative AI:")
#     for m in genai.list_models():
#         if "generateContent" in m.supported_generation_methods:
#             print(f"  Nombre: {m.name}, Métodos soportados: {m.supported_generation_methods}")

# # Llamar a la función al inicio para depuración
# list_gemini_models()

def obtener_respuesta(mensaje):
    modelo = genai.GenerativeModel("gemini-1.5-flash") # Usar la referencia completa
    respuesta = modelo.generate_content(mensaje)
    return respuesta.text  # Extrae la respuesta generada
