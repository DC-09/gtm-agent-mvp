"""Verifica automatica delle fonti dei lead qualificati.

Uso:
    python scripts/verify_sources.py [file.json]       # verifica e scrive data/verification.json
    python scripts/verify_sources.py --show URL PAROLA  # mostra il testo della pagina intorno a PAROLA

Per ogni lead QUALIFIED riapre le pagine citate e controlla, in modo tollerante:
- che la frase copiata dalla fonte (`evidence_quote`) di ogni segnale che dà punti ci sia davvero;
- che il nome del buyer compaia nella sua pagina di fonte;
- che il telefono aziendale, se c'è in data/contacts.json, compaia nella pagina da cui è preso.

Un lead va al revisore ("da rivedere") solo in due casi (docs/decisions.md):
1. c'è un dubbio di esclusione non risolto (`doubts` con tipo `possibile_esclusione`);
2. togliendo i fatti non confermati il lead cambierebbe tier: il risultato dipende da qualcosa
   che lo script non è riuscito a confermare.
Tutto il resto (pagina bloccata o fatto non confermato che non cambia il tier) resta una nota.
"""

import copy
import html
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contacts import digits, load as load_contacts  # noqa: E402
from validate_leads import DEFAULT_DATA, MAP, ROOT, compute  # noqa: E402

OUT = ROOT / "data" / "verification.json"
USER_AGENT = "IusfulGTM-verifier/0.1 (verifica fonti per un progetto MVP; contatto nel repository)"
TIMEOUT_S = 15
MIN_COVERAGE = 0.75  # quota di parole della citazione che devono comparire nella pagina

_cache = {}
CONTACTS = load_contacts()


def normalize(text):
    text = unicodedata.normalize("NFKD", html.unescape(text))
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    text = re.sub(r"(?<=\d)[.\s](?=\d{3}\b)", "", text)  # 25.000 / 25 000 -> 25000
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def page_text(url):
    """Testo visibile della pagina, oppure (None, motivo) se non si apre."""
    if url in _cache:
        return _cache[url]
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "it,en;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            raw = resp.read().decode(resp.headers.get_content_charset() or "utf-8", errors="replace")
        raw = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", raw)
        result = (re.sub(r"<[^>]+>", " ", raw), None)
    except urllib.error.HTTPError as e:
        result = (None, f"pagina non raggiungibile (HTTP {e.code})")
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        result = (None, f"pagina non raggiungibile ({getattr(e, 'reason', e)})")
    _cache[url] = result
    return result


def quote_found(quote, text):
    """Tollerante ma locale: in uno stesso tratto di testo devono comparire tutte le cifre
    della citazione e almeno il 75% delle sue parole. Parole sparse in punti diversi della
    pagina non bastano."""
    q, t = normalize(quote), normalize(text)
    if q and f" {q} " in f" {t} ":
        return True, 1.0
    words = list(dict.fromkeys(w for w in q.split() if len(w) >= 3 or w.isdigit()))
    if not words:
        return False, 0.0
    numbers = {w for w in words if w.isdigit()}
    tokens = t.split()
    window = 2 * len(q.split()) + 5
    wanted = set(words)
    best = 0.0
    for start in range(0, max(1, len(tokens) - window + 1)):
        seen = wanted.intersection(tokens[start:start + window])
        if numbers - seen:
            continue
        best = max(best, len(seen) / len(words))
        if best >= MIN_COVERAGE:
            break
    return best >= MIN_COVERAGE, round(best, 2)


