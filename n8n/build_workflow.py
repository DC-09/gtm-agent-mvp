"""Genera i tre flussi n8n del progetto in n8n/workflows/:

- qualified_lead_ingest.json (QUALIFIED_LEAD_INGEST): riceve un lead, lo filtra e lo crea o
  aggiorna nel CRM Notion, con i contatti se ci sono, registrando l'interazione;
- gtm_run_summary.json (GTM_RUN_SUMMARY): riceve i numeri del funnel e scrive un report su Notion;
- handoff_sales.json (HANDOFF_SALES): porta in "Pronto per sales" i Tier A con verifica
  superata (o rivista a mano) e registra il passaggio.

Uso: python n8n/build_workflow.py ['{"id": "<id credenziale Notion>", "name": "<nome>"}']
Senza argomento i nodi Notion restano senza credenziale (da scegliere in n8n).
Ogni JSON si importa con: n8n import:workflow --input=n8n/workflows/<file>.json
"""

import json
import sys

AZIENDE_DB = "47bd791712bb4d30acce6f2af257a433"
PERSONE_DB = "9ed966106914451594f22af8d009d1e3"
INTERAZIONI_DB = "f95fe1d7744640c3aadeabc8aca2ce45"
REPORT_DB = "c80f0cbb73a9400593fee933737cd5ca"
NOTION = "https://api.notion.com/v1"
CRED = json.loads(sys.argv[1]) if len(sys.argv) > 1 else None  # {"id": ..., "name": ...}

PREPARE_JS = r"""// Prepara le proprietà Notion a partire dal lead ricevuto.
// update_properties non contiene "Stato": un aggiornamento non deve far tornare indietro
// un lead che nel CRM è già passato a "Pronto per sales" o "Contattato".
const b = $json.body;
const txt = (s) => [{ text: { content: String(s ?? '').slice(0, 2000) } }];
const day = (s) => !s ? null : s.length === 4 ? `${s}-01-01` : s.length === 7 ? `${s}-01` : s;
const signalDate = day(b.primary_signal && b.primary_signal.date);

const common = {
  'Azienda': { title: txt(b.company_name) },
  'Dominio': { rich_text: txt(b.domain) },
  'Sito': { url: b.website || null },
  'Tier': { select: { name: b.tier } },
  'Score': { number: b.score_total },
  'Città': { rich_text: txt(b.city) },
  'Dipendenti': { rich_text: txt(b.employees) },
  'Segnale principale': { rich_text: txt(b.primary_signal && b.primary_signal.fact) },
  'Data segnale': { date: signalDate ? { start: signalDate } : null },
  'Fonte segnale': { url: b.evidence_url || null },
  'Bisogni legali': { rich_text: txt((b.legal_pains || []).join('; ')) },
  'Angle outreach': { rich_text: txt(b.outreach_angle) },
  'Flag': { multi_select: (b.flags || []).map((name) => ({ name })) },
  'Data valutazione': { date: { start: b.evaluation_date } },
};
if (b.business_model) common['Modello'] = { select: { name: b.business_model } };

// Contatti (solo se trovati: un aggiornamento senza contatti non cancella quelli già nel CRM)
const c = b.contacts || {};
if (c.company_phone) common['Telefono'] = { phone_number: c.company_phone };
const person = {};
if (c.buyer_email) person['Email'] = { email: c.buyer_email };
if (c.buyer_mobile) person['Cellulare'] = { phone_number: c.buyer_mobile };
if (c.source) person['Fonte contatto'] = { rich_text: txt(c.source) };

// Esito di scripts/verify_sources.py. In aggiornamento non sovrascrive "Rivista a mano".
const v = b.verification || {};
const verification = {
  'Verifica': { select: { name: v.status === 'da_rivedere' ? 'Da rivedere' : 'Superata' } },
  'Motivo verifica': { rich_text: txt(v.reason) },
};

return {
  json: {
    body: b,
    create_properties: { ...common, ...verification, 'Stato': { select: { name: 'Qualificato' } } },
    update_properties: common,
    verification_properties: verification,
    person_properties: person,
    has_person_contacts: Object.keys(person).length > 0,
  },
};
"""

