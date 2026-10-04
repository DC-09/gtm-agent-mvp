# Scoring: Iusful GTM Agent

Versione 5, 4 ottobre 2026, **regole fissate**: da qui in avanti punteggi e soglie non cambiano per questo MVP. Rispetto alla versione 4 (3 ottobre: aziende finanziate da VC escluse, annunci senza data datati alla consultazione, recenza a 12/18 mesi, fasce di dipendenti accettate come verifica, dipendenti mancanti penalizzati una volta sola) aggiunge le righe della mappa per rete di sedi, aperture e acquisizioni, servizi continuativi, dati particolari, gare e convenzioni, nuovi servizi. Il calcolo è implementato in `scripts/validate_leads.py`, che ricalcola ogni componente e segnala le differenze. Definisce come si calcola lo score di un'azienda, come si assegna il tier e come si scrive la `score_reason`. Usa solo criteri già presenti in `docs/icp.md` e `docs/decisions.md`; i pesi sono quelli di partenza [BASE]. Le sigle delle fonti sono le stesse di `docs/icp.md` ([DEC], [PROD §x], [LOOK], [PRD], [CLAUDE]).

La "Decisione aperta" di [BASE] (come trattare i segnali di "troppo tardi", cioè di un bisogno legale già coperto) è superata da [DEC]: la copertura legale strutturale non è un criterio, quindi non produce esclusioni, penalità o flag. Offerte per legal counsel, ingresso in un gruppo con ufficio legale e studi citati nei comunicati non cambiano lo score.

## 1. Come si calcola

1. **Perimetro (prima dello score).** Si applicano le esclusioni di [ICP §5]. Se una regola di esclusione è verificata da una fonte, il lead è `REJECT` con `exclusion_reason` e non riceve un tier, qualunque sia il punteggio.
2. **Score.** Si sommano i cinque componenti, ognuno con la sua `score_reason`.
3. **Tier.** Si assegna in base al totale (§3). Se i dipendenti non sono verificati il tier massimo è B [DEC].
4. **Flag.** Si aggiunge, se serve, il flag sul fatturato (§4). Il flag non cambia né lo score né il tier.

```
TOTAL = company_fit (0–30) + legal_complexity (0–25) + buying_signals (0–25)
      + buyer_availability (0–10) + evidence_quality (0–10)
```

Regole valide per tutti i componenti:
- Un fatto conta solo se ha un URL di fonte. Senza URL non entra nello score [CLAUDE].
- Un dato mancante non si stima: vale 0 nel componente che lo usa e riduce `evidence_quality` [CLAUDE], [ICP §2.2].
- Il segnale è un fatto osservato; il bisogno legale collegato è un'inferenza e nella `score_reason` va scritto come tale [CLAUDE].

## 2. I cinque componenti

### 2.1 Company fit (0–30)

[BASE] lo definisce come "dimensione, settore, modello di business, geografia". Per [ICP §1] e [ICP §2.2] geografia e dimensione sono criteri di perimetro, senza priorità interne: valgono punti solo in quanto **verificati**, e valgono gli stessi punti per ogni azienda dentro la fascia. Il settore non è un criterio separato (vedi Conflitto S1).

| Sotto-criterio | Punti | Regola | Fonte |
| --- | --- | --- | --- |
| Geografia | 5 | Sede in Italia, da fonte. Fuori Italia (San Marino incluso) è esclusione, non punteggio | [ICP §1], [DEC] |
| Dimensione | 10 | Dipendenti tra 1 e 50, verificati. Stessi punti per 1–5, 5–15 e 15–50. Dipendenti non verificati: 0 (e tier massimo B, §3); è l'unica penalità per questo dato. Fuori dalla fascia è esclusione | [ICP §2.2], [DEC] |
| Modello di business | 15 | Il modello rientra nell'elenco di [ICP §3] (B2B, SaaS e piattaforme digitali, e-commerce e marketplace, servizi digitali, tech, agenzie strutturate, aziende innovative). "Aziende innovative" vale solo con iscrizione verificata alla sezione speciale del Registro delle imprese come PMI innovativa (non come startup innovativa); senza verifica non si applica. Fuori elenco o non determinabile: 0. Fuori elenco non è un'esclusione | [ICP §3], [DEC] |

