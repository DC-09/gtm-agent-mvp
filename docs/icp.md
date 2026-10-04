# ICP: Iusful GTM Agent

Versione 5, 4 ottobre 2026, **regole fissate** per questo MVP. Rispetto alla versione 4 (aziende finanziate da VC escluse, annunci di lavoro senza data accettati, recenza a 12/18 mesi, fasce di dipendenti accettate come verifica) aggiunge i segmenti servizi B2B e B2C e sanità e formazione private, con le loro righe nella mappa (§3, §4.1). Definisce quali aziende cercare, quali segnali collegano un'azienda a un bisogno legale coperto da Iusful, chi escludere e chi contattare. Lo scoring è in `docs/scoring.md`.

## Come leggere questo documento

Accanto a ogni criterio è indicato il file da cui viene:

| Sigla | File |
| --- | --- |
| [DEC] | `docs/decisions.md` |
| [BASE] | Impostazione di partenza del progetto, prima delle decisioni |
| [PROD §x] | `docs/iusful_product.md`, sezione indicata (§7 = interpretazioni, da trattare come ipotesi) |
| [LOOK] | `docs/clienti_lookalike.md` (le righe "Pattern" e "Implicazioni" sono interpretazioni) |
| [PRD] | `docs/prd.md` |
| [CLAUDE] | `CLAUDE.md` |

- **Ipotesi**: criterio che viene da una sezione di interpretazione ([PROD §7], Pattern o Implicazioni di [LOOK]). Si usa, ma non vale come un fatto.
- **Conflitto**: due file dicono cose diverse. Si segue [DEC] e il conflitto è riassunto in fondo.
- **Da decidere**: questione aperta in [DEC]. Qui non viene risolta.

## 1. Perimetro

| Criterio | Regola | Fonte |
| --- | --- | --- |
| Geografia | Solo aziende italiane. San Marino è fuori perimetro (vedi Eccentrica in [LOOK]) | [DEC], [PRD], [BASE] |
| Dimensione | Tra 1 e 50 dipendenti: è l'intervallo dei piani pubblici, Essential compreso; oltre non c'è un'offerta da proporre | [DEC], [PRD] |
| Priorità tra 1–5, 5–15 e 15–50 | Nessuna priorità nell'MVP: i clienti attuali non la sostengono; la decideranno i dati (vedi Conflitto C1) | [DEC] |
| Tipo di azienda | PMI del tessuto produttivo italiano con un minimo di spinta d'innovazione, sul modello di Elodie Brides: e-commerce, brand che vendono online, servizi digitali. Le aziende finanziate da fondi di venture capital sono escluse (§5) | [DEC] |
| Spinta d'innovazione | Almeno un canale o prodotto digitale verificabile: e-commerce o vendita online propria, servizio o prodotto digitale, iscrizione alla sezione delle PMI innovative (l'iscrizione come startup innovativa non basta). Coincide con l'elenco dei modelli di §3 | [DEC] |
| Momento | Quando la complessità legale sta crescendo, non durante un problema puntuale: si legge dai segnali di crescita, non dalla presenza di un legale. Il concorrente reale è lo status quo (avvocato chiamato al bisogno) | [DEC], [PRD] |
| Maturità | In crescita o con processi già sufficientemente complessi | [BASE] |
| Prodotto target | Abbonamento (Essential, Professional, Enterprise). On demand è solo un punto d'ingresso per chi ha un bisogno ancora sporadico (ipotesi) | [PROD §7] |
| Uso dei clienti attuali | I quattro clienti citati sul sito correggono l'ICP, non lo ridisegnano: sono pochi e almeno due vengono dalla stessa rete personale | [DEC], [LOOK] |
| Volume | 20–50 aziende, qualità prima del volume | [PRD], [CLAUDE] |

## 2. Criteri dimensionali

### 2.1 Fasce dei piani Iusful