ACTION = "$('Cerca azienda per dominio').item.json.results.length > 0 ? 'aggiornato' : 'creato'"
LEAD = "$('Prepara proprietà CRM').item.json.body"


def http(node_id, name, method, url, body_expr, pos):
    node = {
        "parameters": {
            "method": method,
            "url": url,
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "notionApi",
            "sendHeaders": True,
            "headerParameters": {"parameters": [{"name": "Notion-Version", "value": "2022-06-28"}]},
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify(" + body_expr + ") }}",
            "options": {},
        },
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": pos,
    }
    if CRED:
        node["credentials"] = {"notionApi": CRED}
    return node


def cond(cid, left, right, op_type, op, single=False):
    c = {"id": cid, "leftValue": left, "rightValue": right, "operator": {"type": op_type, "operation": op}}
    if single:
        c["operator"]["singleValue"] = True
    return c


def if_node(node_id, name, conditions, pos):
    return {
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose"},
                "conditions": conditions,
                "combinator": "and",
            },
            "options": {},
        },
        "id": node_id, "name": name, "type": "n8n-nodes-base.if", "typeVersion": 2, "position": pos,
    }


def respond(node_id, name, body_expr, code, pos):
    return {
        "parameters": {"respondWith": "json", "responseBody": "={{ JSON.stringify(" + body_expr + ") }}",
                       "options": {"responseCode": code}},
        "id": node_id, "name": name, "type": "n8n-nodes-base.respondToWebhook", "typeVersion": 1.1, "position": pos,
    }


