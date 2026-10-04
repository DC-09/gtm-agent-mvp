"""Controllo settimanale: cosa è cambiato da una settimana all'altra.

Uso:
    python scripts/watch_signals.py           # controlla e scrive data/weekly/novita_<data>.json
    python scripts/watch_signals.py --reset   # dimentica le copie salvate (la prossima esecuzione fa da base)

Fa la parte meccanica del flusso settimanale (prompts/settimanale.md), senza decidere nulla:
1. riapre le pagine di data/watch.json (annunci di lavoro, comunicati) e le confronta con la
   copia della settimana prima; per una pagina cambiata riporta solo le frasi nuove;
2. ricalcola il punteggio di ogni lead alla data di oggi, senza scriverlo: i segnali invecchiano
   (dopo 12 mesi valgono metà, dopo 18 zero) e un lead può cambiare tier anche se non succede nulla.
Se una frase nuova è davvero un segnale lo decide l'agente, con le regole di sempre.
Le copie delle pagine stanno in data/watch_state.json (fuori dal repository).
"""

import copy
import hashlib
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_leads import DEFAULT_DATA, ROOT, compute  # noqa: E402
from verify_sources import page_text  # noqa: E402

WATCH = ROOT / "data" / "watch.json"
STATE = ROOT / "data" / "watch_state.json"
OUT_DIR = ROOT / "data" / "weekly"
MAX_NEW_SENTENCES = 15


CHUNK_WORDS = 25


def sentences(text):
    """Pezzi di testo della pagina, per vedere cosa è comparso di nuovo. Le frasi lunghe
    (le pagine senza punteggiatura ne hanno molte) si spezzano in blocchi di 25 parole."""
    flat = re.sub(r"\s+", " ", html.unescape(text))
    out = []
    for part in re.split(r"(?<=[.!?;])\s+| \| ", flat):
        words = part.split()
        for i in range(0, len(words), CHUNK_WORDS):
            chunk = " ".join(words[i:i + CHUNK_WORDS])
            if len(chunk) >= 25:
                out.append(chunk)
    return out


def key(sentence):
    """Confronto che ignora maiuscole e numeri: contatori e date cambiano a ogni visita."""
    return re.sub(r"\d+", "#", sentence.lower())


def check_pages(watch, state):
    changes, errors = [], []
    for lead_id, urls in watch.items():
        if lead_id.startswith("_"):
            continue
        for url in urls:
            text, err = page_text(url)
            if text is None:
                errors.append({"lead": lead_id, "url": url, "error": err})
                continue
            sents = sentences(text)
            keys = sorted({key(s) for s in sents})
            digest = hashlib.sha256("\n".join(keys).encode("utf-8")).hexdigest()
            old = state.get(url)
            state[url] = {"hash": digest, "keys": keys, "checked": date.today().isoformat()}
            if old is None:
                continue  # prima volta: fa da base, nessuna novità
            if old["hash"] != digest:
                seen = set(old["keys"])
                new = [s for s in sents if key(s) not in seen][:MAX_NEW_SENTENCES]
                if new:
                    changes.append({"lead": lead_id, "url": url, "new_sentences": new})
    return changes, errors


def aging(leads, today):
    """Lead che oggi avrebbero un tier diverso solo perché i segnali sono invecchiati."""
    moved = []
    for lead in leads:
        if lead["status"] == "REJECTED" and lead["exclusion_reason"]:
            continue
        now = copy.deepcopy(lead)
        now["evaluation_date"] = today.isoformat()
        score, d = compute(now)
        if d["tier"] != lead["tier"] or score["total"] != lead["score"]["total"]:
            moved.append({"lead": lead["id"], "company": lead["company_name"],
                          "from": f"{lead['tier']} {lead['score']['total']}",
                          "to": f"{d['tier']} {score['total']}"})
    return moved


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--reset" in sys.argv:
        STATE.unlink(missing_ok=True)
        print("Copie salvate cancellate.")
        return 0
    today = date.today()
    watch = json.loads(WATCH.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    first_run = not state
    leads = json.loads(DEFAULT_DATA.read_text(encoding="utf-8"))

    changes, errors = check_pages(watch, state)
    moved = aging(leads, today)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / f"novita_{today.isoformat()}.json"
    result = {"date": today.isoformat(), "first_run": first_run, "page_changes": changes,
              "page_errors": errors, "aging": moved}
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    pages = sum(len(v) for k, v in watch.items() if not k.startswith("_"))
    print(f"Pagine controllate: {pages}{' (prima esecuzione: salvate come base)' if first_run else ''}")
    print(f"Pagine con frasi nuove: {len(changes)}")
    for c in changes:
        print(f"  - {c['lead']}: {c['url']} ({len(c['new_sentences'])} frasi nuove)")
    print(f"Pagine non raggiungibili: {len(errors)}")
    for e in errors:
        print(f"  - {e['lead']}: {e['url']} ({e['error']})")
    print(f"Lead che cambiano punteggio per l'età dei segnali: {len(moved)}")
    for m in moved:
        print(f"  - {m['company']}: {m['from']} -> {m['to']}")
    print(f"Esito in {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
