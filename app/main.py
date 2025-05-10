from fastapi import FastAPI
from .bot import handle_webhook
from .config import CACHE_DIR

app = FastAPI()

# Optional Health-Endpoint
@app.get("/health")
def health():
    return {"status":"ok", "model_cache": CACHE_DIR}

# Telegram-Webhook-Endpoint
@app.post("/webhook")
async def webhook(request):
    return await handle_webhook(request)