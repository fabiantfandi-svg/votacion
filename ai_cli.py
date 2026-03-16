import requests
import time
import getpass
from google import genai
from google.genai import types

# --- 1. FUNCIÓN DE LOGIN ---
def login_usuario():
    print("--- 🔑 Login de Administrador/Votante ---")
    email = input("Email: ")
    password = getpass.getpass("Contraseña: ")
    url_login = "http://127.0.0.1:8000/api/auth/login/"
    try:
        response = requests.post(url_login, json={"email": email, "password": password})
        if response.status_code == 200:
            print("✅ Autenticación exitosa.")
            return response.json().get('token')
        print(f"❌ Error: {response.json().get('error')}")
    except Exception as e:
        print(f"⚠️ Error de conexión: {e}")
    return None

# --- 2. HERRAMIENTAS PARA LA IA ---
def consultar_votos():
    """Consulta los votos registrados en la base de datos de Django."""
    print("\n[SISTEMA] 🔍 Consultando API de Django (GET)...")
    url = "http://127.0.0.1:8000/api/votos/"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(url, headers=headers)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def registrar_voto(candidato: str, mesa_id: str = "MESA-05", comentario: str = "Voto emitido con seguridad"):
    """Registra un nuevo voto. Usamos 'candidato' como el valor para 'candidato_id'."""
    print(f"\n[SISTEMA] 🚀 Registrando voto para {candidato}...")
    url = "http://127.0.0.1:8000/api/votos/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # IMPORTANTE: Cambiamos la clave 'candidato' por 'candidato_id'
    # para que coincida con tu estructura de Firestore.
    payload = {
        "candidato_id": candidato, 
        "mesa_id": mesa_id,
        "comentario": comentario
    }
    
    try:
        res = requests.post(url, json=payload, headers=headers)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

# --- 3. CONFIGURACIÓN IA ---
API_KEY = "AIzaSyD6D0yPcsdI0-5v3O7Ee64N8fYn1BSL__M"
client = genai.Client(api_key=API_KEY)
modelo_id = "gemini-2.5-flash"

# --- 4. FLUJO PRINCIPAL ---
token = login_usuario()

if token:
    print("\n🤖 IA: ¡Hola! Soy tu asistente de ADSO. ¿Qué deseas consultar hoy?")
    
    while True:
        user_input = input("\nTú: ")
        if user_input.lower() in ['salir', 'exit', 'bye']: break

        # Instrucción clara para que la IA sepa qué herramienta usar
        prompt = (
            f"Eres un asistente de votaciones. Tienes dos herramientas: consultar_votos y registrar_voto.\n"
            f"Si el usuario quiere votar, usa registrar_voto(candidato='NOMBRE'). "
            f"Los parámetros candidato_id='CAND-001', mesa_id='MESA-05', comentario='Voto emitido' "
            f"son obligatorios, así que úsalos SIEMPRE por defecto si el usuario no los da.\n"
            f"Si el usuario te da un nombre o código, úsalo como 'candidato'.\n"
            f"Pregunta del usuario: {user_input}"
        )

        try:
            # Aquí le pasamos ambas herramientas a la IA
            response = client.models.generate_content(
                model=modelo_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[consultar_votos, registrar_voto]
                )
            )
            print(f"🤖 IA: {response.text}")

        except Exception as e:
            print(f"⚠️ Ups! Algo pasó: {e}")