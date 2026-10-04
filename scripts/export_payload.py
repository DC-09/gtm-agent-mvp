"""Prepara i lead qualificati (Tier A e B) per n8n e per il CRM.

Uso:
    python scripts/export_payload.py [file.json]

Legge data/leads.json (o il file indicato), lo controlla con le stesse regole di
validate_leads.py e si ferma se trova anche un solo errore: un export parziale
nasconderebbe il problema. Poi scrive:
- data/qualified_leads.json: un oggetto per lead, il formato che push_n8n.py invia a n8n;
- data/qualified_leads.csv: le stesse righe, da importare a mano in qualsiasi CRM
  se il collegamento automatico non è disponibile;
- data/run_summary.json: i numeri del funnel su tutti i lead valutati, scartati compresi.
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_leads import DEFAULT_DATA, MAP, ROOT, compute, errors_by_lead  # noqa: E402

OUT_JSON = ROOT / "data" / "qualified_leads.json"
OUT_CSV = ROOT / "data" / "qualified_leads.csv"
OUT_SUMMARY = ROOT / "data" / "run_summary.json"
VERIFICATION = ROOT / "data" / "verification.json"


def funnel_summary(leads, verification=None):
    """Numeri del funnel su tutti i lead valutati, anche scartati, per GTM_RUN_SUMMARY."""
    tiers = {"A": 0, "B": 0, "C": 0, "REJECT": 0}
    reasons, missing_buyer, unverified, recent = {}, 0, 0, 0
    for lead in leads:
        score, d = compute(lead)
        tiers[d["tier"]] += 1
        if d["tier"] == "REJECT":
            r = lead["exclusion_reason"]["rule"] if lead["exclusion_reason"] else "score_sotto_50"
            reasons[r] = reasons.get(r, 0) + 1
        missing_buyer += lead["buyer"]["role_match"] == "unclear"
        unverified += not d["emp_verified"] and not lead["exclusion_reason"]
        recent += score["buying_signals"] > 0
    n = len(leads)
    qualified = tiers["A"] + tiers["B"]
    today = date.today().isoformat()
    return {
        "run_name": f"Esecuzione del {today}: {n} candidati",
        "date": today,
        "candidates": n,
        "qualified": qualified,
        "tier_a": tiers["A"],
        "tier_b": tiers["B"],
        "tier_c": tiers["C"],
        "rejected": tiers["REJECT"],
        "rejection_reasons": reasons,
        "missing_buyer": missing_buyer,
        "unverified_employees": unverified,
        "with_recent_signal": recent,
        "to_review": sum(v["status"] == "da_rivedere" for v in (verification or {}).values()),
        "qualification_rate": round(qualified / n * 100, 1) if n else 0,
        "weekly_notes": weekly_notes(today),
    }


def weekly_notes(today):
    """Sintesi scritta dall'agente nel controllo settimanale (prompts/settimanale.md), se c'è."""
    path = ROOT / "data" / "weekly" / f"sintesi_{today}.txt"
    return path.read_text(encoding="utf-8").strip()[:1900] if path.exists() else ""


def employees_text(emp):
    if emp["source_url"] and not emp["source_says_unverified"]:
        if emp["value"] is not None:
            return str(emp["value"])
        if emp["range_min"] is not None:
            hi = emp["range_max"]
            return f"{emp['range_min']}-{hi}" if hi is not None else f"oltre {emp['range_min'] - 1}"
    return "non verificati"


def primary_signal(lead):
    """Il segnale di attività datato che vale di più; se non c'è, il primo segnale."""
    _, d = compute(lead)
    best, best_key = None, None
    for s, age in zip(lead["signals"], d["signal_ages"]):
        _, strength, is_event = MAP[s["map_row"]]
        if not is_event or age is None or age < 0 or age > 18:
            continue
        key = (strength == "forte", -age)
        if best_key is None or key > best_key:
            best, best_key = s, key
    return best or (lead["signals"][0] if lead["signals"] else None)


