import logging
from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from mangum import Mangum
from app.handlers import process_incoming_message_hybrid

# Load env vars for local dev
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="WhatsApp Bot API",
    description="Receives WhatsApp messages via Twilio and replies "
                "with a true/false prediction.",
    version="1.0.0",
)

@app.post("/webhook", response_class=PlainTextResponse)
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    logger.info(f"Incoming message from {From}: {Body}")

    # Run the processing program
    reply_text = process_incoming_message_hybrid(Body)

    logger.info(f"Replying with: {reply_text}")
    return PlainTextResponse(content=reply_text)

# AWS Lambda entrypoint
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI app locally...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
