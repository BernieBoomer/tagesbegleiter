# 📇 Übergabe-Index — Tagesbegleiter

> Chronologische Übersicht aller Übergabe-/Review-Dokumente zwischen Bodo und Claude.
> Neueste Einträge oben. Bei jeder neuen Übergabe eine Zeile ergänzen.

---

| Datum | Richtung | Dokument | Kurzbeschreibung | Status |
|---|---|---|---|---|
| 2026-08-08 | Bodo → Claude | `Response-Bodo-an-Claude-2026-08-08.md` | Regression bestätigt (kein Git!), DB-Passwort-Fix erledigt, SSL bestätigt funktionsfähig | ✅ ehrlich aufgeklärt, Ursache gefunden |
| 2026-08-08 | Bodo → Claude | `Uebergabe-Bodo-an-Claude-2026-08-08-v2.md` | Alle Blocker bestätigt behoben (Git, .env, SSL, ICS-Ansatz von Bernd bestätigt). Schema-Drift-Ursache geklärt: zweites, paralleles Verzeichnis `/data/tagesbegleiter-grundgeruest/` — nicht Claudes Rekonstruktion | ✅ Blocker zu, 3 kleine Folgepunkte offen |
| 2026-08-08 | Claude → Bodo | `Response-Claude-an-Bodo-2026-08-08-Rekonstruktion.md` | transcribe.py + waste.py rekonstruiert (unterschiedliche Sicherheit, waste.py unverifiziert), Git-Repository eingerichtet, /v1-Präfix für waste entschieden | ✅ von Bodo bestätigt, ICS-Ansatz korrekt |
| 2026-08-08 | — (Claude direkt verifiziert) | github.com/BernieBoomer/tagesbegleiter | **Erster direkter Repo-Zugriff.** models.py live geprüft: Contact/VisitNote-Schema entspricht dem Original (channel/channel_id, contact_name/clinic/topic) — Drift-Verdacht war das inzwischen entsorgte Zweit-Verzeichnis, nicht der echte Code | ✅ Schema-Drift-Sorge ausgeräumt, mit echtem Beleg statt Beschreibung |
| 2026-08-08 | Bodo → Claude | `Uebergabe-Bodo-an-Claude-2026-08-08-v3.md` | GitHub-Repo live (public), Cronjob-URLs auf /v1/ korrigiert, doppeltes Verzeichnis bereinigt | ✅ verifiziert über direkten GitHub-Zugriff |
| 2026-08-08 | Claude → Bodo | `Review-Claude-2026-08-08.md` | ⛔ Blocker: Verdacht auf Regression (Calendar/Contacts als Stub, Voice/Mail-Endpoints fehlen, Schema geändert), DB-Passwort im Klartext, SSL-Status unklar | ⏳ Klärung von Bodo ausstehend |
| 2026-08-08 | Bodo → Claude | `Uebergabe-Bodo-an-Claude-2026-08-08.md` | Server-Update, MariaDB/Apache-Recovery, PG14→16-Upgrade, Backend-Deployment, Offsite-Backup zu Hetzner Storage Box | ⚠️ reviewed, mehrere Blocker offen |
| 2026-08-01 | Claude → Bodo | (dieser Chat, noch kein separates Dokument) | Entscheidung: Migration SQLite → PostgreSQL, jetzt solange DB leer ist. Backup-Strategie wird mit Postgres-Umstellung zusammen gelöst | ⏳ an Bodo zu übergeben |
| 2026-08-01 | Bodo → Claude | `Response-Bodo-an-Claude-2026-08-01.md` | Alle Sofort-Punkte aus Review erledigt (Alembic, CORS, Backup, Versionierung), Rollenverteilung vereinbart | ✅ abgearbeitet, 2 Nachfragen offen (Backup-Offsite, Modellwahl) |
| 2026-08-01 | Claude → Bodo | `Review-Claude-2026-08-01.md` | Review der v0.2.0-Übergabe: Schema-Drift, CORS, Backup, Offline-Handling, Versionierung | ✅ von Bodo beantwortet |
| 2026-08-01 | Bodo → Claude | `Uebergabe-Bodo-an-Claude-2026-08-01.md` | Backend v0.2.0 live deployed, erweiterte Endpoints, DB-Schema-Übersicht | ✅ reviewed |
| 2026-07-30 | — | (Chat, kein Dokument) | Security-Runde: eigener System-User `tagesbegleiter`, systemd statt crontab, `nologin`-Shell | ✅ abgeschlossen |
| 2026-07-30 | — | (Chat, kein Dokument) | MVP 1 (Sprachnotizen/Whisper) und MVP 4 (Mail-Zusammenfassung) deployed und verifiziert | ✅ abgeschlossen |
| 2026-07-29 | Claude → Bodo | `Bodo-Briefing-Rollenwechsel.md` | Rollenklärung: Bodo = Orchestrator + Coder, kein Telegram-Workaround mehr, Security-Anforderungen, MVP-1-Ablauf | ✅ von Bodo bestätigt |
| 2026-07-29 | — | `tagesbegleiter-grundgeruest.zip` | Erstes Backend-/Flutter-Grundgerüst inkl. `CLAUDE.md`, lokal getestet | ✅ Basis für alle weiteren Übergaben |
| 2026-07-29 | — | `Dashboard-UI-Spec-v0_1.md` | UI-Spezifikation des Desktop-Dashboards, aus Mockup abgeleitet | ✅ Referenzdokument |
| Juli 2026 | — | `Pflichtenheft-v0_3.md` | Vollständiges Pflichtenheft, Architekturprinzip API-first ergänzt, VPS-Korrektur (dedizierter Server) | 📌 laufendes Referenzdokument |

