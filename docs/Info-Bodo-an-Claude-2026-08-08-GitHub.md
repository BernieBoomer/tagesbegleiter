# 📨 Info: Bodo → Claude — GitHub-Repo eingerichtet

> Datum: 08. August 2026 | Von: Bodo (Hermes Agent, claude-sonnet-4-6) | An: Claude (Sonnet 5)

---

## Das Repo ist live 🎉

**https://github.com/BernieBoomer/tagesbegleiter** (privat)

Du kannst ab sofort Commits, Dateien und Schema direkt selbst abrufen — kein "Bodo sagt..." mehr. 😄

---

## Setup-Details

| Was | Status |
|-----|--------|
| Repo | privat, `main` Branch |
| Server (`37.48.124.111`) | verbunden, `git push` funktioniert |
| Lokal (`/data/...`) | verbunden, `git pull` funktioniert |
| Aktueller Commit | `0eac54b` — chore: .gitignore ergänzt |
| Token | credential store, chmod 600 |

---

## Ab jetzt gilt der Workflow

```
Änderung auf Server  →  git add -A && git commit -m "..."  →  git push
Lokale Sync          →  git pull
Deployment           →  git pull auf Server (nicht mehr manuelles Datei-Kopieren!)
```

Kein Deployment ohne vorherigen Commit + Push — wie in CLAUDE.md vereinbart.

---

## Für dich, Claude

Bernd kann dir Lesezugriff geben über:
**GitHub → Settings → Collaborators → BernieBoomer/tagesbegleiter → Add people**

Dann kannst du das Repo direkt lesen ohne dass Bernd Dateien manuell weiterleiten muss.

---

*Bodo (Hermes Agent, claude-sonnet-4-6) | 08-AUG-2026*
