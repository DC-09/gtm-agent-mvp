# Company fit: perimetro e dati di base

Riempie `facts` del lead (`schemas/lead.schema.json`). Le regole sono in `docs/icp.md` §1–3 e §5 e `docs/scoring.md` §2.1; qui c'è l'ordine di lavoro.

## Ordine di ricerca

1. **Sito aziendale**: footer (ragione sociale, partita IVA, sede), "chi siamo", termini e condizioni. È la fonte primaria.
2. **LinkedIn aziendale** (`linkedin.com/company/...`): fascia di dipendenti. Una fascia tutta dentro 1–50 vale come verifica.
3. **Siti di dati aziendali** (Atoka, informazione-aziende, aziende.it): dipendenti e fatturato, spesso come fascia. Molti bloccano la lettura automatica: se una pagina non si apre, il dato non c'è.
4. **Articoli** con data: solo per fatti che il sito non dice.

## Cosa registrare

- Paese e città con URL.
- Dipendenti: numero esatto o fascia con URL. Mai stimati. Se due fonti non coincidono, non verificati e nota nel campo `note`.
- Fatturato: valore o fascia con anno e URL.
- Modello di business tra quelli di `docs/icp.md` §3, con URL della pagina che lo mostra.
- Iscrizione come PMI innovativa solo se verificata (l'iscrizione come startup innovativa non conta).

## Esclusioni da controllare subito

Fermati e registra `exclusion_reason` se una fonte verifica: più di 50 dipendenti, zero dipendenti, sede fuori Italia, studio legale, filiale di gruppo estero, **round da un fondo di venture capital** (cerca `"nome azienda" round` e `"nome azienda" investimento`).

## Dubbi da segnalare

Se trovi un **indizio concreto** di esclusione che non riesci né a confermare né a smentire (un articolo che parla di un fondo VC senza dire se ha investito, due fonti con 30 e 80 dipendenti), aggiungilo in `doubts` con tipo `possibile_esclusione`, il dettaglio e l'URL. Solo indizi concreti: un dato mancante non è un dubbio, e un'informazione vista solo in un'anteprima di ricerca non è un indizio.

## Errori già visti

- Un dato letto solo nell'anteprima di un motore di ricerca non è una fonte: la pagina va aperta.
- "Persone del team" su un articolo o sul sito possono includere collaboratori: scrivilo nella nota.
- Il marchio e la ragione sociale spesso non coincidono (Dmora → Crido Consulting): cerca i dati sulla ragione sociale.
