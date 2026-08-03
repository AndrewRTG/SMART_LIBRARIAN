import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# Calea către fișierul .env din folderul curent al proiectului
env_path = Path(__file__).parent / ".env"

if not env_path.exists():
    raise FileNotFoundError(
        f"Fișierul .env nu a fost găsit la: {env_path}"
    )

load_dotenv(dotenv_path=env_path)

api_key = os.getenv("ENDAVA_OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "ENDAVA_OPENAI_API_KEY nu a fost găsită în fișierul .env."
    )

# Nu afișăm cheia; verificăm doar dacă a fost încărcată.
print("Cheia API a fost încărcată din fișierul .env.")

client = OpenAI(api_key=api_key)

try:
    models = client.models.list()
    print("Conectarea la OpenAI API a reușit.")
    print("Cheia API este validă.")
except Exception as error:
    print("Conectarea la OpenAI API a eșuat.")
    print(f"Tip eroare: {type(error).__name__}")
    print(f"Mesaj: {error}")