#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from huggingface_hub import snapshot_download
import requests

def main():
    # 1) Einlesen der Umgebungsvariablen
    model_name    = os.getenv("MODEL_NAME", "NousResearch/Meta-Llama-3.1-8B-Instruct")
    hf_token      = os.getenv("HUGGINGFACE_HUB_TOKEN")
    hf_cache_root = os.getenv("HF_CACHE_DIR", "/workspace/models/cache")
    local_root    = os.getenv("HF_CACHE_DIR", "/workspace/models")

    if not hf_token:
        print("❌ Bitte setze HUGGINGFACE_HUB_TOKEN mit einem gültigen Token.", file=sys.stderr)
        sys.exit(1)

    # 2) Zielverzeichnis für das Modell
    safe_name = model_name.replace("/", "_")
    local_dir = Path(local_root) / safe_name
    local_dir.mkdir(parents=True, exist_ok=True)
    print(f"Modell: {model_name}")

    print(f"➡️  Lade Modell {model_name} nach {local_dir} …")
    try:
        snapshot_download(
            repo_id=model_name,
            cache_dir=hf_cache_root,           
            local_dir=str(local_dir),          
            local_dir_use_symlinks=False,
            resume_download=True,
            token=hf_token
        )
    except requests.exceptions.HTTPError as e:
        print("❌ HTTP-Fehler beim Download:", e, file=sys.stderr)
        print(
            "• Prüfe, ob dein Token Leserechte hat und der Repo-Name korrekt ist.",
            "• Falls das Modell gated ist, öffne im Browser https://huggingface.co/"
            f"{model_name} und akzeptiere dort die Lizenzbedingungen.",
            file=sys.stderr
        )
        sys.exit(1)
    except Exception as e:
        print("❌ Unerwarteter Fehler:", e, file=sys.stderr)
        sys.exit(1)

    print("✅ Download abgeschlossen!")

if __name__ == "__main__":
    main()
