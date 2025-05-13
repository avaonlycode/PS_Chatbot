from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import json
import os
import sys

def main():
    # Prüfe, ob das Datenverzeichnis existiert
    data_dir = Path("app/data")
    if not data_dir.exists():
        print(f"❌ Datenverzeichnis {data_dir} existiert nicht!", file=sys.stderr)
        sys.exit(1)
        
    # Prüfe, ob Markdown-Dateien vorhanden sind
    md_files = list(data_dir.glob("*.md"))
    if not md_files:
        print(f"❌ Keine Markdown-Dateien im Verzeichnis {data_dir} gefunden!", file=sys.stderr)
        sys.exit(1)
    
    print(f"🔍 Lade Sentence-Transformer...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    
    print(f"📄 Verarbeite {len(md_files)} Markdown-Dateien...")
    texts = []
    for md in md_files:
        print(f"  - {md.name}")
        chunk = md.read_text().split("\n\n")  # einfache Chunks
        for part in chunk:
            if part.strip():  # Leere Chunks überspringen
                texts.append({"text": part, "meta": str(md)})
    
    print(f"🔢 Erstelle Embeddings für {len(texts)} Textabschnitte...")
    embeddings = embedder.encode([t["text"] for t in texts])
    
    print(f"📊 Erstelle FAISS-Index...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    # Speicherung
    index_path = data_dir / "company.index"
    texts_path = data_dir / "company_texts.json"
    
    print(f"💾 Speichere Index in {index_path}...")
    faiss.write_index(index, str(index_path))
    
    print(f"💾 Speichere Texte in {texts_path}...")
    with open(texts_path, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Index-Erstellung abgeschlossen! {len(texts)} Textabschnitte indiziert.")

if __name__ == "__main__":
    main()