nodes = [
    {
        "parameters": {"httpMethod": "POST", "path": "iusful/qualified-lead", "responseMode": "responseNode", "options": {}},
        "id": "a1f0c6d2-1b1e-4c55-9d0a-000000000001", "name": "Ricevi lead", "type": "n8n-nodes-base.webhook",
        "typeVersion": 2, "position": [0, 0], "webhookId": "5b2f4a8e-7c1d-4e2a-9f3b-1a2b3c4d5e6f",
    },
    if_node("a1f0c6d2-1b1e-4c55-9d0a-000000000002", "Valido e score >= 65?", [
        cond("c1", "={{ $json.body.score_total }}", 65, "number", "gte"),
        cond("c2", "={{ $json.body.company_name }}", "", "string", "notEmpty", True),
        cond("c3", "={{ $json.body.domain }}", "", "string", "notEmpty", True),
        cond("c4", "={{ $json.body.evidence_url }}", "http", "string", "startsWith"),
    ], [240, 0]),
    {
        "parameters": {"jsCode": PREPARE_JS},
        "id": "a1f0c6d2-1b1e-4c55-9d0a-000000000005", "name": "Prepara proprietà CRM", "type": "n8n-nodes-base.code",
        "typeVersion": 2, "position": [480, -120],
    },
    http("a1f0c6d2-1b1e-4c55-9d0a-000000000006", "Cerca azienda per dominio", "POST",
         f"{NOTION}/databases/{AZIENDE_DB}/query",
         "{ filter: { property: 'Dominio', rich_text: { equals: $json.body.domain } }, page_size: 1 }", [720, -120]),
    if_node("a1f0c6d2-1b1e-4c55-9d0a-000000000007", "Esiste già?", [
        cond("e1", "={{ $json.results.length }}", 0, "number", "gt"),
    ], [960, -120]),
    http("a1f0c6d2-1b1e-4c55-9d0a-000000000008", "Aggiorna azienda", "PATCH",
         "={{ 'https://api.notion.com/v1/pages/' + $json.results[0].id }}",
         "{ properties: Object.assign({}, $('Prepara proprietà CRM').item.json.update_properties,"
         " (($json.results[0].properties['Verifica'] || {}).select || {}).name === 'Rivista a mano'"
         " ? {} : $('Prepara proprietà CRM').item.json.verification_properties) }", [1200, -240]),
    http("a1f0c6d2-1b1e-4c55-9d0a-000000000009", "Crea azienda", "POST", f"{NOTION}/pages",
         "{ parent: { database_id: '" + AZIENDE_DB + "' }, properties: $('Prepara proprietà CRM').item.json.create_properties }",
         [1200, 0]),
    http("a1f0c6d2-1b1e-4c55-9d0a-000000000010", "Crea persona", "POST", f"{NOTION}/pages",
         "{ parent: { database_id: '" + PERSONE_DB + "' }, properties: {"
         " 'Nome': { title: [{ text: { content: " + LEAD + ".buyer.name || 'Buyer non identificato' } }] },"
         " 'Ruolo': { rich_text: [{ text: { content: " + LEAD + ".buyer.title || '' } }] },"
         " 'Azienda': { relation: [{ id: $json.id }] },"
         " 'Ruolo nel buying': { select: { name: " + LEAD + ".buyer.role_match } },"
         " 'Fonte': { url: " + LEAD + ".buyer.source_url || null },"
         " ...$('Prepara proprietà CRM').item.json.person_properties } }",
         [1440, 120]),
    http("a1f0c6d2-1b1e-4c55-9d0a-000000000011", "Registra interazione", "POST", f"{NOTION}/pages",
         "{ parent: { database_id: '" + INTERAZIONI_DB + "' }, properties: {"
         " 'Cosa': { title: [{ text: { content: 'Ricevuto da n8n: ' + (" + ACTION + ") + ' (Tier ' + " + LEAD + ".tier + ', ' + " + LEAD + ".score_total + ')' } }] },"
         " 'Azienda': { relation: [{ id: $json.id }] },"
         " 'Tipo': { select: { name: 'Nota' } },"
         " 'Chi': { select: { name: 'n8n' } },"
         " 'Data': { date: { start: $now.toISODate() } } } }",
         [1680, -120]),
    # Azienda già nel CRM: i contatti nuovi vanno sulla persona collegata, se c'è
    if_node("a1f0c6d2-1b1e-4c55-9d0a-000000000012", "Contatti persona?", [
        cond("p1", "={{ $('Prepara proprietà CRM').item.json.has_person_contacts }}", "", "boolean", "true", True),
    ], [1440, -400]),
    http("a1f0c6d2-1b1e-4c55-9d0a-000000000013", "Cerca persona", "POST",
         f"{NOTION}/databases/{PERSONE_DB}/query",
         "{ filter: { property: 'Azienda', relation: { contains: $('Cerca azienda per dominio').item.json.results[0].id } }, page_size: 1 }",
         [1680, -400]),
    if_node("a1f0c6d2-1b1e-4c55-9d0a-000000000014", "Persona trovata?", [
        cond("p2", "={{ $json.results.length }}", 0, "number", "gt"),
    ], [1920, -400]),
    http("a1f0c6d2-1b1e-4c55-9d0a-000000000015", "Aggiorna contatti persona", "PATCH",
         "={{ 'https://api.notion.com/v1/pages/' + $json.results[0].id }}",
         "{ properties: $('Prepara proprietà CRM').item.json.person_properties }", [2160, -400]),
    respond("a1f0c6d2-1b1e-4c55-9d0a-000000000003", "Accettato",
            "{ accepted: true, company: " + LEAD + ".company_name, tier: " + LEAD + ".tier, score: " + LEAD
            + ".score_total, crm: " + ACTION + " }", 200, [1920, -120]),
    respond("a1f0c6d2-1b1e-4c55-9d0a-000000000004", "Scartato",
            "{ accepted: false, reason: 'rejected_by_automation', company: $json.body.company_name || null, score: $json.body.score_total ?? null }",
            422, [480, 160]),
]


