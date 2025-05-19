# Product Society Chatbot

Ein Telegram-Chatbot für Product Society, der Produktentwicklungsanfragen über einen interaktiven Fragebogen erfasst und Fragen über das Unternehmen beantwortet.

## Features

### 1. Unternehmens-Chatbot
- Beantwortet Fragen über Product Society
- Verwendet ein LLM (Meta-Llama-3-8B-Instruct) für natürliche Antworten
- Nutzt Retrieval-Augmented Generation (RAG) für kontextbezogene Antworten

### 2. Automatischer Fragebogen
- Startet automatisch bei neuen Chat-Sitzungen
- Erfasst detaillierte Produktentwicklungsanfragen
- Unterstützt verschiedene Fragetypen (Text, Auswahl, Datum, Zahlen)
- Kann manuell mit `/questionnaire` gestartet werden

### 3. PDF-Erstellung und E-Mail-Versand
- Generiert automatisch eine PDF-Zusammenfassung der Antworten
- Sendet die PDF per E-Mail an eine konfigurierte Adresse
- Löscht temporäre Dateien nach der Verarbeitung

## Installation

1. Clone Repository
   ```
   git clone https://github.com/avaonlycode/PS_Chatbot.git
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
6. Download Modell:
   ```
   python scripts/download_model.py
   ```
7. Create Index:
   ```
   python scripts/build_index.py
   ```

## Verwendung

1. Start Bot:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```
4. Runpod mit Telegramm Bot Connecten
   ```
   curl -X POST "https://api.telegram.org/BotID/setWebhook" \
     -d url=https://RunPod_ID-Port.proxy.runpod.net/webhook
   ```
   replace BotID and RunPod_ID with the right ids
## Fragebogen-Struktur

5. Umgebungsvariablen konfigurieren (Once the Email server is on):
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_token
   HUGGINGFACE_HUB_TOKEN=your_huggingface_token
   EMAIL_SENDER=your_email@example.com
   EMAIL_PASSWORD=your_email_password
   EMAIL_RECIPIENT=ps@society.de
   ```

Der Fragebogen ist in folgende Abschnitte unterteilt:
1. Product Development Request
2. Customer Profile
3. Packaging
4. Formula Profile
5. Benchmark
6. Regulatory
7. Sampling Instructions
8. Additional Comments

## Konfiguration

Die Fragen können in der Datei `app/data/questions.json` angepasst werden.
E-Mail-Einstellungen können in `app/config.py` oder über Umgebungsvariablen konfiguriert werden.

#### Logs anzeigen
```bash
sudo supervisorctl tail -f ps_chatbot
```

#### Anwendung aktualisieren
```bash
cd /opt/ps_chatbot
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart ps_chatbot
```

### Fehlerbehebung

#### Bot startet nicht
- Überprüfen Sie die Logs: `sudo supervisorctl tail -f ps_chatbot`
- Stellen Sie sicher, dass alle Umgebungsvariablen korrekt gesetzt sind
- Prüfen Sie, ob das Modell korrekt heruntergeladen wurde

#### PDF-Generierung funktioniert nicht
- Stellen Sie sicher, dass die ReportLab- und PyPDF2-Bibliotheken korrekt installiert sind
- Überprüfen Sie die Berechtigungen für das Verzeichnis `app/data/generated_pdfs`

#### E-Mail-Versand schlägt fehl
- Prüfen Sie die SMTP-Einstellungen
- Bei Gmail: Aktivieren Sie "Weniger sichere Apps" oder verwenden Sie App-Passwörter
- Überprüfen Sie die Firewall-Einstellungen für ausgehenden SMTP-Verkehr 
