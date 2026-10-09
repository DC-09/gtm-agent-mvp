"""Controlla i lead contro lo schema e contro le regole di docs/scoring.md.

Uso:
    python scripts/validate_leads.py [file.json]

Il file (default: data/leads.json) è un array di lead. Per ogni lead lo script:
1. verifica lo schema schemas/lead.schema.json;
2. ricalcola i cinque componenti, il totale, il tier e lo status;
3. controlla le regole che lo schema non vede (URL obbligatori, flag, esclusioni,
   coerenza delle sottrazioni, lunghezza delle score_reason, duplicati).
Alla fine stampa il funnel. Esce con codice 1 se c'è almeno un errore.
"""

import json
import sys
from datetime import date
from pathlib import Path

from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contacts import check as check_contacts, load as load_contacts  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schemas" / "lead.schema.json"
DEFAULT_DATA = ROOT / "data" / "leads.json"

# docs/icp.md §4.1: aree Iusful, forza, e se la riga è un'attività (conta nei buying signals)
# o un tratto strutturale (conta solo in legal_complexity).
MAP = {
    "piu_paesi": (["Contratti", "Societario"], "forte", True),
    "fundraising_soci": (["Societario"], "normale", True),
    "piani_dipendenti": (["Societario"], "normale", True),
    "assunzioni": (["Lavoro & persone"], "normale", True),
    "remoto_ibrido": (["Lavoro & persone"], "normale", True),
    "freelance_agenzie": (["Proprietà intellettuale", "Contratti"], "normale", True),
    "prodotto_ai": (["Tech, AI & cyber", "Dati & privacy"], "normale", True),
    "saas_piattaforma": (["Contratti", "Dati & privacy", "Tech, AI & cyber"], "normale", False),
    "marketplace_ecommerce": (["Contratti", "Dati & privacy", "Tech, AI & cyber"], "normale", False),
    "brevetto": (["Proprietà intellettuale", "Contratti"], "normale", True),
    # (4 ottobre 2026) Complessità di chi vende solo in Italia: una rete di sedi pesa come l'export
    "rete_sedi": (["Contratti", "Lavoro & persone"], "forte", False),
    "apertura_acquisizione": (["Contratti", "Lavoro & persone"], "normale", True),
    # (4 ottobre 2026) Segmenti servizi (B2B e B2C) e sanità e formazione private
    "servizio_continuativo": (["Contratti", "Dati & privacy"], "normale", False),
    "dati_particolari": (["Dati & privacy", "Tech, AI & cyber"], "forte", False),
    "appalti_convenzioni": (["Contratti", "Dati & privacy"], "normale", True),
    "nuovo_servizio": (["Contratti", "Dati & privacy"], "normale", True),
}

# docs/scoring.md §2.2
AREA_POINTS = {0: 0, 1: 5, 2: 9, 3: 13, 4: 17, 5: 20, 6: 20}
STRONG_BONUS = 5

# docs/scoring.md §2.3: (fino a 12 mesi, tra 12 e 18 mesi)
SIGNAL_POINTS = {"forte": (12, 6), "normale": (7, 3)}

# docs/scoring.md §2.4
BUYER_POINTS = {"primario": 10, "alternativa": 7, "solo ruolo": 4, "nome senza ruolo": 4, "unclear": 0}

# docs/scoring.md §2.5
DEDUCTIONS = {"fatturato_mancante": 1, "nessuna_fonte_primaria": 2, "dato_non_verificato": 2}
MAX_UNVERIFIED_DEDUCTION = 4

# docs/scoring.md §2.3: righe che un annuncio di lavoro può mostrare, e che quindi possono
# essere datate al giorno della consultazione se l'annuncio non ha data.
JOB_AD_ROWS = {"assunzioni", "remoto_ibrido", "freelance_agenzie", "piu_paesi"}

REVENUE_FLAG_THRESHOLD = 50_000_000
MAX_REASON_WORDS = 40


