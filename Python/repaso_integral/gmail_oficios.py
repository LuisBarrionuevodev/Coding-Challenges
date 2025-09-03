import os
import pickle
import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

# Cargar variables del .env
load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
auth_uri = os.getenv("GOOGLE_AUTH_URI")
token_uri = os.getenv("GOOGLE_TOKEN_URI")

config = {
    "installed": {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uris": [redirect_uri],
        "auth_uri": auth_uri,
        "token_uri": token_uri,
    }
}

# --- Autenticación ---
if os.path.exists("token.pickle"):
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)
else:
    flow = InstalledAppFlow.from_client_config(config, SCOPES)
    creds = flow.run_local_server(port=0)
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

service = build("gmail", "v1", credentials=creds)

print("✅ Autenticación exitosa con Gmail API")


# --- Obtener TODOS los mensajes con la etiqueta ---
query = "label:contestaciones-oficios"
results = []
page_token = None

while True:
    response = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=100,
        pageToken=page_token
    ).execute()

    if "messages" in response:
        results.extend(response["messages"])

    page_token = response.get("nextPageToken")
    if not page_token:
        break

total = len(results)
print(f"✅ Total mails encontrados: {total}")

# --- Procesar cada mail ---
data_list = []

for i, msg in enumerate(results, start=1):
    m = service.users().messages().get(userId="me", id=msg["id"]).execute()
    headers = m["payload"]["headers"]

    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
    from_ = next((h["value"] for h in headers if h["name"] == "From"), "")
    date_ = next((h["value"] for h in headers if h["name"] == "Date"), "")

    data_list.append({"Asunto": subject, "De": from_, "Fecha": date_})

    # --- Progreso en consola ---
    print(f"📨 Procesado {i}/{total} -> {subject[:50]}...")

# --- Guardar en Excel ---
df = pd.DataFrame(data_list)
df.to_excel("contestaciones_oficios.xlsx", index=False)

print("\n📂 Archivo 'contestaciones_oficios.xlsx' generado correctamente.")
