"""Invia i lead qualificati al webhook locale di n8n.

Uso:
    python scripts/push_n8n.py            # invia
    python scripts/push_n8n.py --dry-run  # mostra cosa invierebbe, senza inviare
    python scripts/push_n8n.py --handoff  # alla fine avvia anche HANDOFF_SALES

Legge data/qualified_leads.json (prodotto da export_payload.py) e manda un lead per
richiesta, in POST JSON, all'indirizzo in N8N_WEBHOOK_URL (variabile d'ambiente o file
.env). Se manca usa http://localhost:5678/webhook/iusful/qualified-lead.
Ogni lead viene ritentato al massimo una volta; l'esito di ogni invio finisce in
data/push_log.json. Alla fine invia anche data/run_summary.json al flusso GTM_RUN_SUMMARY
(/webhook/iusful/run-summary sullo stesso n8n), che scrive il report del funnel su Notion.
I contatti (data/contacts.json, fuori dal repository) si aggiungono a ogni lead solo al
momento dell'invio: nessun file del repository li contiene.
Esce con codice 1 se almeno un invio fallisce.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contacts import for_crm, load as load_contacts  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
IN_JSON = ROOT / "data" / "qualified_leads.json"
SUMMARY_JSON = ROOT / "data" / "run_summary.json"
LOG = ROOT / "data" / "push_log.json"
DEFAULT_URL = "http://localhost:5678/webhook/iusful/qualified-lead"
TIMEOUT_S = 10
ATTEMPTS = 2


def webhook_url():
    if os.environ.get("N8N_WEBHOOK_URL"):
        return os.environ["N8N_WEBHOOK_URL"]
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("N8N_WEBHOOK_URL=") and line.split("=", 1)[1].strip():
                return line.split("=", 1)[1].strip()
    return DEFAULT_URL


def post(url, payload):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return resp.status, body[:500]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    dry_run = "--dry-run" in sys.argv
    if not IN_JSON.exists():
        print("Manca data/qualified_leads.json: esegui prima python scripts/export_payload.py")
        return 1
    leads = json.loads(IN_JSON.read_text(encoding="utf-8"))
    contacts = load_contacts()
    for lead in leads:
        lead["contacts"] = for_crm(contacts, lead["id"])
    url = webhook_url()
    print(f"Webhook: {url}")
    print(f"Lead da inviare: {len(leads)}{' (prova, nessun invio)' if dry_run else ''}\n")

    log = []
    for lead in leads:
        if dry_run:
            c = lead["contacts"] or {}
            have = [k for k in ("company_phone", "buyer_email", "buyer_mobile") if c.get(k)]
            print(f"  [prova] {lead['tier']} {lead['score_total']:>3}  {lead['company_name']}  contatti: {', '.join(have) or 'nessuno'}")
            continue
        entry = send(url, lead, lead["id"])
        print(f"  {'✓' if entry['ok'] else '✗'} {lead['company_name']}: {entry['status']} {entry['response'][:120]}")
        log.append(entry)

    summary_url = url.split("/webhook/", 1)[0] + "/webhook/iusful/run-summary"
    if SUMMARY_JSON.exists():
        summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
        if dry_run:
            print(f"\n  [prova] report del funnel a {summary_url}: {summary['qualified']} qualificati su {summary['candidates']}")
        else:
            entry = send(summary_url, summary, "run_summary")
            print(f"\n  {'✓' if entry['ok'] else '✗'} Report del funnel: {entry['status']} {entry['response'][:160]}")
            log.append(entry)

    # --handoff: dopo l'invio avvia HANDOFF_SALES, che porta in "Pronto per sales" i Tier A verificati
    if "--handoff" in sys.argv:
        handoff_url = url.split("/webhook/", 1)[0] + "/webhook/iusful/handoff"
        if dry_run:
            print(f"  [prova] passaggio al sales a {handoff_url}")
        else:
            entry = send(handoff_url, {}, "handoff")
            print(f"  {'✓' if entry['ok'] else '✗'} Passaggio al sales: {entry['status']} {entry['response'][:120]}")
            log.append(entry)

    failures = sum(not e["ok"] for e in log)
    if not dry_run:
        LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nInvii riusciti: {len(log) - failures}, falliti: {failures}. Esito in {LOG.relative_to(ROOT)}")
    return 1 if failures else 0


def send(url, payload, entry_id):
    """Una POST con al massimo un nuovo tentativo; restituisce la riga per il log."""
    entry = {"id": entry_id, "sent_at": datetime.now().isoformat(timespec="seconds")}
    for attempt in range(1, ATTEMPTS + 1):
        try:
            status, body = post(url, payload)
            entry.update(ok=200 <= status < 300, status=status, response=body, attempts=attempt)
            return entry
        except urllib.error.HTTPError as e:
            entry.update(ok=False, status=e.code, response=e.read().decode("utf-8", errors="replace")[:500], attempts=attempt)
        except (urllib.error.URLError, TimeoutError) as e:
            entry.update(ok=False, status=None, response=str(e), attempts=attempt)
        if attempt < ATTEMPTS:
            time.sleep(2)
    return entry


if __name__ == "__main__":
    sys.exit(main())
