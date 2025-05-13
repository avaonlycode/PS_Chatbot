# Product Society Chatbot - Fragebogen-Funktion

## Übersicht

Der Product Society Chatbot enthält eine automatische Fragebogenfunktion, die bei jedem neuen Chat gestartet wird. Der Fragebogen sammelt wichtige Informationen über Produktentwicklungsanfragen und speichert diese für die spätere Verwendung.

## Funktionsweise

1. **Automatischer Start**: Wenn ein Benutzer den Chat mit `/start` beginnt, wird der Fragebogen automatisch gestartet.
2. **Manuelle Steuerung**: Der Fragebogen kann auch manuell mit `/questionnaire` gestartet oder mit `/cancel` abgebrochen werden.
3. **Schrittweise Abfrage**: Die Fragen werden nacheinander gestellt, und der Benutzer kann sie der Reihe nach beantworten.
4. **Speicherung**: Die Antworten werden in JSON-Dateien im Verzeichnis `app/data/responses/` gespeichert.

## Fragebogen-Struktur

Der Fragebogen ist in verschiedene Abschnitte unterteilt:

1. **Product Development Request**: Grundlegende Informationen zur Art der Produktentwicklung
2. **Customer Profile**: Informationen zum Kunden und zum Produkt
3. **Packaging**: Verpackungsdetails und -anforderungen
4. **Formula Profile**: Informationen zur Formulierung und zu Inhaltsstoffen
5. **Benchmark**: Vergleichsprodukte und deren Eigenschaften
6. **Regulatory**: Regulatorische Informationen
7. **Sampling Instructions**: Anweisungen für Produktmuster
8. **Additional Comments**: Zusätzliche Anmerkungen oder Anforderungen

## Datenmodell

Die Fragen sind als JSON-Objekte mit folgenden Eigenschaften definiert:

- **id**: Eindeutiger Bezeichner für die Frage
- **section**: Abschnitt, zu dem die Frage gehört
- **text**: Der Text der Frage
- **type**: Typ der Frage (text, choice, date, number)
- **options**: Liste von Auswahlmöglichkeiten (nur für Fragen vom Typ "choice")

## Anpassung

Die Fragen können angepasst werden, indem die Datei `app/data/questions.json` bearbeitet wird. Nach Änderungen muss der Bot neu gestartet werden, damit die Änderungen wirksam werden.

## Beispiel-Antworten

Die gesammelten Antworten werden in folgendem Format gespeichert:

```json
{
  "chat_id": 123456789,
  "start_time": "2023-05-01T12:34:56.789Z",
  "end_time": "2023-05-01T12:45:00.123Z",
  "responses": {
    "product_development_type": "New Development",
    "customer_company": "Example Brand",
    "customer_contact_name": "John Doe",
    "customer_phone": "+1 234 567 8900",
    "customer_email": "john@example.com",
    // weitere Antworten
  }
}
``` 