| Piano | Dipendenti | Fatturato | Prezzo | Dentro il perimetro MVP? | Fonte |
| --- | --- | --- | --- | --- | --- |
| Essential | 1–5 | €0–1M | da €250/mese | Sì | [PROD §3], [DEC] |
| Professional | 5–15 | €1–10M | da €500/mese | Sì | [PROD §3] |
| Enterprise | 15–50 | €10–50M | su richiesta | Sì | [PROD §3] |
| On demand | qualsiasi | qualsiasi | preventivo entro 48 ore | Solo come ingresso, non come obiettivo (ipotesi) | [PROD §3], [PROD §7] |
| Nessun piano pubblico | 1–50 | oltre €50M | — | Sì fino a X, con flag "fuori dai piani pubblici, da verificare"; oltre X no | [DEC] |

### 2.2 Come usare dipendenti e fatturato

| Criterio | Regola | Fonte |
| --- | --- | --- |
| Dipendenti | Criterio di perimetro: fuori dalla fascia 1–50 l'azienda è esclusa | [DEC], [PRD] |
| Fatturato fino a €50M | Normale: il fatturato indica solo il piano plausibile e non esclude né penalizza nessuno | [DEC], [PROD §3] |
| Fatturato da €50M a X | Dentro, con flag "fuori dai piani pubblici, da verificare" | [DEC] |
| Fatturato oltre X | Fuori. Il valore di X è **Da decidere** | [DEC] |
| Confini | Le fasce dei piani si toccano a 5 e a 15 dipendenti (1–5 / 5–15 / 15–50). Tutte e tre le fasce sono dentro il perimetro [DEC] | [PROD §3] |
| Segnale privacy nel 15–50 | Enterprise include il DPO, quindi i segnali privacy potrebbero pesare di più nel 15–50 (ipotesi) | [PROD §7] |
| Dato mancante | Dipendenti e fatturato vanno presi da una fonte; se mancano non si stimano. Il dato mancante riduce la confidenza | [CLAUDE] |
| Dipendenti verificati | Numero da una fonte con URL, oppure fascia da una fonte (es. LinkedIn "11-50") che cade tutta dentro 1–50. Una fascia che tocca lo 0 ("0-4") non basta | [DEC] |
| Dipendenti non verificati | Il lead non può superare il Tier B. Il dato mancante si penalizza una volta sola (vedi `docs/scoring.md` §2.1) | [DEC] |

## 3. Modelli di business

