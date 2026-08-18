# Claude-Uebergabe Tagesbegleiter
**Stand:** 18.08.2026 | **Letzter Commit:** 1a1c218

---

## Stack und Server
- Backend: FastAPI + PostgreSQL 16, Python 3.12
- Service-Venv: /home/tagesbegleiter/.venv/
- Projektpfad: /home/tagesbegleiter/tagesbegleiter/
- Server: Leaseweb 37.48.124.111, systemd-Service: tagesbegleiter-backend.service
- GitHub: BernieBoomer/tagesbegleiter (oeffentlich)
- Flutter: auf Bernds Windows-PC (nicht auf Server!)

## Alembic Migrationen
- Baseline: 4a1f1b246cb2
- 3709715557d1: shoppingitem Tabelle (13.08.2026)
- env.py liest DATABASE_URL aus .env via dotenv (nicht aus alembic.ini!)

## Endpoints (alle /v1/, Auth: X-API-Key Header)
- GET/POST/PATCH/DELETE /v1/todos
- GET/POST /v1/contacts
- GET/POST /v1/calendar
- GET/POST /v1/visit-notes (NIEMALS an CRM syncen!)
- GET/POST /v1/mail
- POST /v1/transcribe (faster-whisper)
- GET/POST /v1/waste/* (ICS einmal/Jahr manuell)
- GET/POST/PATCH/DELETE /v1/shopping (NEU 13.08.2026)

## Aktuelle Datenlage (13.08.2026)
- Todos: 1 echter Eintrag (Hartmut Essmann Anruf, 14.08., Wiedervorlage)
- Einkaufsliste: 7 echte Artikel (Kraeter, Leinoel, Mehl, Olivenoel, Fritz Spritz, Nudeln)
- Kontakte: Dr. med. Jalal Ramez (Berlin-Neukoelln, 030/667 12 20)
- Testdaten: alle geloescht

## Was heute gemacht wurde
1. db.py: pool_pre_ping=True + pool_recycle=1800 (SSL-Timeout-500er behoben)
2. Alle Testdaten geloescht
3. Einkaufsliste komplett: Model, Router /v1/shopping, Alembic-Migration, deployed
4. Alembic env.py gefixt: dotenv-basierte DATABASE_URL
5. Erster echter Todo: Hartmut Essmann Anruf
6. Erste echte Einkaufsartikel eingetragen
7. Erster echter Kontakt: Dr. Ramez per Visitenkarten-Foto

## Offene Punkte
- Flutter ShoppingList-Screen bauen (WICHTIG: jedes Feature = Backend + Flutter-Screen!)
- Flutter Dashboard: Einkaufsliste-Screen
- Muelkalender: echte ICS fuer Rauen hochladen
- Kontakte: weitere echte Kontakte eintragen
- Kalender: echte Termine importieren
- CLAUDE.md nach jeder Session committen (Pflicht!)

## Wichtige Konventionen
- Ein Router pro Ressource, eine Zeile in main.py
- Alembic Pflicht vor jeder Schema-Aenderung
- Secrets in .env, chmod 600, nie ins Repo
- Binaerdaten nicht in DB, nur Pfad speichern
- VisitNotes: NIEMALS an CRM syncen
- Jedes neue Feature = Backend-Endpoint + Flutter-Screen zusammen denken!

## Einkabe-Keywords (fuer Bodo im Chat)
- Todo: <Text> -> Bodo traegt ein
- Einkauf: <Artikel> <Menge> -> Bodo traegt ein
- Einkaufsliste -> Bodo zeigt Liste
- Abhaken: <Artikel> -> Bodo hakt ab

## Technische Stolperfallen
- Alembic autogenerate erzeugt sqlmodel.sql.sqltypes.AutoString() ohne Import -> durch sa.String() ersetzen
- Service-Venv: /home/tagesbegleiter/.venv/ (nicht .../tagesbegleiter/venv/)
- alembic.ini hat *** als Passwort-Platzhalter, nie direkt nutzen
- Flutter laeuft auf Windows-PC, nicht auf Leaseweb!
- Paramiko fuer SSH von Hermes aus (kein direkter SSH-Zugang)
