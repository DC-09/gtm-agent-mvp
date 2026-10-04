"""Importa l'ultimo export CSV di Clay dalla cartella Download e fa una prima scrematura.

Uso:
    python scripts/import_clay.py            # cerca in ~/Downloads l'export Clay più recente (ultime 24 ore)
    python scripts/import_clay.py file.csv   # usa un file preciso

Copia il file in data/clay/find_companies_risultati.csv e scrive data/clay/candidati_da_clay.json
con i candidati da ricercare. Scarta solo ciò che è chiaramente fuori perimetro (docs/icp.md §5):
fascia di dipendenti sopra 50, sede fuori Italia, società quotata, studi legali.
Tutto il resto lo valuta l'agente con prompts/agente.md.
"""

import csv
import json
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS = Path.home() / "Downloads"
RAW = ROOT / "data" / "clay" / "find_companies_risultati.csv"
OUT = ROOT / "data" / "clay" / "candidati_da_clay.json"
LEADS = ROOT / "data" / "leads.json"
# Solo gli studi legali: agenzie e software house fanno parte del target (docs/icp.md §3,
# "Agenzie strutturate" e "Servizi digitali"); fino al 4 ottobre 2026 venivano scartate per errore
EXCLUDE_WORDS = re.compile(r"\b(studio legale|avvocati|law firm)\b", re.I)


def find_export():
    """L'export Clay più recente delle ultime 24 ore: Clay lo chiama "<tabella>-<vista>-export-<numero>.csv".
    Guarda solo i file con quel nome, per non aprire altri CSV della cartella Download."""
    since = time.time() - 24 * 3600
    files = sorted((p for p in DOWNLOADS.glob("*-export-*.csv") if p.stat().st_mtime >= since),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    for p in files:
        with p.open(encoding="utf-8-sig", errors="replace") as fh:
            header = next(csv.reader(fh), [])
        if {"Name", "Size"} <= set(header):
            return p
    return None


def col(row, *names):
    for n in names:
        for k, v in row.items():
            if k and k.strip().lower() == n.lower() and v:
                return v.strip()
    return ""


def domain_of(url):
    d = re.sub(r"^https?://", "", url.strip().lower()).split("/")[0]
    return d[4:] if d.startswith("www.") else d


def size_range(text):
    """'11-50 employees' -> (11, 50); '10,001+ employees' -> (10001, None)."""
    nums = [int(n.replace(",", "").replace(".", "")) for n in re.findall(r"\d[\d,.]*", text or "")]
    if not nums:
        return None, None
    return nums[0], (nums[1] if len(nums) > 1 else None)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else find_export()
    if not src or not src.exists():
        print(f"Nessun export Clay trovato in {DOWNLOADS} nelle ultime 24 ore (serve un CSV con colonne Name e Size).")
        return 1
    RAW.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, RAW)
    print(f"Export: {src.name} → {RAW.relative_to(ROOT)}")

    known = {l["domain"] for l in json.loads(LEADS.read_text(encoding="utf-8"))}
    with RAW.open(encoding="utf-8-sig", errors="replace") as fh:
        rows = list(csv.DictReader(fh))

    kept, dropped = [], []
    for r in rows:
        name = col(r, "Name")
        url = col(r, "Domain", "Website", "Url", "Company Domain")
        dom = domain_of(url) if url else ""
        lo, hi = size_range(col(r, "Size"))
        country = col(r, "Country")
        location = col(r, "Location")
        ctype = col(r, "Type")
        desc = col(r, "Description")
        reason = None
        if dom and dom in known:
            reason = "già valutata"
        elif lo is not None and lo > 50:
            reason = f"fascia {col(r, 'Size')}"
        elif country and country.lower() not in ("italy", "italia"):
            reason = f"paese {country}"
        elif ctype.lower() == "public company":
            reason = "società quotata"
        elif EXCLUDE_WORDS.search(desc) or EXCLUDE_WORDS.search(name):
            reason = "studio legale"
        item = {"name": name, "domain": dom, "linkedin": col(r, "LinkedIn", "Linkedin Url", "LinkedIn URL"),
                "size": col(r, "Size"), "size_min": lo, "size_max": hi, "location": location,
                "type": ctype, "industry": col(r, "Primary Industry"), "description": desc,
                # Colonne di "Find contacts at company" (filtro Founder, Owner, Partner, C-suite):
                # vanno controllate, Clay a volte restituisce un ruolo diverso da quello chiesto
                "clay_person": {"name": col(r, "Name People"), "title": col(r, "Title People"),
                                "linkedin": col(r, "Url People")} if col(r, "Name People") else None}
        (dropped if reason else kept).append({**item, "scartata_perche": reason} if reason else item)

    OUT.write_text(json.dumps(kept, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Righe: {len(rows)}; da ricercare: {len(kept)}; scartate subito: {len(dropped)}")
    for d in dropped:
        print(f"  - {d['name']}: {d['scartata_perche']}")
    missing_domain = sum(not k["domain"] for k in kept)
    if missing_domain:
        print(f"Attenzione: {missing_domain} righe senza dominio; nell'export mancano forse le colonne nascoste.")
    print(f"Candidati in {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
