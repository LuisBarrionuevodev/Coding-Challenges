import os
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# ==============================
# CONFIGURACIÓN
# ==============================
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
LABEL_NAME = "contestaciones oficios"
OUTPUT_FILE = "mails_oficio.xlsx"

# ==============================
# AUTENTICACIÓN
# ==============================
creds = None
if os.path.exists("token.pkl"):
    with open("token.pkl", "rb") as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
    with open("token.pkl", "wb") as token:
        pickle.dump(creds, token)

# ==============================
# CONEXIÓN A GMAIL
# ==============================
service = build("gmail", "v1", credentials=creds)

# Buscar la etiqueta contestaciones oficios
results = service.users().labels().list(userId="me").execute()
labels = results.get("labels", [])
label_id = None
for lbl in labels:
    if lbl["name"].lower() == LABEL_NAME.lower():
        label_id = lbl["id"]

if not label_id:
    print(f"❌ No encontré la etiqueta '{LABEL_NAME}' en tu Gmail.")
    exit()

# Buscar mensajes con esa etiqueta
results = service.users().messages().list(userId="me", labelIds=[label_id]).execute()
messages = results.get("messages", [])
total = len(messages)
print(f"📩 Total de mails encontrados: {total}")

# ==============================
# PROCESAR MENSAJES
# ==============================
data = []
for i, msg in enumerate(messages, start=1):
    print(f"Procesando {i}/{total}...")  # progreso
    txt = service.users().messages().get(userId="me", id=msg["id"]).execute()
    headers = txt["payload"]["headers"]

    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
    sender = next((h["value"] for h in headers if h["name"] == "From"), "")
    date = next((h["value"] for h in headers if h["name"] == "Date"), "")

    data.append({"Fecha": date, "De": sender, "Asunto": subject})

# Guardar en Excel
df = pd.DataFrame(data)
df.to_excel(OUTPUT_FILE, index=False)
print(f"✅ Exportado a {OUTPUT_FILE}")