def link(*targets):
    return [[{"node": t, "type": "main", "index": 0} for t in targets]]


connections = {
    "Ricevi lead": {"main": link("Valido e score >= 65?")},
    "Valido e score >= 65?": {"main": link("Prepara proprietà CRM") + link("Scartato")},
    "Prepara proprietà CRM": {"main": link("Cerca azienda per dominio")},
    "Cerca azienda per dominio": {"main": link("Esiste già?")},
    "Esiste già?": {"main": link("Aggiorna azienda") + link("Crea azienda")},
    "Aggiorna azienda": {"main": link("Registra interazione", "Contatti persona?")},
    "Contatti persona?": {"main": link("Cerca persona")},
    "Cerca persona": {"main": link("Persona trovata?")},
    "Persona trovata?": {"main": link("Aggiorna contatti persona")},
    "Crea azienda": {"main": [[{"node": "Registra interazione", "type": "main", "index": 0},
                               {"node": "Crea persona", "type": "main", "index": 0}]]},
    "Registra interazione": {"main": link("Accettato")},
}

def save(wf_id, name, wf_nodes, wf_connections, filename):
    wf = {"id": wf_id, "active": False, "name": name, "nodes": wf_nodes, "connections": wf_connections,
          "settings": {"executionOrder": "v1"}, "pinData": {}}
    out = f"n8n/workflows/{filename}"
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(wf, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("scritto", out, "nodi:", len(wf_nodes), "credenziale:", bool(CRED))


save("iusfulLeadIngest", "QUALIFIED_LEAD_INGEST", nodes, connections, "qualified_lead_ingest.json")


# --- GTM_RUN_SUMMARY -------------------------------------------------------------------------
S = "$json.body"
summary_nodes = [
    {
        "parameters": {"httpMethod": "POST", "path": "iusful/run-summary", "responseMode": "responseNode", "options": {}},
        "id": "b2f0c6d2-1b1e-4c55-9d0a-000000000001", "name": "Ricevi funnel", "type": "n8n-nodes-base.webhook",
        "typeVersion": 2, "position": [0, 0], "webhookId": "6c3a5b9f-8d2e-4f3b-a04c-2b3c4d5e6f70",
    },
    http("b2f0c6d2-1b1e-4c55-9d0a-000000000002", "Scrivi report su Notion", "POST", f"{NOTION}/pages",
         "{ parent: { database_id: '" + REPORT_DB + "' }, properties: {"
         " 'Esecuzione': { title: [{ text: { content: " + S + ".run_name } }] },"
         " 'Data': { date: { start: " + S + ".date } },"
         " 'Candidati valutati': { number: " + S + ".candidates },"
         " 'Qualificati': { number: " + S + ".qualified },"
         " 'Tier A': { number: " + S + ".tier_a },"
         " 'Tier B': { number: " + S + ".tier_b },"
         " 'Riserva (C)': { number: " + S + ".tier_c },"
         " 'Scartati': { number: " + S + ".rejected },"
         " 'Motivi di scarto': { rich_text: [{ text: { content: Object.entries(" + S + ".rejection_reasons || {}).map(([k, v]) => k + ': ' + v).join('; ') } }] },"
         " 'Buyer non trovato': { number: " + S + ".missing_buyer },"
         " 'Dipendenti non verificati': { number: " + S + ".unverified_employees },"
         " 'Con segnale recente': { number: " + S + ".with_recent_signal },"
         " 'Da rivedere': { number: " + S + ".to_review ?? 0 },"
         " 'Novità della settimana': { rich_text: [{ text: { content: String(" + S + ".weekly_notes || '').slice(0, 2000) } }] },"
         " 'Tasso di qualificazione %': { number: " + S + ".qualification_rate } } }",
         [260, 0]),
    respond("b2f0c6d2-1b1e-4c55-9d0a-000000000003", "Report salvato",
            "{ saved: true, report_url: $json.url }", 200, [520, 0]),
]
summary_connections = {
    "Ricevi funnel": {"main": link("Scrivi report su Notion")},
    "Scrivi report su Notion": {"main": link("Report salvato")},
}
save("iusfulRunSummary", "GTM_RUN_SUMMARY", summary_nodes, summary_connections, "gtm_run_summary.json")


# --- HANDOFF_SALES ---------------------------------------------------------------------------
# Si avvia a mano (Manual Trigger) o dopo ogni invio di lead: passano i Tier A con Verifica
# "Superata" o "Rivista a mano" (docs/decisions.md);
# oppure con una POST a /webhook/iusful/handoff. La risposta al webhook è immediata: l'esito
# si vede in Notion (Stato e Interazioni) e nelle esecuzioni di n8n.
handoff_nodes = [
    {
        "parameters": {}, "id": "c3f0c6d2-1b1e-4c55-9d0a-000000000001", "name": "Avvio manuale",
        "type": "n8n-nodes-base.manualTrigger", "typeVersion": 1, "position": [0, -100],
    },
    {
        "parameters": {"httpMethod": "POST", "path": "iusful/handoff", "responseMode": "onReceived", "options": {}},
        "id": "c3f0c6d2-1b1e-4c55-9d0a-000000000002", "name": "Avvio da webhook", "type": "n8n-nodes-base.webhook",
        "typeVersion": 2, "position": [0, 100], "webhookId": "7d4b6c0a-9e3f-4a4c-b15d-3c4d5e6f7081",
    },
    http("c3f0c6d2-1b1e-4c55-9d0a-000000000003", "Cerca Tier A verificati", "POST",
         f"{NOTION}/databases/{AZIENDE_DB}/query",
         "{ filter: { and: ["
         " { property: 'Tier', select: { equals: 'A' } },"
         " { or: [ { property: 'Verifica', select: { equals: 'Superata' } },"
         " { property: 'Verifica', select: { equals: 'Rivista a mano' } } ] },"
         " { property: 'Stato', select: { equals: 'Qualificato' } } ] } }",
         [260, 0]),
    {
        "parameters": {"fieldToSplitOut": "results", "options": {}},
        "id": "c3f0c6d2-1b1e-4c55-9d0a-000000000004", "name": "Una azienda alla volta",
        "type": "n8n-nodes-base.splitOut", "typeVersion": 1, "position": [520, 0],
    },
    http("c3f0c6d2-1b1e-4c55-9d0a-000000000005", "Passa a Pronto per sales", "PATCH",
         "={{ 'https://api.notion.com/v1/pages/' + $json.id }}",
         "{ properties: { 'Stato': { select: { name: 'Pronto per sales' } } } }", [780, 0]),
    http("c3f0c6d2-1b1e-4c55-9d0a-000000000006", "Registra passaggio al sales", "POST", f"{NOTION}/pages",
         "{ parent: { database_id: '" + INTERAZIONI_DB + "' }, properties: {"
         " 'Cosa': { title: [{ text: { content: 'Passato al sales (Tier A, verifica ' + (($json.properties['Verifica'] || {}).select || {}).name + ')' } }] },"
         " 'Azienda': { relation: [{ id: $json.id }] },"
         " 'Tipo': { select: { name: 'Passaggio al sales' } },"
         " 'Chi': { select: { name: 'n8n' } },"
         " 'Data': { date: { start: $now.toISODate() } } } }",
         [1040, 0]),
]
handoff_connections = {
    "Avvio manuale": {"main": link("Cerca Tier A verificati")},
    "Avvio da webhook": {"main": link("Cerca Tier A verificati")},
    "Cerca Tier A verificati": {"main": link("Una azienda alla volta")},
    "Una azienda alla volta": {"main": link("Passa a Pronto per sales")},
    "Passa a Pronto per sales": {"main": link("Registra passaggio al sales")},
}
save("iusfulHandoffSale", "HANDOFF_SALES", handoff_nodes, handoff_connections, "handoff_sales.json")
