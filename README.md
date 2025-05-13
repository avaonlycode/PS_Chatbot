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

1. Repository klonen
2. Abhängigkeiten installieren:
   ```
   pip install -r requirements.txt
   ```
3. Umgebungsvariablen konfigurieren:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_token
   HUGGINGFACE_HUB_TOKEN=your_huggingface_token
   EMAIL_SENDER=your_email@example.com
   EMAIL_PASSWORD=your_email_password
   EMAIL_RECIPIENT=ps@society.de
   ```
4. Model Downloaden:
   ```
   python scripts/download_model.py
   ```

## Verwendung

1. Bot starten:
   ```
   uvicorn app.main:app
   ```
2. Webhook für Telegram einrichten oder mit Polling starten
3. Bot im Telegram-Chat mit `/start` starten
4. Runpod mit Telegramm Bot Connecten
   ```
   curl -X POST "https://api.telegram.org/bot7914580183:AAGgOiqMCLrLtAu1MAAfL22cz3Bweglv0H4/setWebhook" \
     -d url=https://RunPod_ID-Port.proxy.runpod.net/webhook
   ```

## Fragebogen-Struktur

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

## Server-Installation und Deployment

### Voraussetzungen
- Linux-Server (Ubuntu/Debian empfohlen)
- Python 3.8 oder höher
- Pip (Python-Paketmanager)
- Nginx (für Reverse Proxy)
- Supervisor oder systemd (für Prozessverwaltung)

### Schritt-für-Schritt-Anleitung

#### 1. Server vorbereiten
```bash
# System-Pakete aktualisieren
sudo apt update && sudo apt upgrade -y

# Benötigte Pakete installieren
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git
```

#### 2. Projektverzeichnis erstellen und Repository klonen
```bash
# Verzeichnis erstellen
mkdir -p /opt/ps_chatbot
cd /opt/ps_chatbot

# Repository klonen
git clone https://github.com/yourusername/PS_Chatbot.git .
```

#### 3. Python-Umgebung einrichten
```bash
# Virtuelle Umgebung erstellen
python3 -m venv venv

# Umgebung aktivieren
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# PyTorch mit CUDA-Unterstützung installieren (optional, für GPU-Beschleunigung)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 4. Umgebungsvariablen konfigurieren
```bash
# .env-Datei erstellen
cat > .env << EOL
TELEGRAM_BOT_TOKEN=your_telegram_token
HUGGINGFACE_HUB_TOKEN=your_huggingface_token
EMAIL_SENDER=your_email@example.com
EMAIL_PASSWORD=your_email_password
EMAIL_RECIPIENT=ps@society.de
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
HF_CACHE_DIR=/opt/ps_chatbot/models
EOL
```

#### 5. Modell herunterladen
```bash
# Umgebungsvariablen laden
export $(cat .env | xargs)

# Modell herunterladen
python -m scripts.download_model
```

#### 6. Index erstellen
```bash
# Stellen Sie sicher, dass die Daten vorhanden sind
mkdir -p app/data

# Index erstellen
python -m scripts.build_index
```

#### 7. Supervisor-Konfiguration erstellen
```bash
sudo cat > /etc/supervisor/conf.d/ps_chatbot.conf << EOL
[program:ps_chatbot]
command=/opt/ps_chatbot/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
directory=/opt/ps_chatbot
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
environment=
    TELEGRAM_BOT_TOKEN="%(ENV_TELEGRAM_BOT_TOKEN)s",
    HUGGINGFACE_HUB_TOKEN="%(ENV_HUGGINGFACE_HUB_TOKEN)s",
    EMAIL_SENDER="%(ENV_EMAIL_SENDER)s",
    EMAIL_PASSWORD="%(ENV_EMAIL_PASSWORD)s",
    EMAIL_RECIPIENT="%(ENV_EMAIL_RECIPIENT)s",
    SMTP_SERVER="%(ENV_SMTP_SERVER)s",
    SMTP_PORT="%(ENV_SMTP_PORT)s",
    HF_CACHE_DIR="%(ENV_HF_CACHE_DIR)s"
EOL

# Supervisor aktualisieren
sudo supervisorctl reread
sudo supervisorctl update
```

#### 8. Nginx als Reverse Proxy konfigurieren
```bash
sudo cat > /etc/nginx/sites-available/ps_chatbot << EOL
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Nginx-Konfiguration aktivieren
sudo ln -s /etc/nginx/sites-available/ps_chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 9. Telegram-Webhook einrichten
```bash
# Webhook für Telegram einrichten (ersetze YOUR_DOMAIN durch deine Domain)
curl -F "url=https://your-domain.com/webhook" https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook
```

#### 10. SSL mit Certbot einrichten (empfohlen)
```bash
# Certbot installieren
sudo apt install -y certbot python3-certbot-nginx

# SSL-Zertifikat einrichten
sudo certbot --nginx -d your-domain.com
```

### Wartung und Updates

#### Bot neustarten
```bash
sudo supervisorctl restart ps_chatbot
```

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