Dipendenti verificati: numero preso da una fonte con URL, non stimato e non segnalato come "da verificare" dalla fonte stessa; oppure una fascia da fonte (es. LinkedIn "11-50") che cade tutta dentro 1–50 [CLAUDE], [ICP §2.2], [DEC]. Una fascia che tocca lo 0 ("0-4") o supera 50 non verifica il perimetro. Una fascia tutta sopra 50 ("51-200") è esclusione.

Il fatturato fino a €50M non dà e non toglie punti [ICP §2.2].

| Fascia | Cosa la produce | Esempio |
| --- | --- | --- |
| 30 | Italia + dipendenti 1–50 verificati + modello in elenco | SaaS B2B con sede a Torino, 22 dipendenti indicati sul sito aziendale |
| 20 | Italia + modello in elenco, dipendenti non verificati | E-commerce milanese di cui nessuna fonte riporta i dipendenti |
| 15 | Italia + dipendenti 1–50 verificati, modello fuori elenco | Azienda manifatturiera di Bergamo con 30 dipendenti e clienti in tre paesi (il segnale internazionale si recupera in `legal_complexity` e, se datato entro 18 mesi, in `buying_signals`) |
| 5 | Solo la sede in Italia è verificata | Società di formazione a Bari, dipendenti non trovati, modello fuori elenco |
| 0 | Nessun sotto-criterio verificato | Solo il nome dell'azienda, senza fonti |

### 2.2 Legal complexity (0–25)

"Numero e intensità dei problemi legali plausibili" [BASE]. Il numero si misura con le aree Iusful (le sei di [PROD §4]) collegate ai segnali osservati tramite la mappa [ICP §4.1]; l'intensità con la forza del segnale indicata nella stessa mappa.

- Contano solo i segnali della tabella [ICP §4.1] con URL. I temi di [ICP §4.2], cause in corso, crediti insoluti, fiscale e sicurezza sul lavoro non contano [ICP §4.2], [DEC].
- Le aree si prendono dalla colonna "Area Iusful" della mappa, non si deducono caso per caso. Ogni area si conta una volta, anche se più segnali la toccano.
- Qui contano anche i segnali strutturali (SaaS o piattaforma digitale, marketplace o e-commerce, rete di sedi, servizi continuativi, dati particolari), che non entrano in `buying_signals` (§2.3).
- Qui contano anche i segnali senza data o più vecchi di 18 mesi: la regola di recenza riguarda solo i buying signals [DEC]. Un'espansione estera di due anni fa dice ancora che l'azienda ha contratti su più paesi.

| Aree Iusful toccate | Punti base |
| --- | --- |
| 0 | 0 |
| 1 | 5 |
| 2 | 9 |
| 3 | 13 |
| 4 | 17 |
| 5–6 | 20 |

**+5** se tra i segnali che toccano le aree ce n'è almeno uno di forza "Forte" (clienti, contratti o vendite su più paesi; espansione estera; rete di 3 o più punti vendita o sedi in Italia; trattamento di dati sanitari, biometrici o di minori). Massimo 25. La rete di sedi è forte dal 4 ottobre 2026 [DEC]: prima solo l'export dava il bonus, e un'azienda che vende solo in Italia partiva con circa 8 punti in meno a parità di complessità.

| Fascia | Esempio |
| --- | --- |
| 21–25 | SaaS (Contratti, Dati & privacy, Tech AI & cyber) che vende in Francia e Spagna (Societario, forte) e assume (Lavoro & persone): 5 aree = 20, +5 forte = 25 |
| 13–20 | E-commerce senza altri segnali: 3 aree = 13. Oppure SaaS che assume: 4 aree = 17 |
| 5–12 | Azienda con solo collaboratori a partita IVA documentati (Proprietà intellettuale, Contratti): 2 aree = 9 |
| 0 | Nessun segnale della mappa con fonte |