def parse_partial_date(s):
    """YYYY-MM-DD, YYYY-MM o YYYY. Mese o anno senza giorno partono dal primo giorno (prudente)."""
    parts = [int(p) for p in s.split("-")]
    while len(parts) < 3:
        parts.append(1)
    return date(*parts)


def months_between(start, end):
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1
    return months


def employees_status(emp):
    """Restituisce (verificati, numero_minimo_noto, numero_massimo_noto)."""
    if not emp["source_url"] or emp["source_says_unverified"]:
        return False, None, None
    if emp["value"] is not None:
        return 1 <= emp["value"] <= 50, emp["value"], emp["value"]
    lo, hi = emp["range_min"], emp["range_max"]
    if lo is not None:
        # range_max None = fascia aperta ("oltre 70"): non verifica mai il perimetro 1-50
        return hi is not None and lo >= 1 and hi <= 50, lo, hi
    return False, None, None


def compute(lead):
    """Ricalcola lo score secondo docs/scoring.md. Restituisce (score, dettagli)."""
    f = lead["facts"]
    eval_date = date.fromisoformat(lead["evaluation_date"])

    # 2.1 company_fit
    fit = 0
    if f["country"]["value"] == "Italia" and f["country"]["source_url"]:
        fit += 5
    emp_verified, emp_lo, emp_hi = employees_status(f["employees"])
    if emp_verified:
        fit += 10
    bm = f["business_model"]
    if bm["value"] not in (None, "Fuori elenco") and bm["source_url"]:
        # "Aziende innovative" vale solo con iscrizione verificata come PMI innovativa [DEC]
        if bm["value"] != "Aziende innovative" or (
            f["innovative_registry"]["section"] == "PMI innovativa" and f["innovative_registry"]["source_url"]
        ):
            fit += 15

    # 2.2 legal_complexity
    areas, strong = set(), False
    for s in lead["signals"]:
        row_areas, strength, _ = MAP[s["map_row"]]
        areas.update(row_areas)
        strong = strong or strength == "forte"
    complexity = min(25, AREA_POINTS[len(areas)] + (STRONG_BONUS if strong else 0))

    # 2.3 buying_signals
    # Gli annunci datati alla consultazione: una stessa pagina conta una volta sola (il migliore).
    # Poi, per ogni riga della mappa, conta il segnale che vale di più.
    candidates, signal_ages = [], []
    for s in lead["signals"]:
        _, strength, is_event = MAP[s["map_row"]]
        age = None
        if s["date"]:
            age = months_between(parse_partial_date(s["date"]), eval_date)
        signal_ages.append(age)
        if not is_event or age is None or age < 0:
            continue
        full, half = SIGNAL_POINTS[strength]
        pts = full if age <= 12 else half if age <= 18 else 0
        candidates.append((s["map_row"], s["url"], s["date_basis"], pts))
    best_per_page = {}
    for row, url, basis, pts in candidates:
        if basis == "consultazione" and pts > best_per_page.get(url, (None, -1))[1]:
            best_per_page[url] = (row, pts)
    kept = [(row, pts) for row, url, basis, pts in candidates if basis != "consultazione"]
    kept += list(best_per_page.values())
    best_per_row = {}
    for row, pts in kept:
        best_per_row[row] = max(best_per_row.get(row, 0), pts)
    buying = min(25, sum(best_per_row.values()))

    # 2.4 buyer_availability
    buyer_pts = BUYER_POINTS[lead["buyer"]["role_match"]]

    # 2.5 evidence_quality
    unverified = sum(DEDUCTIONS["dato_non_verificato"] for d in lead["evidence_deductions"] if d["code"] == "dato_non_verificato")
    other = sum(DEDUCTIONS[d["code"]] for d in lead["evidence_deductions"] if d["code"] != "dato_non_verificato")
    evidence = max(0, 10 - other - min(unverified, MAX_UNVERIFIED_DEDUCTION))

    total = fit + complexity + buying + buyer_pts + evidence

    # 3. tier
    if lead["exclusion_reason"]:
        tier = "REJECT"
    elif total >= 80:
        tier = "A" if emp_verified else "B"
    elif total >= 65:
        tier = "B"
    elif total >= 50:
        tier = "C"
    else:
        tier = "REJECT"
    status = {"A": "QUALIFIED", "B": "QUALIFIED", "C": "RESERVE", "REJECT": "REJECTED"}[tier]

    score = {
        "company_fit": fit, "legal_complexity": complexity, "buying_signals": buying,
        "buyer_availability": buyer_pts, "evidence_quality": evidence, "total": total,
    }
    details = {
        "emp_verified": emp_verified, "emp_lo": emp_lo, "emp_hi": emp_hi,
        "areas": sorted(areas), "signal_ages": signal_ages, "tier": tier, "status": status,
    }
    return score, details


