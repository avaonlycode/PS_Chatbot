import os
import json
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import logging
from datetime import datetime
from typing import Dict, Optional, Any

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    logging.warning("PDF-Bibliotheken nicht verfügbar. Installiere sie mit: pip install reportlab PyPDF2")

from .config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT, SMTP_SERVER, SMTP_PORT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFHandler:
    def __init__(self):
        self.template_path = Path("app/data/Template.pdf")
        self.output_dir = Path("app/data/generated_pdfs")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
    def generate_pdf(self, responses_file: Path) -> Optional[Path]:
        """Generiert eine PDF aus den Fragebogen-Antworten"""
        try:
            # Lade die Antworten aus der JSON-Datei
            with open(responses_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            chat_id = data.get("chat_id", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"questionnaire_{chat_id}_{timestamp}.pdf"
            
            # Prüfe, ob wir ein Template haben oder eine neue PDF erstellen müssen
            if self.template_path.exists():
                self._fill_template_pdf(data, output_file)
            else:
                self._create_new_pdf(data, output_file)
                
            logger.info(f"PDF erfolgreich erstellt: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Fehler bei der PDF-Erstellung: {e}")
            return None
            
    def _fill_template_pdf(self, data: Dict[str, Any], output_file: Path):
        """Füllt ein PDF-Template mit den Antworten aus"""
        # Hier würde die Logik zum Ausfüllen eines PDF-Templates stehen
        # Da wir keine echte Template-Verarbeitung haben, erstellen wir stattdessen eine neue PDF
        self._create_new_pdf(data, output_file)
            
    def _create_new_pdf(self, data: Dict[str, Any], output_file: Path):
        """Erstellt eine neue PDF mit den Fragebogen-Antworten"""
        doc = SimpleDocTemplate(str(output_file), pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Titel
        title_style = styles["Heading1"]
        title = Paragraph("Product Development Questionnaire", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Metadaten
        elements.append(Paragraph(f"Chat ID: {data.get('chat_id', 'Unknown')}", styles["Normal"]))
        elements.append(Paragraph(f"Completed: {data.get('end_time', 'Unknown')}", styles["Normal"]))
        elements.append(Spacer(1, 24))
        
        # Antworten nach Abschnitten gruppieren
        responses = data.get("responses", {})
        sections = {}
        
        # Lade die Fragen, um die Abschnitte zu ermitteln
        questions_file = Path("app/data/questions.json")
        if questions_file.exists():
            with open(questions_file, "r", encoding="utf-8") as f:
                questions = json.load(f)
                
            # Gruppiere Fragen nach Abschnitten
            for question in questions:
                qid = question["id"]
                section = question["section"]
                text = question["text"]
                
                if qid in responses:
                    if section not in sections:
                        sections[section] = []
                    
                    sections[section].append({
                        "question": text,
                        "answer": responses[qid]
                    })
        
        # Füge die Antworten nach Abschnitten sortiert hinzu
        for section, items in sections.items():
            # Abschnittsüberschrift
            section_style = styles["Heading2"]
            section_title = Paragraph(section, section_style)
            elements.append(section_title)
            elements.append(Spacer(1, 6))
            
            # Tabelle mit Fragen und Antworten
            table_data = [["Question", "Answer"]]
            for item in items:
                table_data.append([item["question"], item["answer"]])
                
            table = Table(table_data, colWidths=[250, 250])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 12))
        
        # Erstelle das PDF-Dokument
        doc.build(elements)
        
    def send_email(self, pdf_file: Path) -> bool:
        """Sendet die PDF per E-Mail"""
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_SENDER
            msg['To'] = EMAIL_RECIPIENT
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = f"Product Development Questionnaire - {pdf_file.stem}"
            
            # E-Mail-Text
            body = "Attached is a completed product development questionnaire.\n\n"
            body += "This email was automatically generated by the Product Society Chatbot."
            msg.attach(MIMEText(body))
            
            # PDF-Anhang
            with open(pdf_file, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{pdf_file.name}"')
            msg.attach(part)
            
            # Sende die E-Mail
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                if EMAIL_PASSWORD:  # Nur anmelden, wenn ein Passwort gesetzt ist
                    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)
                
            logger.info(f"E-Mail mit PDF erfolgreich gesendet an {EMAIL_RECIPIENT}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim E-Mail-Versand: {e}")
            return False
            
    def delete_file(self, file_path: Path) -> bool:
        """Löscht eine Datei"""
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Datei gelöscht: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Fehler beim Löschen der Datei {file_path}: {e}")
            return False
            
    def process_questionnaire(self, responses_file: Path) -> bool:
        """Verarbeitet einen abgeschlossenen Fragebogen"""
        try:
            # 1. Generiere PDF
            pdf_file = self.generate_pdf(responses_file)
            if not pdf_file:
                return False
                
            # 2. Sende E-Mail
            email_sent = self.send_email(pdf_file)
            
            # 3. Lösche temporäre Dateien
            self.delete_file(responses_file)
            if email_sent:
                self.delete_file(pdf_file)
                
            return email_sent
            
        except Exception as e:
            logger.error(f"Fehler bei der Verarbeitung des Fragebogens: {e}")
            return False

# Singleton-Instanz
pdf_handler = PDFHandler() 