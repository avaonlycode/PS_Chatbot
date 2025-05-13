from fastapi import FastAPI, Request
from .bot import handle_webhook
from .config import CACHE_DIR

app = FastAPI()


@app.get("/health")
def health():
    return {"status":"ok", "model_cache": CACHE_DIR}

@app.post("/webhook")
async def webhook(request: Request):  # <-- wichtig: Request, nicht dict!
    return await handle_webhook(request)