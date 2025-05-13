from typing import Dict, List, Optional, Union, Literal
import json
from pathlib import Path
import datetime
import logging

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Datenmodelle
class Question:
    def __init__(self, id: str, section: str, text: str, 
                 type: Literal["text", "choice", "date", "number"], 
                 options: Optional[List[str]] = None):
        self.id = id
        self.section = section
        self.text = text
        self.type = type
        self.options = options or []

    def to_dict(self):
        return {
            "id": self.id,
            "section": self.section,
            "text": self.text,
            "type": self.type,
            "options": self.options
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data["id"],
            section=data["section"],
            text=data["text"],
            type=data["type"],
            options=data.get("options", [])
        )

class QuestionnaireManager:
    def __init__(self):
        self.questions = []
        self._load_questions()
        self.active_sessions = {}  # chat_id -> {current_index, responses}
    
    def _load_questions(self) -> List[Question]:
        """Lädt die Fragebogen-Definitionen aus der JSON-Datei"""
        try:
            questions_file = Path("app/data/questions.json")
            if questions_file.exists():
                with open(questions_file, "r", encoding="utf-8") as f:
                    questions_data = json.load(f)
                self.questions = [Question.from_dict(q) for q in questions_data]
            else:
                # Fallback zu hardcodierten Fragen, wenn die Datei nicht existiert
                self._create_default_questions()
        except Exception as e:
            logger.error(f"Fehler beim Laden der Fragen: {e}")
            self._create_default_questions()
        
        return self.questions
    
    def _create_default_questions(self):
        """Erstellt die Standard-Fragen basierend auf der Spezifikation"""
        # Diese Methode würde alle Fragen aus der Spezifikation erstellen
        # Für die Kürze wird hier nur eine Teilmenge erstellt
        self.questions = [
            Question(
                id="product_development_type",
                section="Product Development Request",
                text="What type of product development is being requested?",
                type="choice",
                options=["New Development", "Modify Existing", "Formulate to Benchmark", 
                         "Line Extension", "PDR Revision", "Formula Redirect", "Tech Transfer"]
            ),
            Question(
                id="customer_company",
                section="Customer Profile",
                text="What is the name of the company or brand?",
                type="text"
            ),
            # Weitere Fragen würden hier hinzugefügt werden
        ]
        
        # Speichern der Fragen in einer JSON-Datei
        self._save_questions()
    
    def _save_questions(self):
        """Speichert die Fragen in einer JSON-Datei"""
        questions_file = Path("app/data/questions.json")
        questions_file.parent.mkdir(exist_ok=True)
        
        with open(questions_file, "w", encoding="utf-8") as f:
            json.dump([q.to_dict() for q in self.questions], f, indent=2)
    
    def start_questionnaire(self, chat_id: int) -> Optional[Question]:
        """Startet einen neuen Fragebogen für den angegebenen Chat"""
        if not self.questions:
            return None
            
        self.active_sessions[chat_id] = {
            "current_index": 0,
            "responses": {},
            "start_time": datetime.datetime.now().isoformat()
        }
        
        return self.questions[0]
    
    def get_next_question(self, chat_id: int, response: str) -> Optional[Question]:
        """Speichert die aktuelle Antwort und gibt die nächste Frage zurück"""
        if chat_id not in self.active_sessions:
            return None
            
        session = self.active_sessions[chat_id]
        current_index = session["current_index"]
        
        # Speichere die aktuelle Antwort
        current_question = self.questions[current_index]
        session["responses"][current_question.id] = response
        
        # Gehe zur nächsten Frage
        next_index = current_index + 1
        if next_index >= len(self.questions):
            # Fragebogen ist abgeschlossen
            response_file = self._save_responses(chat_id)
            if response_file:
                # Starte den PDF-Erstellungs- und E-Mail-Versandprozess
                self._process_completed_questionnaire(response_file)
            return None
            
        session["current_index"] = next_index
        return self.questions[next_index]
    
    def _save_responses(self, chat_id: int) -> Optional[Path]:
        """Speichert die Antworten des Fragebogens und gibt den Dateipfad zurück"""
        if chat_id not in self.active_sessions:
            return None
            
        session = self.active_sessions[chat_id]
        
        # Erstelle Verzeichnis, falls es nicht existiert
        responses_dir = Path("app/data/responses")
        responses_dir.mkdir(exist_ok=True, parents=True)
        
        # Speichere die Antworten in einer JSON-Datei mit Zeitstempel
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"responses_{chat_id}_{timestamp}.json"
        file_path = responses_dir / filename
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({
                    "chat_id": chat_id,
                    "start_time": session["start_time"],
                    "end_time": datetime.datetime.now().isoformat(),
                    "responses": session["responses"]
                }, f, indent=2)
            
            # Entferne die Session
            del self.active_sessions[chat_id]
            
            logger.info(f"Antworten gespeichert in {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Antworten: {e}")
            return None
    
    def _process_completed_questionnaire(self, response_file: Path):
        """Verarbeitet einen abgeschlossenen Fragebogen (PDF-Erstellung und E-Mail-Versand)"""
        try:
            # Importiere den PDF-Handler erst hier, um zirkuläre Importe zu vermeiden
            from .pdf_handler import pdf_handler
            
            # Starte die Verarbeitung asynchron
            import threading
            thread = threading.Thread(
                target=pdf_handler.process_questionnaire,
                args=(response_file,)
            )
            thread.start()
            
            logger.info(f"PDF-Erstellung und E-Mail-Versand für {response_file} gestartet")
            
        except Exception as e:
            logger.error(f"Fehler bei der Verarbeitung des Fragebogens: {e}")
    
    def is_questionnaire_active(self, chat_id: int) -> bool:
        """Prüft, ob ein Fragebogen für den Chat aktiv ist"""
        return chat_id in self.active_sessions

# Singleton-Instanz
questionnaire_manager = QuestionnaireManager() 