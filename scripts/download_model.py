#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from huggingface_hub import snapshot_download

def main():
    # Einlesen der wichtigen Umgebungsvariablen
    model_name   = os.getenv("MODEL_NAME", "NousResearch/Meta_Llama-3.1-8B-Instruct")
    hf_token     = os.getenv("HUGGINGFACE_HUB_TOKEN")
    cache_dir    = os.getenv("HF_CACHE_DIR", "/workspace/models")

    if hf_token is None:
        print("❌ Bitte setze die Umgebungsvariable HUGGINGFACE_HUB_TOKEN.", file=sys.stderr)
        sys.exit(1)

    # Prepare target path
    model_folder = Path(cache_dir) / model_name.replace("/", "_")
    model_folder.mkdir(parents=True, exist_ok=True)

    print(f"➡️  Downloading {model_name} into {model_folder} …")
    snapshot_download(
        repo_id=model_name,
        cache_dir=str(model_folder),
        token=hf_token,
        resume_download=True,    # bei Abbruch fortsetzen
        local_dir_use_symlinks=False
    )
    print("✅ Download fertig!")

if __name__ == "__main__":
    main()