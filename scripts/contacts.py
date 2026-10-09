"""Contatti dei lead qualificati: telefono generico dell'azienda dal suo sito, email nominativa e
cellulare del buyer da Clay (docs/decisions.md, Contatti).

I contatti sono dati personali: stanno in data/contacts.json, escluso dal repository, e arrivano
al CRM solo attraverso push_n8n.py. Nessun file del repository li contiene.
"""

import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
CONTACTS = ROOT / "data" / "contacts.json"
SCHEMA = ROOT / "schemas" / "contacts.schema.json"

# Indirizzi di ruolo: non sono email nominative
ROLE_LOCAL_PARTS = {"info", "commerciale", "sales", "vendite", "amministrazione", "contatti", "contact",
                    "hello", "ciao", "support", "assistenza", "ordini", "orders", "shop", "privacy",
                    "marketing", "segreteria", "office", "admin", "customer", "customercare", "servizioclienti"}


def load():
    if not CONTACTS.exists():
        return {}
    return json.loads(CONTACTS.read_text(encoding="utf-8"))


def digits(phone):
    """Numero nazionale senza prefisso e separatori: '+39 02 1234567' -> '021234567'."""
    d = re.sub(r"\D", "", phone)
    if d.startswith("0039"):
        d = d[4:]
    elif d.startswith("39") and len(d) > 10:
        d = d[2:]
    return d


def base_domain(host):
    host = host.lower().split("@")[-1]
    host = host[4:] if host.startswith("www.") else host
    parts = host.split(".")
    return ".".join(parts[-3:]) if len(parts) >= 3 and parts[-2] in {"pc", "co", "com"} else ".".join(parts[-2:])


def check(leads, contacts):
    """Errori e avvisi sui contatti, più i conteggi per il riepilogo."""
    errors, warnings = [], []
    by_id = {l["id"]: l for l in leads}
    for e in Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).iter_errors(contacts):
        errors.append("schema: " + "/".join(str(p) for p in e.path) + f": {e.message}")
    if errors:
        return errors, warnings, {}

    stats = {"leads": 0, "company_phone": 0, "buyer_email": 0, "buyer_mobile": 0}
    for lead_id, c in contacts.items():
        lead = by_id.get(lead_id)
        if lead is None:
            errors.append(f"{lead_id}: nessun lead con questo id")
            continue
        if lead["status"] != "QUALIFIED":
            errors.append(f"{lead_id}: contatti solo per i lead qualificati (status {lead['status']})")
        stats["leads"] += 1
        if c["company_phone"]:
            stats["company_phone"] += 1
            if base_domain(c["company_phone"]["source_url"].split("/")[2]) != base_domain(lead["domain"]):
                errors.append(f"{lead_id}: il telefono aziendale deve venire dal sito dell'azienda")
        if c["buyer_email"]:
            stats["buyer_email"] += 1
            email = c["buyer_email"]["value"].lower()
            local = email.split("@")[0]
            if local in ROLE_LOCAL_PARTS:
                errors.append(f"{lead_id}: '{local}@' è un indirizzo di ruolo, non un'email nominativa")
            if base_domain(email) != base_domain(lead["domain"]) and not c["buyer_email"]["note"]:
                errors.append(f"{lead_id}: dominio dell'email diverso da quello dell'azienda, senza nota che lo spieghi")
            if not lead["buyer"]["name"]:
                errors.append(f"{lead_id}: email senza un buyer con nome")
        if c["buyer_mobile"]:
            stats["buyer_mobile"] += 1
            if not digits(c["buyer_mobile"]["value"]).startswith("3"):
                errors.append(f"{lead_id}: il cellulare deve iniziare per 3")
            if not lead["buyer"]["name"]:
                errors.append(f"{lead_id}: cellulare senza un buyer con nome")
    return errors, warnings, stats


def for_crm(contacts, lead_id):
    """Campi da mandare a n8n per un lead: solo i valori, senza fonti interne."""
    c = contacts.get(lead_id)
    if not c:
        return None
    return {
        "company_phone": c["company_phone"]["value"] if c["company_phone"] else None,
        "buyer_email": c["buyer_email"]["value"] if c["buyer_email"] else None,
        "buyer_mobile": c["buyer_mobile"]["value"] if c["buyer_mobile"] else None,
        "source": ", ".join(x for x in [
            "telefono dal sito aziendale" if c["company_phone"] else "",
            f"email da Clay ({c['buyer_email']['retrieved']})" if c["buyer_email"] else "",
            f"cellulare da Clay ({c['buyer_mobile']['retrieved']})" if c["buyer_mobile"] else "",
        ] if x),
    }
