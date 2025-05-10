from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, Filters
from fastapi import Request
from .llm import get_pipeline
from .config import TELEGRAM_TOKEN

bot = Bot(token=TELEGRAM_TOKEN)
dp  = Dispatcher(bot, None, workers=0)
llm = get_pipeline()

def chat_handler(update: Update, context):
    user_text = update.message.text
    resp = llm(user_text, max_new_tokens=128)[0]["generated_text"]
    update.message.reply_text(resp)

dp.add_handler(MessageHandler(Filters.text & ~Filters.command, chat_handler))

async def handle_webhook(request: Request):
    data   = await request.json()
    update = Update.de_json(data, bot)
    dp.process_update(update)
    return {"ok": True}