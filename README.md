# Iusful GTM Agent

Un MVP di sistema go-to-market per [Iusful](https://iusful.it). Trova PMI italiane che con buona probabilità hanno bisogno di un partner legale continuativo, verifica ogni fatto sulla fonte, assegna un punteggio, sceglie la persona da contattare e sincronizza i lead migliori nel CRM, con un report di funnel a ogni esecuzione.

L'obiettivo è la qualità, non il volume: 20-50 aziende, ognuna con prove verificabili.

## Risultato (4 ottobre 2026)

| | |
| --- | --- |
| Aziende valutate | 40 |
| Qualificate | **25** (7 Tier A, 18 Tier B) |
| In riserva (Tier C) | 8 |
| Scartate, con il motivo | 7 (3 finanziate da fondi VC, 2 oltre 50 dipendenti, 1 filiale di gruppo estero, 1 sotto soglia) |
| Fonti verificate in automatico | 25, nessuna da rivedere |
| Doppioni nel CRM | 0 |

I 7 Tier A, già in "Pronto per sales": Esplodia, ProduceShop, You Medical, Emilia Food Love, Sciara, Dmora, SD Calabria. Le bozze di outreach, che il sistema non invia, sono in [`outreach/bozze_tier_a.md`](outreach/bozze_tier_a.md).

## Come funziona

```
 Clay (Find Companies, Find contacts)        articoli, siti, annunci di lavoro
                 │                                        │
                 ▼                                        ▼
        scripts/import_clay.py  ──►  Claude Code: segnali, buyer, punteggio  ──►  data/leads.json
                                                                                      │
                     scripts/validate_leads.py  ◄─────────────────────────────────────┘
                     (ricalcola punteggi e regole)
                                 │
                     scripts/verify_sources.py
                     (riapre le fonti, cerca le citazioni)
                                 │
                     scripts/export_payload.py  ──►  scripts/push_n8n.py
                                                            │
                         n8n: QUALIFIED_LEAD_INGEST ─► Notion CRM (Aziende, Persone, Interazioni)
                              GTM_RUN_SUMMARY ───────► Notion (Report funnel)
                              HANDOFF_SALES ─────────► Tier A verificati in "Pronto per sales"
```

- **Claude Code** è l'agente. Riceve l'obiettivo, decide cosa cercare, abbandona presto i lead deboli e separa i fatti osservati dai bisogni legali dedotti. Istruzioni in [`CLAUDE.md`](CLAUDE.md) e [`prompts/`](prompts/).
- **Clay** trova le aziende (filtri Italia, 2-50 dipendenti e settore: retail ed e-commerce, servizi, sanità e formazione) e le persone (fondatori, titolari, C-level). Guida in [`docs/clay.md`](docs/clay.md).
- **Gli script Python** non si fidano dell'agente: ricalcolano ogni punteggio con le regole di [`docs/scoring.md`](docs/scoring.md) e riaprono le pagine citate. Se una citazione non c'è e senza quel fatto il lead cambierebbe tier, il lead va in revisione.
- **n8n** sincronizza il CRM senza doppioni (chiave: il dominio) e scrive il report di funnel. I flussi funzionano allo stesso modo su n8n cloud o su un server aziendale: cambia solo l'indirizzo dei webhook.
- **Notion** fa da CRM nell'MVP per praticità: si prepara in pochi minuti e si collega a n8n. Il posto giusto per i lead è un CRM vero, per esempio HubSpot: per passarci cambia solo l'ultimo nodo di n8n, e c'è anche un export CSV ([`data/qualified_leads.csv`](data/qualified_leads.csv)).

## Le regole che contano

- **Nessun fatto inventato.** Ogni segnale ha un URL e, quando possibile, una data. Un'anteprima di un motore di ricerca non è una fonte.
- **Punteggio trasparente** su 100 punti: company fit 30, complessità legale 25, segnali di acquisto 25, buyer 10, qualità delle prove 10. Tier A da 80, B da 65, C da 50. Ogni punto ha una motivazione scritta.
- **Segnali recenti.** Punti pieni fino a 12 mesi, metà tra 12 e 18 mesi, zero oltre o senza data.
- **Tre segmenti.** E-commerce e retail, servizi B2B e B2C, sanità e formazione private, ognuno con le sue righe nella mappa dei segnali (rete di sedi, dati sanitari o di minori, gare e convenzioni, nuovi servizi).
- **Revisione umana solo dove serve.** Arriva in revisione solo un lead con un dubbio di esclusione o un tier che dipende da un fatto non confermato ([`docs/controllo_manuale.md`](docs/controllo_manuale.md)).
- **Contatti con fonte, fuori dal repository.** Telefono aziendale dal sito, email e cellulare del buyer da Clay: stanno in un file escluso da git e arrivano al CRM solo con l'invio a n8n ([`docs/decisions.md`](docs/decisions.md)).
- **Nessun invio automatico.** Il sistema produce bozze. I segnali servono a scegliere chi contattare e quando, non vengono citati nelle email ([`prompts/outreach.md`](prompts/outreach.md)).

Le regole sono fissate alla versione 5 (4 ottobre 2026): da qui i lead cambiano solo per fatti nuovi. Ogni scelta, con data e motivo, è in [`docs/decisions.md`](docs/decisions.md).

## Come si esegue

Requisiti: Python 3, un'istanza n8n con i tre flussi di [`n8n/workflows/`](n8n/workflows/) importati e attivi, una credenziale Notion in n8n e l'indirizzo dei webhook in `.env` (`N8N_WEBHOOK_URL`, modello in [`.env.example`](.env.example)).

```bash
python scripts/import_clay.py        # prende l'ultimo export Clay dalla cartella Download
python scripts/validate_leads.py     # ricalcola punteggi e regole, stampa il funnel
python scripts/verify_sources.py     # riapre le fonti dei lead qualificati
python scripts/export_payload.py     # rifiuta l'export se la verifica manca o è vecchia
python scripts/push_n8n.py --handoff # invia lead e report a n8n e passa i Tier A al sales (--dry-run per provare)
```

**Controllo settimanale.** È pensato per partire da solo ogni lunedì come attività pianificata dell'app Claude; nell'MVP si lancia a mano ([`prompts/settimanale.md`](prompts/settimanale.md)):
1. `scripts/watch_signals.py` riapre le pagine di annunci e comunicati ([`data/watch.json`](data/watch.json)) e segnala le frasi nuove e i lead che cambiano tier perché i segnali invecchiano;
2. Clay cerca annunci aperti e notizie dei lead qualificati e in riserva;
3. l'agente trasforma in segnali solo le novità verificate, ricalcola, invia al CRM con `push_n8n.py --handoff` e apre una pull request con la sintesi della settimana, che finisce anche nel report su Notion.

I flussi n8n si rigenerano con `python n8n/build_workflow.py '{"id": "<credenziale>", "name": "<nome>"}'`.

## Struttura

| Cartella | Contenuto |
| --- | --- |
| `docs/` | PRD, prodotto Iusful, ICP, scoring, decisioni, CRM, Clay |
| `prompts/` | Istruzioni dell'agente per sourcing, fit, segnali, buyer, outreach |
| `schemas/` | Contratto dati di un lead (`lead.schema.json`) |
| `scripts/` | Import da Clay, validazione, verifica fonti, export, invio a n8n |
| `n8n/` | Generatore e JSON dei tre flussi |
| `data/` | Lead valutati, verifiche, payload e report |
| `outreach/` | Bozze di sequenza per i Tier A |

Il CRM è in un workspace Notion privato. Nessuna chiave o token è nel repository (`.env` è escluso, il modello è in [`.env.example`](.env.example)).
