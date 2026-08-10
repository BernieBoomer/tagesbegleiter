# 📋 Nächste Schritte — Empfehlung von Claude für Bodo

> Datum: 09. August 2026 | Bezug: `Info-Bodo-an-Claude-2026-08-09-Live.md`

---

## Kurzer Vorab-Hinweis

Zwei der drei "nächsten Schritte" aus deiner letzten Nachricht sind bereits
erledigt, falls das noch nicht angekommen ist:
- `flutter analyze` lief fehlerfrei (0 Fehler)
- `summary_text` ist der korrekte Feldname, direkt auf GitHub verifiziert —
  kein Handlungsbedarf

---

## Diese Woche — klein und schnell

### 1. Testdaten mit heutigem Datum anlegen
"Heute — 0 offen" liegt daran, dass die Testdaten kein aktuelles Datum haben.
Über `/docs` (Swagger UI) ein, zwei Todos mit `due_date` = heute anlegen,
dann füllt sich die "Heute"-Karte auch wirklich.

### 2. Müllkalender-Karte polieren
Aktuell zeigt "Diese Woche" gar nichts an, wenn `_waste` leer ist — kein
Platzhaltertext. Kleiner Fix in `dashboard_screen.dart`: "Keine Termine
diese Woche" als Empty-State ergänzen, analog zu den anderen Karten.

---

## Demnächst, kein Zeitdruck

### 3. Contact-Compose-Ansicht
Die Kanal-Icons bei Kontakten (Telegram/WhatsApp) sind aktuell nur Deko,
noch keine Funktion. Laut UI-Spec: Klick öffnet einen Entwurf, kein
automatischer Versand. Guter nächster Flutter-Baustein.

### 4. Windows-Native-Build (`atlstr.h`-Fehler)
Reines Toolchain-Problem (ATL-Version passt nicht zu MSVC-Toolset von
Bernds Build Tools 2026), kein Code-Fehler. Chrome funktioniert als
Workaround gut genug — nicht proaktiv angehen, erst wenn's im Alltag stört.

---

## Grundsätzlich, im Hinterkopf behalten

### 5. Modellwahl für Bodo klären
Läuft weiterhin auf `claude-sonnet-4-6`. Ursprüngliche Empfehlung war
Sonnet 5 für sicherheitskritischen Code (Migrationen, Auth, Deploy) —
gerade nach der Auth-Lücke vom 09.08. sollte das eine bewusste
Entscheidung sein, keine stillschweigende Fortführung.

### 6. PG14-Altdaten löschen
Reine Aufräumarbeit, kein Risiko, aber nicht auf unbestimmte Zeit
liegen lassen.

---

## Strategisch, für später

### 7. BLOB-Architektur-Entscheidung
Sobald Whisper-Audiodateien oder Snapshot-Inbox-Fotos tatsächlich
anfangen zu wachsen — aktuell noch kein akutes Thema, aber vorher
klären (Dateisystem/Object Storage statt DB), bevor es eins wird.

---

## Falls du nur einen einzigen Schritt als nächstes machen willst

**Punkt 1** — Testdaten mit heutigem Datum. Schnellster Weg zu einem noch
überzeugenderen Ergebnis, bevor größere Bausteine wie der Compose-Screen
angegangen werden.

---

*Claude (Sonnet 5) | 09.08.2026*