def check_lead(lead):
    checks, notes, unconfirmed_signals, buyer_unconfirmed = [], [], [], False
    _, base = compute(lead)

    for i, s in enumerate(lead["signals"]):
        _, _, is_event = MAP[s["map_row"]]
        if not (is_event and s["date"]):
            continue  # conta solo per la complessità: non serve confermarlo per il tier
        q = s.get("evidence_quote")
        if not q:
            checks.append({"what": f"segnale {s['map_row']}", "url": s["url"], "ok": False, "detail": "nessuna citazione salvata"})
            unconfirmed_signals.append(i)
            continue
        text, err = page_text(s["url"])
        if text is None:
            checks.append({"what": f"segnale {s['map_row']}", "url": s["url"], "ok": False, "detail": err})
            unconfirmed_signals.append(i)
            continue
        ok, cov = quote_found(q, text)
        checks.append({"what": f"segnale {s['map_row']}", "url": s["url"], "ok": ok,
                       "detail": "citazione trovata" if ok else f"citazione non trovata (copertura {cov})"})
        if not ok:
            unconfirmed_signals.append(i)

    b = lead["buyer"]
    if b["name"] and b["source_url"] and b["role_match"] != "unclear":
        text, err = page_text(b["source_url"])
        ok = text is not None and quote_found(b["name"], text)[0]
        detail = "nome trovato" if ok else (err or "nome non trovato nella pagina")
        # LinkedIn blocca la lettura automatica: un profilo personale trovato da Clay vale come
        # confermato (docs/decisions.md), altrimenti ogni buyer da Clay finirebbe "da rivedere"
        if not ok and text is None and "linkedin.com/in/" in b["source_url"]:
            ok, detail = True, "profilo LinkedIn trovato da Clay, non leggibile in automatico: accettato"
        checks.append({"what": "buyer", "url": b["source_url"], "ok": ok, "detail": detail})
        buyer_unconfirmed = not ok

    # Il tier reggerebbe senza i fatti non confermati?
    reasons = []
    if unconfirmed_signals or buyer_unconfirmed:
        worst = copy.deepcopy(lead)
        worst["signals"] = [s for i, s in enumerate(lead["signals"]) if i not in unconfirmed_signals]
        if buyer_unconfirmed:
            worst["buyer"]["role_match"] = "unclear"
        _, w = compute(worst)
        if w["tier"] != base["tier"]:
            missing = [c["what"] for c in checks if not c["ok"]]
            reasons.append(f"il tier passerebbe da {base['tier']} a {w['tier']} senza i fatti non confermati: {', '.join(missing)}")
        else:
            notes.append("fatti non confermati, ma il tier resta lo stesso anche senza: " +
                         ", ".join(c["what"] for c in checks if not c["ok"]))

    # Telefono aziendale (data/contacts.json): il numero deve comparire nella pagina citata.
    # Nell'esito si scrive solo se c'è, non il numero: data/verification.json è nel repository.
    phone = (CONTACTS.get(lead["id"]) or {}).get("company_phone")
    if phone:
        text, err = page_text(phone["source_url"])
        ok = text is not None and digits(phone["value"]) in re.sub(r"\D", "", text)
        checks.append({"what": "telefono aziendale", "url": phone["source_url"], "ok": ok,
                       "detail": "numero trovato" if ok else (err or "numero non trovato nella pagina")})
        if not ok:
            notes.append("telefono aziendale non confermato sulla pagina: da ricontrollare, non cambia il tier")

    for d in lead.get("doubts", []):
        if d["type"] == "possibile_esclusione":
            reasons.append(f"possibile esclusione da verificare: {d['detail']}")

    return {
        "status": "da_rivedere" if reasons else "superata",
        "reasons": reasons,
        "notes": notes,
        "checks": checks,
        "checked_at": datetime.now().isoformat(timespec="seconds"),
    }


def show(url, word):
    text, err = page_text(url)
    if text is None:
        print(err)
        return 1
    flat = re.sub(r"\s+", " ", html.unescape(text))
    hits = [m.start() for m in re.finditer(re.escape(word), flat, re.IGNORECASE)][:5]
    print(f"{len(hits)} occorrenze di '{word}'")
    for h in hits:
        print("  …" + flat[max(0, h - 200): h + 250] + "…")
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) >= 4 and sys.argv[1] == "--show":
        return show(sys.argv[2], " ".join(sys.argv[3:]))

    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DATA
    leads = json.loads(path.read_text(encoding="utf-8"))
    results = {}
    for lead in leads:
        if lead["status"] != "QUALIFIED":
            continue
        r = check_lead(lead)
        results[lead["id"]] = r
        mark = "✓ superata   " if r["status"] == "superata" else "⚠ da rivedere"
        print(f"{mark} {lead['company_name']}")
        for c in r["checks"]:
            print(f"      {'ok ' if c['ok'] else 'no '} {c['what']}: {c['detail']}")
        for x in r["reasons"]:
            print(f"      → da rivedere: {x}")
        for x in r["notes"]:
            print(f"      · nota: {x}")

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    to_review = sum(r["status"] == "da_rivedere" for r in results.values())
    print(f"\nVerificati: {len(results)}; da rivedere: {to_review}. Esito in {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
