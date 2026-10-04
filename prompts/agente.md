# Prompt di avvio dell'agente

Da incollare in Claude Code per una nuova sessione di ricerca. Sostituire il numero e, se serve, il tipo di azienda.

```
Trova 10 nuovi prospect per Iusful: PMI italiane tra 1 e 50 dipendenti, sul modello di
Elodie Brides (e-commerce e aziende con un canale digitale), non finanziate da fondi VC.

Lavora così:
1. Leggi CLAUDE.md, docs/decisions.md, docs/icp.md e docs/scoring.md.
2. Leggi data/leads.json: non rivalutare aziende già presenti (stesso dominio).
3. Cerca i candidati con prompts/sourcing.md.
4. Per ogni candidato segui, in ordine, prompts/company_fit.md, prompts/trigger_research.md
   e prompts/buyer_selection.md. Fermati appena trovi un'esclusione verificata:
   registra il lead come REJECTED con exclusion_reason e passa al successivo.
5. Calcola lo score con docs/scoring.md e aggiungi il lead a data/leads.json.
6. Dopo ogni lead aggiunto esegui python scripts/validate_leads.py e correggi gli errori.
7. Esegui python scripts/verify_sources.py e mostrami i lead "da rivedere", se ci sono.
8. Esegui python scripts/export_payload.py e mostrami il funnel.

Non inviare niente a nessuno. Non inventare dati: un dato senza fonte resta vuoto.
```