Ipotesi non applicata: "i segnali privacy pesano di più nel 15–50" [PROD §7], [ICP §2.2] non si usa nell'MVP (vedi Conflitto S4).

### 2.3 Buying signals (0–25)

"Segnali recenti e verificabili" [BASE]: misurano il momento, che per [DEC] si legge dai segnali di crescita.

- Un segnale conta solo se ha una data verificabile nella fonte. Fino a 12 mesi alla data della valutazione vale punti pieni; tra 12 e 18 mesi metà punti, arrotondati per difetto; oltre 18 mesi o senza data vale 0 qui (resta valido per `legal_complexity`, §2.2) [DEC].
- **Annunci di lavoro senza data.** Un annuncio ancora online vale come datato al giorno della consultazione (età 0, punti pieni) [DEC]. Vale solo per le righe che un annuncio può mostrare: assunzioni, offerte da remoto o ibride, freelance e agenzie, più paesi (ruolo dedicato a un mercato estero). Nel lead il segnale ha `date_basis = "consultazione"` e la data coincide con quella di consultazione della pagina in `sources`. Una stessa pagina di annunci conta come **un solo** segnale, quello che vale di più.
- Età in mesi interi compiuti tra la data del segnale e la data della valutazione. Se la fonte dà solo mese o anno, si parte dal primo giorno del mese o dell'anno [DEC].
- Contano le righe di [ICP §4.1] che descrivono un'attività o un evento: più paesi/espansione estera, fundraising e nuovi soci, piani per dipendenti, assunzioni, offerte da remoto o ibride, freelance e agenzie, nuovo prodotto AI, brevetto depositato, nuova apertura o acquisizione, gara o convenzione con un ente, nuovo servizio. Rete di sedi, servizi continuativi e dati particolari sono strutturali: contano in `legal_complexity`, non qui.
- Non contano qui SaaS/piattaforma e marketplace/e-commerce: sono il modello di business, già premiato in `company_fit` e `legal_complexity`, e da soli non dicono nulla sul momento.
- Ogni riga della mappa si conta una volta (cinque offerte di lavoro sono un solo segnale "assunzioni").
- Le partnership, citate in [BASE], non contano: non sono nella mappa (vedi Conflitto S2).

| Segnale con URL e data | Fino a 12 mesi | Tra 12 e 18 mesi | Oltre 18 mesi o senza data |
| --- | --- | --- | --- |
| Forte | 12 | 6 | 0 |
| Normale | 7 | 3 | 0 |

Si sommano, massimo 25. Se più segnali cadono sulla stessa riga della mappa, conta quello che vale di più. La data va scritta nella `score_reason` così come appare nella fonte, con l'età in mesi.

| Fascia | Esempio (valutazione il 3 ottobre 2026) |
| --- | --- |
| 17–25 | Contratti con clienti in Germania (comunicato del 2026-06-10, 12) + round seed (articolo del 2025-11-03, 7) + offerte di lavoro (pagina careers del 2026-09-15, 7) = 26 → 25 |
| 12–16 | Solo vendite su più paesi (2026-01-15, 12). Oppure assunzioni (2026-08-20, 7) + brevetto depositato (2025-12-10, 7) = 14 |
| 7–11 | Un solo segnale normale entro 12 mesi, ad esempio un round seed del 2026-02-15 (7) |
| 1–6 | Un solo segnale tra 12 e 18 mesi, ad esempio un'espansione in Spagna del 2025-06-01 (16 mesi, forte, 6) |
| 0 | Nessun segnale di attività con data entro 18 mesi. Ad esempio un'espansione estera del 2024, o freelance citati sul sito senza data |

### 2.4 Buyer availability (0–10)

"Esiste una persona identificabile con ownership plausibile?" [BASE]. Lo scenario e il ruolo atteso vengono dalla tabella [ICP §6]; lo scenario si sceglie in base al pain emerso, non alla seniority.

