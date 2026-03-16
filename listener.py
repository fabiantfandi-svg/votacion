from google import genai
client = genai.Client(api_key="AIzaSyD6D0yPcsdI0-5v3O7Ee64N8fYn1BSL__M")

for m in client.models.list():
    print(f"Modelo disponible: {m.name}")