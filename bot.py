from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
from typing import Optional
from pywa import WhatsApp
import uvicorn
import requests
import PyPDF2

print("=== BOT STARTED ===")

# ================= CONFIG =================
PHONE_ID = "YOUR_PHONE_ID"
PERMANENT_TOKEN = "YOUR_PERMANENT_TOKEN"
VERIFY_TOKEN = "shreya-contract-bot-2026"

# ================= FASTAPI =================
app = FastAPI()

# ================= WHATSAPP CLIENT =================
wa = WhatsApp(
    phone_id=PHONE_ID,
    token=PERMANENT_TOKEN,
)

print("=== WhatsApp Client Ready ===")


# ================= WEBHOOK VERIFICATION =================
@app.get("/webhook")
async def verify_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        print("Webhook verified")
        return PlainTextResponse(hub_challenge)

    return PlainTextResponse("Verification failed", status_code=403)


# ================= DOWNLOAD FILE FROM WHATSAPP =================
def download_whatsapp_file(media_id):

    url = f"https://graph.facebook.com/v19.0/{media_id}"

    headers = {
        "Authorization": f"Bearer {PERMANENT_TOKEN}"
    }

    res = requests.get(url, headers=headers)
    media_url = res.json()["url"]

    file_data = requests.get(media_url, headers=headers)

    filename = "contract.pdf"

    with open(filename, "wb") as f:
        f.write(file_data.content)

    return filename


# ================= EXTRACT TEXT FROM PDF =================
def extract_pdf_text(file_path):

    text = ""

    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            text += page.extract_text()

    return text


# ================= SIMPLE CONTRACT ANALYSIS =================
def analyze_contract(text):

    risks = []

    keywords = {
        "penalty": "⚠️ Penalty clause detected",
        "termination": "⚠️ Early termination clause",
        "deposit": "⚠️ Deposit condition found",
        "liability": "⚠️ Liability clause present",
        "payment": "⚠️ Payment obligation clause"
    }

    for word in keywords:
        if word in text.lower():
            risks.append(keywords[word])

    if not risks:
        return "✅ No major risky clauses detected."

    return "\n".join(risks)


# ================= RECEIVE MESSAGES =================
@app.post("/webhook")
async def receive_webhook(request: Request):

    data = await request.json()
    print("Incoming webhook event:")
    print(data)

    try:
        entry = data["entry"][0]
        change = entry["changes"][0]
        value = change["value"]

        if "messages" in value:

            message = value["messages"][0]
            phone = message["from"]
            msg_type = message["type"]

            # TEXT MESSAGE
            if msg_type == "text":

                wa.send_message(
                    to=phone,
                    text="👋 Hello! Send me a PDF contract and I will analyze it."
                )

            # DOCUMENT MESSAGE
            elif msg_type == "document":

                doc = message["document"]
                media_id = doc["id"]
                filename = doc.get("filename", "contract.pdf")

                print("Downloading document:", filename)

                wa.send_message(
                    to=phone,
                    text="📄 Contract received. Downloading and analyzing..."
                )

                # Download file
                file_path = download_whatsapp_file(media_id)

                # Extract text
                text = extract_pdf_text(file_path)

                # Analyze contract
                result = analyze_contract(text)

                # Send result
                wa.send_message(
                    to=phone,
                    text=f"📊 Contract Analysis Result:\n\n{result}"
                )

    except Exception as e:
        print("Error:", e)

    return {"status": "ok"}


print("=== Bot Ready ===")

# ================= RUN SERVER =================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

https://grok.com/share/bGVnYWN5_6f9fa9e9-995b-42c3-9599-5cc9c6b9418b




from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from groq import Groq
import PyPDF2
import requests
import os
import asyncio

# ================= CONFIG =================

TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
GROQ_API_KEY = "YOUR_GROQ_API_KEY"

client = Groq(api_key=GROQ_API_KEY)

app = FastAPI()

# ================= PDF EXTRACTION =================

def extract_pdf_text(file_path):
    text = ""

    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


# ================= GROQ ANALYSIS =================

def analyze_contract_with_groq(contract_text):

    prompt = f"""
You are an expert legal contract reviewer.

Analyze the contract below and identify:

1. Risky clauses
2. Penalties
3. Liability issues
4. Payment obligations
5. Termination conditions
6. Missing protections

Give the result in simple bullet points.

Contract:

{contract_text[:12000]}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


# ================= START COMMAND =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 Hello!\n\nSend me a PDF contract and I will analyze it using AI."
    )


# ================= PDF HANDLER =================

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    if not document.file_name.lower().endswith(".pdf"):
        await update.message.reply_text(
            "❌ Please send a PDF file."
        )
        return

    await update.message.reply_text(
        "📄 Contract received.\nAnalyzing..."
    )

    file = await context.bot.get_file(document.file_id)

    file_path = f"downloads/{document.file_name}"

    os.makedirs("downloads", exist_ok=True)

    await file.download_to_drive(file_path)

    contract_text = extract_pdf_text(file_path)

    result = analyze_contract_with_groq(contract_text)

    if len(result) > 4000:
        result = result[:3900] + "\n\n...(truncated)"

    await update.message.reply_text(
        f"📊 Contract Analysis\n\n{result}"
    )


# ================= TELEGRAM APP =================

telegram_app = Application.builder().token(
    TELEGRAM_BOT_TOKEN
).build()

telegram_app.add_handler(
    CommandHandler("start", start)
)

telegram_app.add_handler(
    MessageHandler(
        filters.Document.PDF,
        handle_document
    )
)


# ================= FASTAPI STARTUP =================

@app.on_event("startup")
async def startup():

    asyncio.create_task(
        telegram_app.initialize()
    )

    asyncio.create_task(
        telegram_app.start()
    )


@app.get("/")
def home():
    return {"status": "Telegram Contract Analyzer Running"}


# ================= MAIN =================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