| Fascia | Regola | Esempio |
| --- | --- | --- |
| 10 | Nome e ruolo da fonte con URL; il ruolo è il buyer primario dello scenario | Azienda di 4 dipendenti (scenario 1–5), CEO e founder indicato per nome nella pagina "chi siamo" |
| 7 | Nome e ruolo da fonte con URL; il ruolo è tra le alternative dello scenario | Clienti su più paesi, Finance Manager indicato per nome su LinkedIn (primario: CEO) |
| 4 | Solo il ruolo è noto da fonte, senza nome; oppure il nome è noto ma il ruolo atteso non è confermato | Testimonianza firmata "CEO e co-founder" senza nome; oppure "fondata da X" senza dire che X è il CEO |
| 0 | Nessuna persona credibile: `buyer_fit = "unclear"` | Nessun nome né ruolo nelle fonti |

L'email o altri dati di contatto non danno punti e non si inventano [CLAUDE].

### 2.5 Evidence quality (0–10)

"Le informazioni sono supportate da fonti primarie/recenti?" [BASE]. Fonte primaria = pagine dell'azienda stessa (sito, pagina careers, comunicati propri), che [BASE] indica come prime fonti da consultare. Si parte da 10 e si sottrae; minimo 0.

| Mancanza | Punti | Fonte |
| --- | --- | --- |
| Fatturato non trovato da una fonte | −1 | [ICP §2.2], [CLAUDE] |
| Nessuna fonte primaria tra quelle usate | −2 | [BASE] |
| Dato usato nello score che la fonte stessa dichiara non verificato (es. identificazione dell'azienda incerta, buyer indicato da una fonte come "ex" o "da verificare") | −2 ciascuno, massimo −4 | [CLAUDE] |

I dipendenti mancanti non tolgono punti qui: sono già penalizzati in `company_fit` (0 nella dimensione) e con il tetto al Tier B, e lo stesso dato si penalizza una volta sola [DEC]. Per lo stesso motivo un numero di dipendenti "da verificare" non conta come dato non verificato in questa tabella: semplicemente non verifica la dimensione.

| Fascia | Esempio |
| --- | --- |
| 9–10 | Fatturato trovato, segnali dal sito aziendale: 10. Fatturato mancante: 9 |
| 6–8 | Fatturato mancante e nessuna fonte primaria: 10 − 1 − 2 = 7 |
| 3–5 | Come sopra, più identificazione dell'azienda incerta: 5. Con due dati non verificati: 3 (minimo possibile) |

## 3. Tier

| Totale | Tier | Uso | Fonte |
| --- | --- | --- | --- |
| 80–100 | A | Da mostrare al founder, pronto per la bozza di outreach | [BASE] |
| 65–79 | B | Valido, richiede verifica aggiuntiva | [BASE] |
| 50–64 | C | Riserva, non esportato | [BASE], [PRD] |
| < 50 | REJECT | Scartato, con motivo nel report di funnel | [BASE], [PRD] |
| ≥ 80 con dipendenti non verificati | B | Tetto: senza dipendenti verificati il lead non supera il Tier B. La `score_reason` di `company_fit` lo dice | [DEC] |
| qualsiasi | REJECT | Esclusione di perimetro verificata ([ICP §5]) | [ICP §5] |

Si esportano verso n8n (e da lì al CRM su Notion, che sostituisce Attio [DEC]) solo i Tier A e B: la soglia del filtro n8n è quindi `score.total >= 65` [PRD, req. 6–7].

## 4. Flag sul fatturato

| Fatturato (da fonte) | Effetto | Fonte |
| --- | --- | --- |
| Fino a €50M (incluso) | Nessuno. Indica solo il piano plausibile | [DEC], [ICP §2.2] |
| Oltre €50M e fino a X | Dentro, con flag `fuori_piani_pubblici_da_verificare` | [DEC] |
| Oltre X | Esclusione di perimetro: `REJECT` | [DEC] |
| Non trovato | Nessun flag, −1 in `evidence_quality` | [ICP §2.2] |

- Il flag non toglie punti e non cambia il tier: [DEC] non gli attribuisce altri effetti. Viene esportato con il lead e mostrato al founder.
- **X non è deciso** [DEC]. Finché non lo è, nessuna azienda viene esclusa per fatturato: ogni azienda tra 1 e 50 dipendenti con fatturato oltre €50M riceve il flag.

## 5. Regola della `score_reason`

Una `score_reason` per componente, una riga, al massimo 40 parole. Riporta i punti di ogni sotto-criterio, l'URL della fonte di ogni fatto e il dato mancante con il suo effetto. Le inferenze sono marcate "(inferenza)", i collegamenti che vengono solo da [PROD §7] "(ipotesi)". Non contiene fatti che non stanno nelle fonti.

| Componente | Deve dire | Esempio |
| --- | --- | --- |
| `company_fit` | I tre sotto-criteri con punti e URL; "non verificato" per il dato mancante, con il tetto al Tier B | "Sede Milano (URL) +5; dipendenti non verificati 0, tier massimo B; e-commerce (URL) +15. Totale 20." |
| `legal_complexity` | Le aree contate, il segnale che porta ciascuna, il bonus forte | "E-commerce (URL) → Contratti, Dati & privacy, Tech AI & cyber (inferenza): 3 aree 13; nessun segnale forte. Totale 13." |
| `buying_signals` | Ogni segnale: riga della mappa, fatto osservato, URL, data ed età in mesi, punti; i segnali esclusi con il motivo | "Vendite in Francia e Spagna (URL, 2026-05-12, 4 mesi), forte 12; offerte di lavoro (URL, data non trovata), non conta. Totale 12." |
| `buyer_availability` | Nome e ruolo con URL, scenario di [ICP §6], primario o alternativa; oppure `unclear` | "Mario Rossi, CEO (URL); scenario 5–15 caso generale, primario. 10." |
| `evidence_quality` | Ogni sottrazione con il motivo | "Fatturato non trovato −1; fonte primaria presente. 9." |

Per un lead `REJECT` per perimetro serve anche `exclusion_reason`: la regola di [ICP §5] e l'URL che la verifica.

Queste regole sono riportate in `schemas/lead.schema.json` (`score.<componente>`, `score_reason.<componente>`, `flags`, `exclusion_reason`) e verificate da `scripts/validate_leads.py`.

## 6. Conflitti

| # | Tema | Cosa dicono i file | Cosa segue questo documento |
| --- | --- | --- | --- |
| S1 | Contenuto del company fit | [BASE] mette dimensione, settore e geografia nel punteggio, e [BASE] fissa il perimetro a 5–50 con priorità al 5–15. [DEC] fissa dimensione (1–50) e geografia come perimetro, senza priorità; [ICP §3] e [DEC] non hanno un criterio di settore (la dimensione internazionale conta più del settore) | Dimensione e geografia danno punti solo se verificate, uguali per tutta la fascia 1–50; il settore non è un sotto-criterio, conta solo il modello di business di [ICP §3] |
| S2 | Partnership | [BASE] cita le partnership tra i buying signals; non sono nella mappa [ICP §4.1] | Non contano finché non entrano nella mappa con una decisione |
| S3 | Colonne Clay | [BASE] prevede tre punteggi (`fit_score`, `trigger_score`, `evidence_score`). [BASE] e [PRD] prevedono cinque componenti | Cinque componenti; le colonne Clay vanno allineate |
| S4 | Segnali privacy nel 15–50 | [PROD §7] (ipotesi, ripresa in [ICP §2.2]) li farebbe pesare di più nel 15–50. [DEC] esclude priorità tra 1–5, 5–15 e 15–50 | Non applicata: darebbe di fatto un vantaggio al 15–50 |
| S5 | "Bisogno già coperto" | [BASE] lo mette tra le esclusioni e [BASE] tra le metriche del funnel. [DEC] lo toglie come criterio; [PRD] non lo elenca nel funnel | [DEC]: nessun effetto sullo score. Fuori da questo documento, ma la metrica in [BASE] va tolta |

## 7. Da decidere

- **X**: soglia di fatturato oltre la quale un'azienda è fuori perimetro [DEC].

## 8. Applicazione ai clienti attuali

Dati usati: solo quelli di `docs/clienti_lookalike.md`, esclusi Pattern e Implicazioni (interpretazioni). Nessuna ricerca aggiuntiva. Data di valutazione: 3 ottobre 2026, quindi un buying signal vale punti pieni se datato dal 3 ottobre 2025 in poi e metà punti se datato tra il 3 aprile 2025 e il 2 ottobre 2025. Per i clienti fuori perimetro il punteggio è **indicativo**: mostra cosa direbbe il modello, ma il tier è comunque `REJECT`.

| Cliente | Fit | Complessità | Segnali | Buyer | Evidenze | Totale | Tier | Perimetro |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Elodie Brides | 20 | 13 | 0 | 10 | 9 | **52** | C | Dentro; dipendenti non verificati (tier massimo B) |
| Eccentrica | 0 | 14 | 0 | 4 | 5 | **23** (indicativo) | REJECT | **Fuori**: sede a San Marino |
| Healthcademia | 5 | 0 | 0 | 4 | 9 | **18** (indicativo) | REJECT | **Fuori**: filiale italiana di un gruppo estero |
| Trademybusiness.com | 20 | 9 | 0 | 4 | 9 | **42** | REJECT (< 50) | Dentro; dipendenti non verificati (tier massimo B) |

Cosa cambia rispetto alla versione 2: i dipendenti mancanti non tolgono più 3 punti in `evidence_quality`, e il dato di enrichment "da verificare" di Trademybusiness.com non toglie più 2 punti (non verifica la dimensione, che resta a 0). Elodie Brides passa da REJECT a Tier C. La recenza a 12/18 mesi non cambia nulla qui: nessuno dei quattro ha un segnale della mappa datato dopo l'aprile 2025.

### Elodie Brides: 52, Tier C

- **Perimetro.** Sede a Milano. Il file stima i dipendenti "probabilmente sotto i 5 (non verificato)": l'azienda è dentro il perimetro 1–50, ma i dipendenti non sono verificati e il tier massimo è B.
- `company_fit` 20: Milano (cbinsights, T&C) +5; dipendenti non verificati 0; e-commerce (https://elodiebrides.com/pages/termini-e-condizioni) +15.
- `legal_complexity` 13: e-commerce → Contratti, Dati & privacy, Tech AI & cyber (inferenza): 3 aree. Nessun segnale forte: l'ambizione di diventare un marketplace europeo è dichiarata, non sono vendite su più paesi osservate.
- `buying_signals` 0: l'e-commerce è strutturale; fondazione 2022 e premio StartupHer 2022 non sono segnali della mappa e sono comunque più vecchi di 18 mesi.
- `buyer_availability` 10: Francesca Mantovani e Giulia Lodia, co-founder (https://www.cbinsights.com/company/elodie-brides/people); Founder/CEO è il primario negli scenari fino a 15 dipendenti, 1–5 compreso.
- `evidence_quality` 9: fatturato non trovato −1; fonte primaria presente (sito aziendale).

### Eccentrica: fuori perimetro (indicativo 23)

- **Perché è fuori.** Sede nella Repubblica di San Marino, esclusa da [ICP §1] e [ICP §5]. In più l'identificazione con Eccentrica Cars non è confermata.
- `company_fit` 0: sede fuori Italia; dipendenti non trovati; restomod di supercar non rientra in un modello dell'elenco. Il file la chiama "startup", ma non c'è (né potrebbe esserci, con sede a San Marino) un'iscrizione verificata alla sezione delle PMI innovative.
- `legal_complexity` 14: clienti e collezionisti internazionali → Contratti, Societario (inferenza): 2 aree 9, +5 forte.
- `buying_signals` 0: il segnale sui clienti internazionali è datato 2024-08-15 (data letta dall'URL https://www.businesswire.com/news/home/20240815233230/en), 25 mesi, oltre 18.
- `buyer_availability` 4: il fondatore Emanuel Colombini è noto per nome, ma il file non dice che è il CEO (primario per lo scenario "clienti su più paesi"); il Finance Manager che firma la testimonianza è noto solo per ruolo.
- `evidence_quality` 5: fatturato −1; nessuna fonte primaria (Wikipedia, BusinessWire, HDmotori) −2; identificazione non confermata −2.

### Healthcademia: fuori perimetro (indicativo 18)

- **Perché è fuori.** L'entità italiana, Healthcademia Education Italy Srl, è una filiale di un gruppo estero: segmento escluso dall'MVP [DEC], [ICP §5]. Misurato sul gruppo (circa 1.500 dipendenti) sarebbe fuori anche per dimensione; i dipendenti dell'entità italiana non sono noti.
- `company_fit` 5: sede a Bari (https://www.altaformazioneaims.it/) +5; dipendenti dell'entità italiana non trovati 0; formazione sanitaria fuori elenco 0.
- `legal_complexity` 0 e `buying_signals` 0: la rete in 11 paesi e il private equity riguardano il gruppo; nessuna fonte li collega a contratti o soci dell'entità italiana, e nessuno dei due ha una data nel file.
- `buyer_availability` 4: Country Manager Italia, noto solo per ruolo; in [ICP §6] è il buyer solo per lo scenario filiale, fuori MVP.
- `evidence_quality` 9: fatturato −1; fonte primaria presente (sito dell'accademia).

### Trademybusiness.com: 42, REJECT

- **Perimetro.** Sede a Milano. L'unico dato sui dipendenti (una fonte di enrichment: 3, "da verificare") sta dentro il perimetro 1–50, ma non è verificato: il tier massimo è B. Non è una società di consulenza legale: fa advisory per la vendita di aziende.
- `company_fit` 20: Milano (https://www.trademybusiness.com/chi-siamo-2/) +5; dipendenti non verificati 0; servizi a imprenditori che vendono l'azienda, B2B +15.
- `legal_complexity` 9: rete di professionisti esterni → Proprietà intellettuale, Contratti (inferenza): 2 aree.
- `buying_signals` 0: l'uso di professionisti esterni (stessa URL) non ha una data nel file, quindi non conta come recente.
- `buyer_availability` 4: "CEO e co-founder" che firma la testimonianza, noto solo per ruolo; Founder/CEO è il primario nello scenario 1–5.
- `evidence_quality` 9: fatturato −1; fonte primaria presente.

### Aggiornamento del 4 ottobre 2026

Con le fasce LinkedIn trovate da Clay (Elodie Brides e Trademybusiness, entrambe 2-10) i dipendenti risultano verificati. Elodie Brides passa a **C 62**, Trademybusiness a **C 52**. Clay (Open Jobs, Recent News) non trova annunci né notizie recenti per nessuno dei due. Lettura: il modello mette i clienti nel perimetro in riserva perché non hanno un segnale di crescita osservabile, coerente con clienti arrivati dalla rete dei founder e non da outbound. I file di prova in `data/samples/` restano quelli del 3 ottobre.

### Cosa dicono questi risultati

- Nessuno dei quattro clienti sarebbe esportato come lead (A o B): coerente con il Pattern di [LOOK] ("nessuno dei quattro corrisponde all'ICP") e con [DEC], per cui i clienti correggono l'ICP senza ridisegnarlo.
- I due clienti piccoli restano bassi soprattutto perché il file non ha segnali datati (0 su 25) e non ha dipendenti verificati. Sono lacune della ricerca sui lookalike, non giudizi sulle aziende: una ricerca mirata su segnali datati e dipendenti potrebbe cambiare il risultato.
- L'unico segnale forte (Eccentrica) cade su un'azienda fuori perimetro ed è del 2024: anche con la regola dei 18 mesi conta per la complessità, non per il momento.
