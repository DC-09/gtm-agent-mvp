# Trigger research: segnali e bisogni legali

Riempie `signals` e `legal_pains`. Le righe valide sono solo quelle della mappa di `docs/icp.md` §4.1; i punti sono in `docs/scoring.md` §2.2–2.3.

## Cosa cercare

1. **Vendite su più paesi** (segnale forte): spedizioni internazionali, versioni del sito in altre lingue, articoli che citano paesi esteri. Per i punti serve una data: di solito viene da un articolo.
2. **Annunci di lavoro** sulla pagina "lavora con noi" o sulla pagina careers: assunzioni, lavoro ibrido o da remoto, freelance, ruoli per mercati esteri. Se l'annuncio non ha data vale come datato al giorno della consultazione (`date_basis = "consultazione"`), ma una stessa pagina conta una sola volta.
3. **Nuovi soci o aumenti di capitale non da VC**, piani per dipendenti, brevetti, nuovi prodotti con AI.
4. **Il modello stesso**: e-commerce, marketplace, SaaS o piattaforma. Conta per la complessità, non per il momento.

## Come registrare un segnale

- `observed_fact`: cosa dice la fonte, senza interpretazioni.
- `evidence_quote`: una frase breve **copiata testualmente** dalla pagina che prova il fatto (es. "presenza in 12 mercati europei"). Obbligatoria per i segnali con data che danno punti: `scripts/verify_sources.py` la cerca nella pagina. Mai riformulare.
- `url` della pagina che lo dice e `date` come risulta dalla fonte (`date_basis = "fonte"`), oppure nessuna data.
- Un segnale non nella mappa (premi, nuove sedi, partnership) va nelle note, non in `signals`.

## Bisogni legali

Al massimo 3, ognuno con l'area Iusful e `basis = "inferenza"` (o `"ipotesi"` se viene solo da `docs/iusful_product.md` §7). Formulali come conseguenza tipica del segnale, mai come problema che l'azienda ha.
