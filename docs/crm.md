# CRM: Notion

Nell'MVP il CRM è un workspace Notion privato, strutturato come un CRM (pagina **Iusful GTM – CRM**), scelto per praticità: si prepara in pochi minuti e si collega a n8n. L'idea è usare un CRM vero, per esempio HubSpot: per passarci cambia solo l'ultimo nodo dei flussi n8n; c'è anche un export CSV (`data/qualified_leads.csv`) importabile in qualsiasi CRM.

## Struttura

| Database | A cosa serve | Chiave | ID database | ID data source |
| --- | --- | --- | --- | --- |
| Aziende | Un record per azienda: stato del lead, tier, score, segnale principale con fonte, bisogni legali, angle | `Dominio` | `47bd791712bb4d30acce6f2af257a433` | `0e1f1ba4-a701-4af6-bd5e-58c9aa265a0b` |
| Persone | Il buyer scelto, collegato all'azienda | nome + azienda | `9ed966106914451594f22af8d009d1e3` | `e7b25378-0c3e-42eb-8b7f-86b9fb2a5a6f` |
| Interazioni | Cosa è successo a ogni lead: qualificazione, verifiche manuali, bozze, passaggio al sales. Il campo "Chi" vale Agente, n8n o Revisore | — | `f95fe1d7744640c3aadeabc8aca2ce45` | `0f25f1d1-52a1-4a86-81b8-fa5cb2739758` |
| Report funnel | Un report per ogni esecuzione: candidati, qualificati, scartati e motivi, novità della settimana | — | `c80f0cbb73a9400593fee933737cd5ca` | `c3a5ef2e-e706-498a-8f9f-7af1b390f871` |

Viste di Aziende: **Pipeline** (colonne per stato) e **Per score** (tabella ordinata per punteggio).

## Ciclo di vita del lead (campo `Stato`)

| Stato | Quando |
| --- | --- |
| Nuovo | Candidato registrato, non ancora valutato |
| Qualificato | Tier A o B secondo `docs/scoring.md`, arrivato da n8n |
| Pronto per sales | Tier A con Verifica "Superata" o "Rivista a mano"; lo imposta HANDOFF_SALES |
| Contattato | Il team commerciale ha scritto al lead (fuori dall'MVP: il sistema non invia nulla) |
| Scartato | Escluso dopo l'ingresso, con il motivo in Interazioni |

## Flussi n8n

| Flusso | Si avvia | Cosa fa |
| --- | --- | --- |
| QUALIFIED_LEAD_INGEST | `scripts/push_n8n.py`, un lead per richiesta | Scarta i lead non validi o sotto 65; cerca l'azienda per dominio, la aggiorna o la crea (con la persona), registra l'interazione |
| GTM_RUN_SUMMARY | `scripts/push_n8n.py`, alla fine dell'invio | Scrive in Report funnel i numeri di `data/run_summary.json` e la sintesi del controllo settimanale ("Novità della settimana") |
| HANDOFF_SALES | `scripts/push_n8n.py --handoff`, a mano in n8n o POST a `/webhook/iusful/handoff` | Porta in "Pronto per sales" i Tier A con Verifica "Superata" o "Rivista a mano" e registra l'interazione "Passaggio al sales" |

Campo **Verifica** delle Aziende: "Superata" o "Da rivedere" lo scrive n8n con l'esito di `scripts/verify_sources.py`; "Rivista a mano" lo sceglie chi ha risolto un dubbio (`docs/controllo_manuale.md`) e n8n non lo sovrascrive.

## Regola anti-doppioni

n8n cerca in Aziende una pagina con lo stesso `Dominio`: se c'è la aggiorna, se non c'è la crea. Un'azienda non deve mai comparire due volte.

## Prove

- **Aggiornamento senza doppioni.** I primi 5 lead, caricati a mano, sono stati reinviati da n8n: aggiornati, nessun record nuovo, stato invariato.
- **Creazione.** Invii successivi hanno creato le aziende nuove con la loro persona e aggiornato le esistenti; oggi Aziende ha un record per ognuno dei 25 lead qualificati, senza doppioni.
- **Passaggio al sales.** HANDOFF_SALES porta da solo in "Pronto per sales" i Tier A verificati: tutti e 7 sono pronti.
