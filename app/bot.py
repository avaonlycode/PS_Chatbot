from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters
)
from fastapi import Request
from .config import TELEGRAM_TOKEN, EMAIL_RECIPIENT
from .llm import get_pipeline, generate_answer
from .questionnaire import questionnaire_manager

import faiss, json
from sentence_transformers import SentenceTransformer
import logging

# Logger konfigurieren
logger = logging.getLogger(__name__)

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
    chat_id = update.effective_chat.id
    
    # Prüfe, ob ein Fragebogen aktiv ist
    if questionnaire_manager.is_questionnaire_active(chat_id):
        # Verarbeite die Antwort und hole die nächste Frage
        next_question = questionnaire_manager.get_next_question(chat_id, user_text)
        
        if next_question:
            # Wenn es eine weitere Frage gibt, sende sie
            question_text = f"**{next_question.section}**\n{next_question.text}"
            
            # Wenn es Auswahlmöglichkeiten gibt, zeige sie an
            if next_question.type == "choice" and next_question.options:
                options_text = "\n".join([f"- {option}" for option in next_question.options])
                question_text += f"\n\nOptions:\n{options_text}"
                
            await update.message.reply_text(question_text)
            return
        else:
            # Fragebogen ist abgeschlossen
            completion_message = (
                "Thank you for completing the questionnaire! Your responses have been saved.\n\n"
                f"A PDF summary of your responses will be generated and sent to {EMAIL_RECIPIENT}.\n\n"
                "You can now ask questions about Product Society."
            )
            await update.message.reply_text(completion_message)
    
    # Normale Chat-Verarbeitung, wenn kein Fragebogen aktiv ist
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


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wird aufgerufen, wenn ein Benutzer /start sendet"""
    chat_id = update.effective_chat.id
    
    # Begrüßungsnachricht
    welcome_message = (
        "Welcome to the Product Society Chatbot! 👋\n\n"
        "I'm here to help you with information about Product Society and assist with your product development needs.\n\n"
        "Before we start, I'd like to ask you a few questions about your product development request."
    )
    await update.message.reply_text(welcome_message)
    
    # Starte den Fragebogen
    await start_questionnaire(update, context)


async def questionnaire_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manueller Befehl zum Starten des Fragebogens"""
    await update.message.reply_text(
        "Starting the product development questionnaire. "
        "You can cancel at any time by typing /cancel."
    )
    await start_questionnaire(update, context)


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Abbrechen des Fragebogens"""
    chat_id = update.effective_chat.id
    
    if questionnaire_manager.is_questionnaire_active(chat_id):
        # Entferne die aktive Session
        if chat_id in questionnaire_manager.active_sessions:
            del questionnaire_manager.active_sessions[chat_id]
        
        await update.message.reply_text(
            "Questionnaire cancelled. You can restart it anytime with /questionnaire."
        )
    else:
        await update.message.reply_text(
            "No active questionnaire to cancel."
        )


async def start_questionnaire(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hilfsfunktion zum Starten des Fragebogens"""
    chat_id = update.effective_chat.id
    
    # Starte den Fragebogen
    first_question = questionnaire_manager.start_questionnaire(chat_id)
    if first_question:
        question_text = f"**{first_question.section}**\n{first_question.text}"
        
        # Wenn es Auswahlmöglichkeiten gibt, zeige sie an
        if first_question.type == "choice" and first_question.options:
            options_text = "\n".join([f"- {option}" for option in first_question.options])
            question_text += f"\n\nOptions:\n{options_text}"
            
        await update.message.reply_text(question_text)


# Handler registrieren
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("questionnaire", questionnaire_command))
application.add_handler(CommandHandler("cancel", cancel_command))
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