---

## Offene Punkte über alle Übergaben hinweg (aktueller Stand)

- [x] **Zwei parallele Grundgerüst-Verzeichnisse zusammengeführt** (`/data/tagesbegleiter-grundgeruest/` entsorgt, Git-Repo unter `/home/tagesbegleiter/tagesbegleiter/` = Single Source of Truth)
- [x] **Schema-Drift Contact/VisitNote** — von Claude direkt auf GitHub verifiziert: kein Drift, echtes Schema entspricht dem Original
- [x] **GitHub-Repo eingerichtet, öffentlich, von Claude direkt lesbar** — erster echter Unabhängigkeits-Check erfolgreich
- [ ] API-Key in `.env` setzen (aktuell leer, Endpoints korrekt fail-closed aber unbenutzbar)
- [ ] Smoke-Tests mit echten Dateien von Bernd (Sprachnotiz, realer ICS-Export) nachholen
- [x] Testnachweis für rekonstruierte `waste.py` — von Bernd bestätigt, ICS-Ansatz korrekt
- [x] Git-Repository auf Server eingerichtet (Commit `18a88c1`, seitdem weitere Commits)
- [x] DB-Passwort aus Code in `.env` verschoben
- [x] SSL-Status verifiziert — funktioniert korrekt
- [x] `/v1/waste`-Präfix entschieden (konsistent mit allen anderen Routern)
- [ ] Modellwahl für sicherheitskritischen Code weiterhin ungeklärt — Bodo lief am 08.08. auf claude-sonnet-4-6, nicht Sonnet 5 wie ursprünglich empfohlen
- [ ] Alembic vollständig einrichten (vor nächster Schema-Änderung)
- [ ] PG14-Cluster-Daten löschen, wenn alles stabil läuft
- [ ] Architektur-Entscheidung BLOBs (Audio/Bilder) — Speicherort getrennt von der DB, bevor Datenmenge wächst
- [ ] Offline-Warteschlange für Flutter-App — laut Pflichtenheft Phase-3-Feature, aktuell bewusst zurückgestellt

---

## Referenzdokumente (fortlaufend versioniert, nicht Teil dieser Liste)

Diese Dateien werden bei Änderungen ersetzt/hochgezählt, nicht als neue datierte Einträge geführt:

- `Pflichtenheft-v0_X.md` — aktuell v0.3
- `Dashboard-UI-Spec-v0_X.md` — aktuell v0.1
- `CLAUDE.md` — kein Versionsnummer-Schema, lebt im Repo, wird direkt aktualisiert

---

*Zuletzt aktualisiert: 01.08.2026*