| Modello | Fonte |
| --- | --- |
| B2B | [BASE] |
| SaaS e piattaforme digitali | [BASE] |
| E-commerce e marketplace (un cliente attuale, Elodie Brides, vende online) | [BASE], [LOOK] |
| Servizi digitali | [BASE] |
| Tech | [BASE] |
| Agenzie strutturate | [BASE] |
| Servizi B2C con un canale digitale verificabile: prenotazione, acquisto o abbonamento online, app (es. centri benessere, scuole di lingue, servizi a domicilio) | [DEC] (4 ottobre 2026) |
| Sanità e formazione private con un canale digitale verificabile: prenotazione online, telemedicina, corsi online (es. poliambulatori, centri diagnostici e dentistici, enti di formazione e academy) | [DEC] (4 ottobre 2026), [LOOK] (Healthcademia) |
| Aziende innovative: solo se iscritte alla sezione speciale del Registro delle imprese come PMI innovativa (non basta l'iscrizione come startup innovativa). Senza questa verifica il criterio non si applica | [BASE], [DEC] |

Dove cercare: si parte da aziende con un canale digitale verificabile (e-commerce, servizi B2B e B2C, sanità e formazione private), non dalle notizie di round, che portano quasi solo aziende finanziate da VC, escluse [DEC] e le prime prove. Per agenzie e servizi le pagine "lavora con noi" danno più segnali di LinkedIn (`docs/clay.md`).

Correzione dai clienti attuali: nessuno dei quattro clienti è un'azienda SaaS o tech italiana, e tre su quattro hanno una dimensione internazionale [LOOK, Pattern]. Per questo la dimensione internazionale (clienti o contratti su più paesi) entra come **segnale forte**, in qualunque settore. L'elenco dei modelli resta invariato: i clienti attuali correggono l'ICP, non lo ridisegnano [DEC]. Vedi Conflitto C3.

## 4. Mappa segnali → bisogno legale

Costruita sulle sei aree e sui temi elencati in [PROD §4]. Ogni segnale va registrato con URL della fonte e, quando possibile, data [CLAUDE]. Come buying signal vale punti pieni fino a 12 mesi, metà punti tra 12 e 18 mesi, zero oltre o senza data verificabile [DEC]. Un annuncio di lavoro ancora online senza data vale come datato al giorno della consultazione; una stessa pagina di annunci conta come un solo segnale [DEC]. Il segnale è un fatto osservato; il bisogno legale è un'inferenza e va tenuto separato [CLAUDE].

### 4.1 Segnali collegati ai temi Iusful

| Segnale osservabile | Area Iusful | Temi di [PROD §4] collegati | Forza | Fonte |
| --- | --- | --- | --- | --- |
| Clienti, contratti o vendite su più paesi; espansione estera (`piu_paesi`) | Contratti, Societario | Condizioni generali; garanzie e manleve; penali e limiti di responsabilità; controllate e joint venture | **Forte** | [BASE], [DEC], [LOOK], [PROD §6] |
| Fundraising, ingresso di nuovi soci (`fundraising_soci`) | Societario | Statuti e patti parasociali; verbali e delibere; ESOP e work-for-equity | Normale | [BASE], [PROD §4] (esempio in homepage: nuovo socio senza patti parasociali) |
| Piani per dipendenti, work-for-equity (`piani_dipendenti`) | Societario | ESOP e work-for-equity | Normale | [PROD §7] (ipotesi) |
| Molte assunzioni, nuove posizioni aperte (`assunzioni`) | Lavoro & persone | Contratti di lavoro; patti di non concorrenza; riservatezza e invenzioni; bonus e piani di incentivo; procedure disciplinari | Normale | [BASE] |
| Offerte di lavoro da remoto o ibride (`remoto_ibrido`) | Lavoro & persone | Smart working policy | Normale | [PROD §7] (ipotesi), [BASE] |
| Uso di freelance, agenzie o collaboratori a partita IVA (`freelance_agenzie`) | Proprietà intellettuale, Contratti | Contratti con freelance e agenzie; cessione dei diritti; titolarità delle opere; NDA, MoU e LOI | Normale | [BASE], [PROD §4] (esempi in homepage: software sviluppato da freelance, collaboratori a partita IVA) |
| Nuovo prodotto o funzione AI (`prodotto_ai`) | Tech, AI & cyber, Dati & privacy | Classificazione del rischio AI; gap analysis AI Act; contratti con provider GPAI | Normale | [BASE], [PROD §7] (ipotesi) |
| SaaS o piattaforma digitale (`saas_piattaforma`) | Contratti, Dati & privacy, Tech, AI & cyber | Condizioni generali; nomine a responsabile (DPA); SaaS, cloud e outsourcing; licenze software e open source | Normale | [BASE] |
| Marketplace o e-commerce (`marketplace_ecommerce`) | Contratti, Dati & privacy, Tech, AI & cyber | Condizioni generali; informative e consensi; T&C di piattaforma e DSA | Normale | [BASE], [PROD §7] (ipotesi) |
| Brevetto depositato (`brevetto`) | Proprietà intellettuale, Contratti | Licenze di marchio e brevetto; know-how e segreti; NDA, MoU e LOI | Normale | [DEC] |
| Rete di 3 o più punti vendita o sedi in Italia (`rete_sedi`) | Contratti, Lavoro & persone | Condizioni generali; franchising e licenze; appalto e subfornitura; contratti di lavoro su più sedi | **Forte** | [DEC] (4 ottobre 2026) |
| Nuova apertura di un punto vendita o sede, o acquisizione di un'azienda, con data (`apertura_acquisizione`) | Contratti, Lavoro & persone | Contratti di locazione e fornitura; passaggio dei dipendenti; garanzie e manleve | Normale | [DEC] (4 ottobre 2026) |
| Servizi continuativi a clienti, business o privati: abbonamenti, contratti di assistenza, retainer, SLA (`servizio_continuativo`) | Contratti, Dati & privacy | Condizioni generali; penali e limiti di responsabilità; nomine a responsabile (DPA) | Normale | [DEC] (4 ottobre 2026) |
| Trattamento di dati sanitari, biometrici o di minori come parte del servizio (`dati_particolari`) | Dati & privacy, Tech, AI & cyber | Registro dei trattamenti; DPIA; data breach; informative e consensi; sicurezza dei sistemi | **Forte** | [DEC] (4 ottobre 2026), [PROD §4] |
| Gara pubblica vinta, convenzione o accreditamento con un ente (SSN, Regione, fondi interprofessionali), con data (`appalti_convenzioni`) | Contratti, Dati & privacy | Appalto e subfornitura; penali e limiti di responsabilità; nomine a responsabile | Normale | [DEC] (4 ottobre 2026) |
| Lancio di un nuovo servizio o di una nuova linea (telemedicina, corso online, nuova specialità), con data (`nuovo_servizio`) | Contratti, Dati & privacy | Condizioni generali; informative e consensi | Normale | [DEC] (4 ottobre 2026) |

### 4.2 Temi senza segnale osservabile nelle fonti

Per questi temi di [PROD §4] le fonti non indicano un segnale pubblico che li renda visibili dall'esterno. Non si usano come segnali finché una fonte o una decisione non li definisce: un segnale senza fonte riduce la confidenza, non si inventa [CLAUDE].

| Area | Temi |
| --- | --- |
| Dati & privacy | Trasferimenti extra UE; richieste degli interessati. Registro dei trattamenti, DPIA e data breach sono diventati osservabili dal 4 ottobre 2026 per chi tratta dati particolari (`dati_particolari`) |
| Societario | Costituzione di NewCo; deleghe e organi di controllo |
| Lavoro & persone | Licenziamenti e conciliazioni |
| Contratti | Appalto e subfornitura, osservabili solo con una gara o convenzione pubblica (`appalti_convenzioni`); franchising e licenze, solo con una rete di sedi (`rete_sedi`) |
| Proprietà intellettuale | Licenze software (coperta solo tramite il segnale SaaS) |
| Tech, AI & cyber | Conformità NIS2 (citata come esempio in homepage [PROD §4], ma le fonti non dicono come riconoscerla dall'esterno) |

Fuori mappa: cause in corso e crediti insoluti sono neutri. Sono bisogni reali ma raramente osservabili dall'esterno per una PMI, quindi non entrano nella mappa segnali [DEC].

Fuori mappa anche fiscale e sicurezza sul lavoro: compaiono tra i casi gestiti ma non tra le sei aree del sito [PROD §5], [PROD §7]. Non generano segnali in questa versione.

## 5. Esclusioni

| Esclusione | Motivo | Fonte |
| --- | --- | --- |
| Più di 50 dipendenti | Fuori dai piani pubblici Iusful | [DEC], [PRD], [BASE] |
| Fatturato oltre X (X da decidere) | Oltre la fascia per cui è previsto il flag "fuori dai piani pubblici, da verificare" | [DEC] |
| Nessun dipendente | Fuori dal perimetro 1–50 | [DEC] |
| Aziende fuori dall'Italia, San Marino incluso | Il servizio è pensato per PMI italiane | [DEC], [PRD], [BASE] |
| Studi legali e società di consulenza legale | Concorrenti o fornitori, non clienti | [BASE] |
| Attività locali micro senza segnali di complessità | Nessun bisogno legale ricorrente osservabile | [BASE] |
| **Aziende finanziate da fondi di venture capital** | Almeno un round da un fondo VC (anche corporate VC o CDP Venture Capital), da fonte. Premi, bandi, crowdfunding, business angel e aumenti di capitale tra soci non escludono | [DEC] |
| **Filiali italiane di gruppi esteri** | Escluse dall'MVP per semplicità: dimensione, buyer e struttura legale sono più difficili da leggere. Non è un giudizio sul segmento (Healthcademia, cliente attuale, è una filiale); da riconsiderare dopo l'MVP | [DEC]; Conflitto C2 con [LOOK] |

## 6. Buyer per scenario

Regole generali:
- Il buyer si sceglie in base al pain emerso, non alla seniority [BASE], [PRD].
- Un buyer primario; un backup solo se utile; se non c'è un buyer credibile, `buyer_fit = "unclear"` [BASE].
- Il buyer non è sempre il founder: tra i clienti attuali firmano un Finance Manager e un Country Manager [DEC], [LOOK].
- Nessun dato di contatto inventato [CLAUDE].

| Scenario | Buyer primario | Alternative | Fonte |
| --- | --- | --- | --- |
| 1–5 dipendenti | Founder / CEO | — | [BASE] |
| 5–10 dipendenti | Founder / CEO | — | [BASE] |
| 5–15 dipendenti, caso generale | Founder / CEO | COO / CFO | [BASE] |
| 15–50 dipendenti, caso generale | CEO | CFO / COO / Head of People | [BASE] |
| 15–50 dipendenti con operations complesse | COO / CFO | CEO | [BASE] |
| Hiring intenso | CEO / COO | Head of People | [BASE] |
| SaaS / AI e privacy | Founder / CEO | COO; CTO solo se il pain è molto tecnico | [BASE] |
| Fundraising / governance | CEO | CFO | [BASE] |
| Clienti o contratti su più paesi | CEO | CFO / Finance Manager | [LOOK] (testimonianza del Finance Manager di Eccentrica sui contratti con clienti su più giurisdizioni; identificazione dell'azienda non confermata), [DEC] |
| Filiale italiana di un gruppo estero | Country Manager | — | [LOOK]. **Fuori MVP** per [DEC]: riportato solo per quando il segmento verrà riconsiderato |

## 7. Conflitti tra file

| # | Tema | Cosa dicono i file | Cosa segue questo documento |
| --- | --- | --- | --- |
| C1 | Perimetro e priorità | [BASE] e [BASE] fissano il perimetro a 5–50 con priorità sul 5–15. [DEC] porta il perimetro a 1–50 ed esclude priorità tra 1–5, 5–15 e 15–50 | [DEC]: perimetro 1–50, nessuna priorità nell'MVP; la decideranno i dati |
| C2 | Filiali di gruppi esteri | [LOOK] (Implicazioni) le propone come nuovo segmento, con il Country Manager come buyer e i dipendenti misurati sull'entità italiana. [DEC] le esclude dall'MVP | [DEC]: escluse; da riconsiderare dopo l'MVP |
| C3 | Modelli di business | [BASE] punta su SaaS e tech. [LOOK] (Pattern) osserva che nessun cliente attuale è SaaS o tech e che la dimensione internazionale conta più del settore | [DEC]: elenco dei modelli invariato, dimensione internazionale aggiunta come segnale forte |
| C4 | Buyer | [BASE] privilegia founder e CEO nelle aziende piccole. [LOOK] mostra Finance Manager e Country Manager come firmatari | [DEC]: il buyer non è sempre il founder; aggiunto lo scenario "clienti o contratti su più paesi" |

## Da decidere

- **X**: soglia di fatturato oltre la quale un'azienda è fuori perimetro. Tra €50M e X l'azienda resta dentro con il flag "fuori dai piani pubblici, da verificare" [DEC].
