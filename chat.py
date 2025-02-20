
#esta es la api key AIzaSyBGoCt7TafHD09OFnc8EcjQ9QOwMdvZtYM

import google.generativeai as genai

# Configura la clave API de Google Gemini
genai.configure(api_key="AIzaSyBGoCt7TafHD09OFnc8EcjQ9QOwMdvZtYM")

def obtener_respuesta(mensaje):
    modelo = genai.GenerativeModel("gemini-pro")
    respuesta = modelo.generate_content(mensaje)
    return respuesta.text  # Extrae la respuesta generada
