import os

TELEGRAM_TOKEN    = os.getenv("TELEGRAM_BOT_TOKEN")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_HUB_TOKEN")
MODEL_NAME        = os.getenv("MODEL_NAME", "NousResearch/Meta_Llama-3.1-8B-Instruct")
CACHE_DIR         = os.getenv("HF_CACHE_DIR", "/workspace/models")