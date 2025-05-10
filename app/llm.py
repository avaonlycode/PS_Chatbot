from transformers import pipeline
from huggingface_hub import snapshot_download
from .config import MODEL_NAME, HUGGINGFACE_TOKEN, CACHE_DIR
import os

# 1) Pre-download (optional, aber empfehlenswert)
def download_model():
    if not os.path.isdir(os.path.join(CACHE_DIR, MODEL_NAME.replace("/", "_"))):
        snapshot_download(
            repo_id=MODEL_NAME,
            cache_dir=CACHE_DIR,
            token=HUGGINGFACE_TOKEN,
            resume_download=True
        )

# 2) Pipeline-Factory
def get_pipeline():
    download_model()
    return pipeline(
        "text-generation",
        model=os.path.join(CACHE_DIR, MODEL_NAME.replace("/", "_")),
        trust_remote_code=True,
        device=0
    )