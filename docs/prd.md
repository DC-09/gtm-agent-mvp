# PRD: Iusful GTM Agent

## Problema

Iusful vende a PMI il cui bisogno legale sta diventando ricorrente, ma che oggi lo gestiscono ancora con consulenze occasionali. Questo passaggio non è osservabile direttamente: va dedotto da segnali pubblici indiretti di crescita e complessità. Senza un metodo sistematico, la selezione dei prospect resta a intuito e il contatto arriva troppo presto (bisogno sporadico, il prezzo pesa) o troppo tardi, quando l'azienda ha già trovato un'altra soluzione.

## Utente

- **Primario: il founder di Iusful.** Riceve lead e report in modo asincrono, probabilmente con pochi minuti a disposizione e senza spiegazioni a voce. Deve capire subito perché ogni azienda è stata scelta e chi contattare.
- **Operativo: chi gestisce il sistema (GTM engineer).** Avvia l'agente in Claude Code in locale, controlla le evidenze e rivede a mano le bozze di outreach.

## Obiettivo misurabile

Consegnare 20–50 PMI italiane tra 1 e 50 dipendenti, non finanziate da fondi di venture capital, prevalentemente Tier A/B (score ≥ 65), ciascuna con almeno una fonte verificabile, un buyer plausibile e un angle di outreach, salvate nel CRM e accompagnate da un report di funnel che mostri anche gli scartati e il motivo.

## Requisiti funzionali

1. Ricevere un obiettivo commerciale e pianificare la ricerca, controllando i dati esistenti prima di chiedere nuovo enrichment.
2. Arricchire le aziende in Clay (dati firmographic e segnali), con AI usata solo per i campi che richiedono giudizio.
3. Collegare ogni segnale a un bisogno legale secondo la mappa segnali → bisogno.
4. Calcolare lo score con i cinque componenti a pesi fissi, ognuno con una `score_reason`, e assegnare il tier.
5. Scegliere un buyer primario in base al pain emerso, non alla seniority.
6. Validare ogni lead contro `schemas/lead.schema.json` ed esportare solo Tier A e B.
7. Inviare i lead a n8n in locale; n8n filtra (score sopra la soglia del Tier B definita in docs/scoring.md) e salva aziende e persone nel CRM senza duplicati. Il CRM è un workspace Notion strutturato come CRM (docs/crm.md).
8. Generare con il workflow `GTM_RUN_SUMMARY` il funnel: candidati, qualificati, Tier A, Tier B, scartati, buyer mancante, evidenza mancante.
9. Produrre bozze di sequenza outbound in italiano (2 email + apertura LinkedIn), senza invio.

## Metriche

| Metrica | Target |
| --- | --- |
| Lead con almeno 1 evidence URL | 100% |
| Lead Tier A/B con buyer identificato | ≥ 85% |
| Lead con trigger recente verificabile | ≥ 70% |
| Duplicati | 0 |
| Lead con fatto inventato rilevato nel QA | 0 |
| Sync n8n → CRM riuscita | 100% sui record validi |

## Vincoli

- Costo zero: Clay Free o trial, n8n in locale con Node.js, Notion gratuito come CRM.
- Esecuzione locale avviata a mano; n8n raggiunto su `localhost` tramite script.
- Nessun fatto inventato: ogni segnale ha una fonte e, quando possibile, una data; le informazioni su Iusful vengono solo dalle sue pagine pubbliche.
- Nessun segreto nel repository: token solo in `.env` o nelle credentials di n8n.
- Controllo manuale obbligatorio su tutte le bozze di outreach.
- Crescita per passi: 1 lead, poi 5, poi 20–50.

## Non-goals

- **Nessun invio reale di email o messaggi.** Il sistema produce solo bozze: l'invio spetta al team commerciale di Iusful, anche per consenso e deliverability.
- **Nessuna scala oltre 50 aziende.** L'obiettivo è dimostrare la qualità della selezione, non il volume.
- **Nessuna azienda sopra i 50 dipendenti o fuori dall'Italia.** I piani pubblici di Iusful coprono aziende fino a 50 dipendenti e il servizio è pensato per PMI italiane: oltre questo perimetro non esiste un'offerta da proporre.
- **Nessun acquisto di database o abbonamento.** Il progetto deve restare a costo zero.
- **Nessuna automazione schedulata o webhook pubblico.** Per la demo basta un'esecuzione locale avviata a mano; la schedulazione è un next step di produzione.
- **Nessuna dashboard o interfaccia custom.** Lo stato dei lead vive nel CRM.
