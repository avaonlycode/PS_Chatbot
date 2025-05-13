from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters
)
from fastapi import Request
from .config import TELEGRAM_TOKEN
from .llm import get_pipeline, generate_answer

import faiss, json
from sentence_transformers import SentenceTransformer


embedder = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("app/data/company.index")
with open("app/data/company_texts.json","r",encoding="utf-8") as f:
    TEXTS = json.load(f)

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
llm = get_pipeline()

def retrieve_context(query, k=3):
    q_emb = embedder.encode([query])
    D, I = index.search(q_emb, k)
    return "\n\n".join(TEXTS[i]["text"] for i in I[0])


async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    context_snippet = retrieve_context(user_text, k=3)
    prompt = (
        "You are a company chatbot for Product Society. "
        "Answer exclusively questions about Product Society using a professional, friendly, and detailed style!\n\n"
        "### Relevant company texts:\n"
        f"{context_snippet}\n\n"
        "### Question:\n"
        f"{user_text}\n\n"
        "### Answer:"
    )
    answer = generate_answer(prompt, max_new_tokens=256)
    await update.message.reply_text(answer)

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

initialized = False

async def handle_webhook(request: Request):
    global initialized
    if not initialized:
        await application.initialize()
        initialized = True

    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}