def check_rules(lead, score, d):
    errors, warnings = [], []
    f = lead["facts"]

    # Score, tier, status ricalcolati
    for k, v in score.items():
        if lead["score"][k] != v:
            errors.append(f"score.{k} = {lead['score'][k]}, ricalcolato {v}")
    if lead["tier"] != d["tier"]:
        errors.append(f"tier = {lead['tier']}, atteso {d['tier']}")
    if lead["status"] != d["status"]:
        errors.append(f"status = {lead['status']}, atteso {d['status']}")

    # Esclusioni di perimetro verificabili dai dati
    rule = lead["exclusion_reason"]["rule"] if lead["exclusion_reason"] else None
    emp = f["employees"]
    if emp["source_url"] and not emp["source_says_unverified"]:
        lo = emp["value"] if emp["value"] is not None else emp["range_min"]
        hi = emp["value"] if emp["value"] is not None else emp["range_max"]
        if lo is not None and lo > 50 and rule != "oltre_50_dipendenti":
            errors.append("dipendenti verificati oltre 50: serve exclusion_reason 'oltre_50_dipendenti'")
        if hi == 0 and rule != "nessun_dipendente":
            errors.append("zero dipendenti verificati: serve exclusion_reason 'nessun_dipendente'")
    country = f["country"]["value"]
    if country and country != "Italia" and f["country"]["source_url"] and rule != "fuori_italia":
        errors.append(f"sede '{country}': serve exclusion_reason 'fuori_italia'")

    # Flag
    flags = set(lead["flags"])
    r = f["revenue_eur"]
    rev_found = r["value"] is not None or r["range_min"] is not None
    rev_min = r["value"] if r["value"] is not None else r["range_min"]
    over_50m = rev_min is not None and rev_min > REVENUE_FLAG_THRESHOLD
    if over_50m and "fuori_piani_pubblici_da_verificare" not in flags:
        errors.append("fatturato oltre €50M: manca il flag 'fuori_piani_pubblici_da_verificare'")
    if not over_50m and "fuori_piani_pubblici_da_verificare" in flags:
        errors.append("flag 'fuori_piani_pubblici_da_verificare' senza fatturato oltre €50M")
    # Per un'azienda esclusa (es. oltre 50 dipendenti) il flag sui dipendenti non ha senso
    if not lead["exclusion_reason"] and d["emp_verified"] != ("dipendenti_non_verificati" not in flags):
        errors.append("flag 'dipendenti_non_verificati' non coerente con i dati sui dipendenti")

    # Dati con fonte
    for label, x in (("fatturato", r), ("dipendenti", emp)):
        if (x["value"] is not None or x["range_min"] is not None) and not x["source_url"]:
            errors.append(f"{label} senza URL di fonte")
        if x["value"] is not None and (x["range_min"] is not None or x["range_max"] is not None):
            errors.append(f"{label}: indicare il valore esatto oppure la fascia, non entrambi")
        if x["range_min"] is None and x["range_max"] is not None:
            errors.append(f"{label}: range_max senza range_min")

    # Sottrazioni di evidence_quality coerenti con i dati
    codes = [x["code"] for x in lead["evidence_deductions"]]
    if (not rev_found) != ("fatturato_mancante" in codes):
        errors.append("'fatturato_mancante' va indicato se e solo se il fatturato manca")
    has_primary = any(s["type"] == "primaria" for s in lead["sources"])
    if has_primary == ("nessuna_fonte_primaria" in codes):
        errors.append("'nessuna_fonte_primaria' va indicato se e solo se non c'è una fonte primaria")
    for c in ("fatturato_mancante", "nessuna_fonte_primaria"):
        if codes.count(c) > 1:
            errors.append(f"sottrazione '{c}' ripetuta")

    # Buyer
    b = lead["buyer"]
    rm = b["role_match"]
    if rm in ("primario", "alternativa") and not (b["name"] and b["title"] and b["source_url"]):
        errors.append(f"buyer '{rm}' richiede nome, ruolo e URL di fonte")
    if rm == "solo ruolo" and not (b["title"] and b["source_url"]):
        errors.append("buyer 'solo ruolo' richiede ruolo e URL di fonte")
    if rm == "nome senza ruolo" and not (b["name"] and b["source_url"]):
        errors.append("buyer 'nome senza ruolo' richiede nome e URL di fonte")
    if b["email"]:
        warnings.append("email presente: va bene solo se viene da enrichment o verifica")

    # Segnali
    accessed = {}
    for src in lead["sources"]:
        accessed.setdefault(src["url"], set()).add(src["accessed"])
    for s, age in zip(lead["signals"], d["signal_ages"]):
        row = s["map_row"]
        if age is not None and age < 0:
            errors.append(f"segnale '{row}' con data {s['date']} successiva alla valutazione")
        if (s["date"] is None) != (s["date_basis"] is None):
            errors.append(f"segnale '{row}': date e date_basis vanno indicati insieme")
        if s["date_basis"] == "fonte" and not s["date_as_in_source"]:
            errors.append(f"segnale '{row}': manca date_as_in_source")
        if s["date_basis"] == "consultazione":
            if row not in JOB_AD_ROWS:
                errors.append(f"segnale '{row}': la data di consultazione vale solo per annunci di lavoro")
            if s["date"] not in accessed.get(s["url"], set()):
                errors.append(f"segnale '{row}': data di consultazione {s['date']} non corrisponde all'accesso a {s['url']} in sources")

    # Requisiti dei lead esportabili
    if d["status"] == "QUALIFIED":
        if not lead["signals"]:
            errors.append("lead QUALIFIED senza alcun segnale con URL")
        if not lead["outreach_angle"]:
            errors.append("lead QUALIFIED senza outreach_angle")
        if not lead["legal_pains"]:
            errors.append("lead QUALIFIED senza legal_pains")
        # verify_sources.py ha bisogno della frase copiata dalla fonte per ogni segnale che dà punti
        for s in lead["signals"]:
            if MAP[s["map_row"]][2] and s["date"] and not s.get("evidence_quote"):
                errors.append(f"segnale '{s['map_row']}' con punti senza evidence_quote")

    if lead["tier"] == "REJECT" and lead["exclusion_reason"] is None and score["total"] >= 50:
        errors.append("REJECT senza exclusion_reason con totale >= 50")

    # score_reason
    for k, text in lead["score_reason"].items():
        n = len(text.split())
        if n > MAX_REASON_WORDS:
            errors.append(f"score_reason.{k}: {n} parole, massimo {MAX_REASON_WORDS}")

    return errors, warnings


