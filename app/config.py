import os

TELEGRAM_TOKEN    = os.getenv("TELEGRAM_BOT_TOKEN")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_HUB_TOKEN")
MODEL_NAME        = os.getenv("MODEL_NAME", "NousResearch/Meta-Llama-3-8B-Instruct")
CACHE_DIR         = os.getenv("HF_CACHE_DIR", "/workspace/models")

# E-Mail-Konfiguration
EMAIL_SENDER      = os.getenv("EMAIL_SENDER", "bot@productsociety.com")
EMAIL_PASSWORD    = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECIPIENT   = os.getenv("EMAIL_RECIPIENT", "ps@society.de")
SMTP_SERVER       = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT         = int(os.getenv("SMTP_PORT", "587"))