def to_payload(lead, verification):
    sig = primary_signal(lead)
    f = lead["facts"]
    return {
        "id": lead["id"],
        "company_name": lead["company_name"],
        "domain": lead["domain"],
        "website": f"https://{lead['domain']}",
        "city": f["city"]["value"],
        "business_model": f["business_model"]["value"],
        "employees": employees_text(f["employees"]),
        "tier": lead["tier"],
        "score_total": lead["score"]["total"],
        "score": lead["score"],
        "primary_signal": None if sig is None else {
            "fact": sig["observed_fact"], "url": sig["url"], "date": sig["date"],
        },
        "evidence_url": sig["url"] if sig else lead["sources"][0]["url"],
        "legal_pains": [p["pain"] for p in lead["legal_pains"]],
        "buyer": {
            "name": lead["buyer"]["name"],
            "title": lead["buyer"]["title"],
            "source_url": lead["buyer"]["source_url"],
            "role_match": lead["buyer"]["role_match"],
        },
        "outreach_angle": lead["outreach_angle"],
        "verification": {
            "status": verification["status"],
            "reason": "; ".join(verification["reasons"] + verification["notes"]) or "Fonti e buyer confermati",
        },
        "flags": lead["flags"],
        "evaluation_date": lead["evaluation_date"],
        "notes": lead.get("notes"),
    }


CSV_COLUMNS = [
    "company_name", "domain", "website", "city", "business_model", "employees", "tier", "score_total",
    "primary_signal", "primary_signal_date", "evidence_url", "legal_pains", "buyer_name", "buyer_title",
    "buyer_source_url", "outreach_angle", "verification", "verification_reason", "flags", "evaluation_date",
]


def to_csv_row(p):
    sig = p["primary_signal"] or {}
    return {
        "company_name": p["company_name"], "domain": p["domain"], "website": p["website"],
        "city": p["city"] or "", "business_model": p["business_model"] or "", "employees": p["employees"],
        "tier": p["tier"], "score_total": p["score_total"],
        "primary_signal": sig.get("fact", ""), "primary_signal_date": sig.get("date") or "",
        "evidence_url": p["evidence_url"], "legal_pains": "; ".join(p["legal_pains"]),
        "buyer_name": p["buyer"]["name"] or "", "buyer_title": p["buyer"]["title"] or "",
        "buyer_source_url": p["buyer"]["source_url"] or "", "outreach_angle": p["outreach_angle"] or "",
        "verification": p["verification"]["status"], "verification_reason": p["verification"]["reason"],
        "flags": "; ".join(p["flags"]), "evaluation_date": p["evaluation_date"],
    }


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DATA
    leads = json.loads(path.read_text(encoding="utf-8"))

    problems = {k: v for k, v in errors_by_lead(leads).items() if v}
    if problems:
        print("Export annullato: ci sono lead non validi. Esegui python scripts/validate_leads.py per i dettagli.")
        for label, errs in problems.items():
            print(f"  - {label}: {len(errs)} errori")
        return 1

    # La verifica delle fonti deve esistere ed essere successiva all'ultima modifica dei lead
    verification = json.loads(VERIFICATION.read_text(encoding="utf-8")) if VERIFICATION.exists() else {}
    stale = VERIFICATION.exists() and VERIFICATION.stat().st_mtime < path.stat().st_mtime
    missing = [l["id"] for l in leads if l["status"] == "QUALIFIED" and l["id"] not in verification]
    if missing or stale:
        print("Export annullato: verifica delle fonti mancante o più vecchia dei lead. "
              "Esegui prima python scripts/verify_sources.py")
        if missing:
            print(f"  senza verifica: {', '.join(missing)}")
        return 1

    qualified = [to_payload(l, verification[l["id"]]) for l in leads if l["status"] == "QUALIFIED"]
    qualified.sort(key=lambda p: (-p["score_total"], p["company_name"]))

    OUT_JSON.write_text(json.dumps(qualified, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        w.writeheader()
        w.writerows(to_csv_row(p) for p in qualified)

    summary = funnel_summary(leads, verification)
    OUT_SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Lead valutati: {len(leads)}; qualificati esportati: {len(qualified)}")
    for p in qualified:
        v = "verifica superata" if p["verification"]["status"] == "superata" else "DA RIVEDERE"
        print(f"  {p['tier']} {p['score_total']:>3}  {p['company_name']}  ({v})")
    print(f"Funnel: {summary['qualified']} qualificati su {summary['candidates']} "
          f"({summary['qualification_rate']}%), scartati {summary['rejected']} {summary['rejection_reasons']}")
    print(f"Scritti {OUT_JSON.relative_to(ROOT)}, {OUT_CSV.relative_to(ROOT)} e {OUT_SUMMARY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