def errors_by_lead(leads):
    """Errori di schema, di regole e duplicati per ogni lead, senza stampare nulla.
    Usato da export_payload.py per rifiutare un export con dati non validi."""
    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    result, seen_ids, seen_domains = {}, set(), set()
    for i, lead in enumerate(leads):
        label = lead.get("id", f"#{i}") if isinstance(lead, dict) else f"#{i}"
        schema_errors = [e.message for e in validator.iter_errors(lead)]
        if schema_errors:
            result[label] = schema_errors
            continue
        score, d = compute(lead)
        errors, _ = check_rules(lead, score, d)
        if lead["id"] in seen_ids:
            errors.append("id duplicato")
        if lead["domain"] in seen_domains:
            errors.append("dominio duplicato")
        seen_ids.add(lead["id"])
        seen_domains.add(lead["domain"])
        result[label] = errors
    return result


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DATA
    if not path.exists():
        print(f"File non trovato: {path}")
        return 1

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    leads = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(leads, list):
        print("Il file deve contenere un array di lead.")
        return 1

    print(f"File: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    print(f"Lead: {len(leads)}\n")

    total_errors = 0
    seen_ids, seen_domains = set(), set()
    funnel = {"A": 0, "B": 0, "C": 0, "REJECT": 0}
    excluded, missing_buyer, missing_signal, unverified_emp, recent = {}, 0, 0, 0, 0

    for i, lead in enumerate(leads):
        label = lead.get("id", f"#{i}") if isinstance(lead, dict) else f"#{i}"
        schema_errors = sorted(validator.iter_errors(lead), key=lambda e: list(e.path))
        if schema_errors:
            total_errors += len(schema_errors)
            print(f"✗ {label}: schema non valido")
            for e in schema_errors:
                where = "/".join(str(p) for p in e.path) or "(radice)"
                print(f"    - {where}: {e.message}")
            continue

        score, d = compute(lead)
        errors, warnings = check_rules(lead, score, d)
        if lead["id"] in seen_ids:
            errors.append("id duplicato")
        if lead["domain"] in seen_domains:
            errors.append("dominio duplicato")
        seen_ids.add(lead["id"])
        seen_domains.add(lead["domain"])

        mark = "✗" if errors else "✓"
        s = score
        print(
            f"{mark} {label}: {lead['tier']} {lead['score']['total']} "
            f"(fit {s['company_fit']}, compl {s['legal_complexity']}, segnali {s['buying_signals']}, "
            f"buyer {s['buyer_availability']}, prove {s['evidence_quality']})"
        )
        for e in errors:
            print(f"    - ERRORE: {e}")
        for w in warnings:
            print(f"    - avviso: {w}")
        total_errors += len(errors)

        funnel[d["tier"]] += 1
        if lead["exclusion_reason"]:
            r = lead["exclusion_reason"]["rule"]
            excluded[r] = excluded.get(r, 0) + 1
        if lead["buyer"]["role_match"] == "unclear":
            missing_buyer += 1
        if not lead["signals"]:
            missing_signal += 1
        if not d["emp_verified"]:
            unverified_emp += 1
        if score["buying_signals"] > 0:
            recent += 1

    n = len(leads)
    print("\nFunnel")
    print(f"  Candidati valutati:        {n}")
    print(f"  Qualificati (A + B):       {funnel['A'] + funnel['B']}  (A {funnel['A']}, B {funnel['B']})")
    print(f"  Riserva (C):               {funnel['C']}")
    print(f"  Scartati:                  {funnel['REJECT']}")
    for r, c in sorted(excluded.items()):
        print(f"    di cui esclusi per {r}: {c}")
    print(f"  Buyer non trovato:         {missing_buyer}")
    print(f"  Nessun segnale con fonte:  {missing_signal}")
    print(f"  Dipendenti non verificati: {unverified_emp}")
    print(f"  Con segnale datato ≤18 mesi: {recent}")

    # Contatti (data/contacts.json, fuori dal repository): solo se il file c'è
    contacts = load_contacts()
    if contacts and path.resolve() == DEFAULT_DATA:
        c_errors, _, st = check_contacts(leads, contacts)
        print("\nContatti")
        if st:
            print(f"  Lead con contatti:         {st['leads']}")
            print(f"  Telefono aziendale:        {st['company_phone']}")
            print(f"  Email del buyer:           {st['buyer_email']}")
            print(f"  Cellulare del buyer:       {st['buyer_mobile']}")
        for e in c_errors:
            print(f"    - ERRORE: {e}")
        total_errors += len(c_errors)
    print(f"\n{'OK' if total_errors == 0 else f'{total_errors} errori'}")
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())
