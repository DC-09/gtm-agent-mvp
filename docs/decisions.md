# Decisioni

Una riga per scelta, con il motivo. Le scelte aperte stanno in fondo.

## Perimetro
- Solo aziende italiane tra 1 e 50 dipendenti (non più da 5). I piani pubblici di Iusful vanno da 1 a 50 dipendenti, Essential compreso (1-5), e il servizio è pensato per PMI italiane: oltre non c'è un'offerta da proporre. Due clienti attuali su quattro risultano in fascia 1-5, secondo stime ancora da verificare in docs/clienti_lookalike.md.
- Il momento giusto è quando la complessità legale sta crescendo, non durante un problema puntuale: si legge dai segnali di crescita, non dalla presenza di un legale. Il concorrente reale è lo status quo (avvocato chiamato al bisogno).
- Brevetti depositati e cause in corso non escludono un'azienda. Sono incarichi puntuali, non copertura del bisogno complessivo; il brevetto può anzi indicare attività IP ricorrente.
- La copertura legale strutturale non è un criterio: nessuna esclusione, penalità o flag.
- Fatturato a intervalli: fino a €50M normale, il fatturato indica solo il piano plausibile; da €50M a X dentro con flag 'fuori dai piani pubblici, da verificare'; oltre X fuori. X da decidere.
- Cause in corso e crediti insoluti sono neutri: bisogni reali ma raramente osservabili dall'esterno per una PMI, quindi non entrano nella mappa segnali.
- Nessuna priorità tra 1-5, 5-15 e 15-50 nell'MVP: i clienti attuali non la sostengono; la decideranno i dati.
- Se i dipendenti non sono verificati, il lead non può superare il Tier B: il numero di dipendenti è il criterio di perimetro, e senza verifica il lead non è pronto per l'outreach.
- (3 ottobre 2026) Una fascia di dipendenti presa da una fonte (es. LinkedIn "11-50") che cade tutta dentro 1-50 vale come dipendenti verificati. Le PMI raramente pubblicano il numero esatto, ma per il perimetro basta sapere che stanno dentro la fascia. Una fascia che tocca lo 0 (es. "0-4") non basta.
- (3 ottobre 2026) Il target sono le PMI del tessuto produttivo italiano, sul modello di Elodie Brides: e-commerce e aziende con un minimo di spinta d'innovazione.
- (4 ottobre 2026) Due segmenti in più, oltre a e-commerce e retail: **servizi B2B e B2C** e **sanità e formazione private**. I 22 qualificati erano tutti e-commerce, mentre solo 1 dei 4 clienti attuali di Iusful lo è. Nuovi modelli "Servizi B2C" e "Sanità e formazione", con lo stesso minimo di innovazione: un canale digitale verificabile (prenotazione, acquisto o corsi online). Nuove righe della mappa: servizi continuativi (strutturale), dati sanitari, biometrici o di minori (strutturale, forte), gare e convenzioni con enti (evento), nuovo servizio (evento). Manifattura e catene restano possibili ma non sono una priorità.
- (4 ottobre 2026) Il target comprende anche il retail in senso largo: catene di negozi fisici, boutique, rivenditori e marketplace che vendono prodotti di altri, non solo e-commerce di marca. Resta il minimo di spinta d'innovazione: chi vende online prende i punti del modello "E-commerce e marketplace"; un negozio solo fisico resta "Fuori elenco" (0 punti, non escluso).
- (4 ottobre 2026) Se una fonte scritta dà un numero di dipendenti diverso dalla fascia LinkedIn di Clay, vale la fonte scritta. Primo caso: Ottica Foppa, "11-50" su LinkedIn, ma "24 negozi e oltre 110 dipendenti" su BergamoNews (28/11/2025), quindi scartata. Per le catene con molti negozi la fascia LinkedIn va sempre controllata.
- (4 ottobre 2026) Clay entra nel processo per il sourcing: "Find Companies" con filtri Italia, 2-50 dipendenti, settori retail e parole chiave e-commerce (docs/clay.md). La fascia di dipendenti di Clay viene da LinkedIn e vale come verifica. L'export si scarica da Tools → Export → Download CSV e scripts/import_clay.py lo prende dalla cartella Download.
- (3 ottobre 2026) Escluse le aziende finanziate da fondi di venture capital: almeno un round da un fondo VC (anche corporate VC o CDP Venture Capital), verificato da una fonte. Non contano come esclusione premi, bandi, crowdfunding, business angel senza fondo, aumenti di capitale tra soci.
- (3 ottobre 2026) "Minimo di spinta d'innovazione" si legge come almeno un canale o prodotto digitale verificabile: e-commerce o vendita online propria, servizio o prodotto digitale, iscrizione alla sezione delle PMI innovative. L'iscrizione come startup innovativa non basta. Nello scoring coincide con l'elenco dei modelli di business di docs/icp.md §3; la ricerca dei candidati parte da aziende che lo hanno.
- (3 ottobre 2026) Se due fonti sui dipendenti non coincidono (es. LinkedIn "2-10" e un registro che indica 0), i dipendenti restano non verificati finché non si controlla a mano. La fascia LinkedIn conta anche titolari e collaboratori, il registro solo i dipendenti: per una ditta individuale la differenza decide tra lead ed esclusione. Un dato che compare solo nell'anteprima di un motore di ricerca, su una pagina che non si apre o non esiste più, non è una fonte.
- (3 ottobre 2026) I dipendenti non verificati si penalizzano una volta sola: 0 punti nella dimensione del company fit e tetto al Tier B, senza togliere altri punti in evidence_quality. Prima lo stesso dato mancante pesava tre volte (−10, −3 e tetto), e bastava a far scartare un'azienda altrimenti buona.
- Filiali italiane di gruppi esteri escluse dall'MVP per semplicità: dimensione, buyer e struttura legale sono più difficili da leggere. Non è un giudizio sul segmento: Healthcademia, cliente attuale, è proprio una filiale. Da riconsiderare dopo l'MVP.
- (4 ottobre 2026) Una PMI controllata da un gruppo italiano non è esclusa: l'esclusione vale solo per i gruppi esteri. Primo caso: All4cycling (Lunar Sport srl), 80% di Sportler spa dal 2021, resta in lista. Il fondatore è ancora alla guida e l'azienda resta sotto i 50 dipendenti.

## Output
- Nessun invio reale di messaggi: il sistema produce solo bozze, l'invio spetta al team commerciale di Iusful.
- Outreach come sequenza di 2-3 messaggi in bozza, in italiano naturale, rivista a mano.
- (4 ottobre 2026) I segnali della ricerca non compaiono nelle email: servono a scegliere chi contattare e quando. Citati nel testo ("ho letto che vendete in sei paesi…") fanno sembrare l'email un'AI che ripete quello che ha appena letto. Le email sono neutre e informali, senza esempi di casi legali, e cambiano solo in base al ruolo del destinatario. Principi in prompts/outreach.md.
- Il report di funnel è parte del sistema, non un extra: a ogni esecuzione mostra qualificati, scartati e motivi.

## Stack
- n8n per i flussi verso il CRM; Clay per dati aziendali e persone, in versione leggera.
- Claude Code gira in locale, perché n8n è su localhost.
- (3 ottobre 2026) CRM su Notion, strutturato come un CRM: database Aziende, Persone e Interazioni, stato del lead e vista pipeline (docs/crm.md). È scelto per praticità nell'MVP; l'idea è un CRM vero, per esempio HubSpot, e il passaggio cambia solo l'ultimo nodo di n8n.
- (3 ottobre 2026) Gli script non dipendono dal CRM: export_payload.py produce un JSON per n8n e un CSV importabile a mano in qualsiasi CRM. Se un servizio salta, cambia solo l'ultimo passaggio.
- (3 ottobre 2026) Il piano gratuito di Clay è limitato a 50 righe per tabella (FAQ di Clay): basta per l'MVP, che si ferma a 50 aziende.
- (3 ottobre 2026) n8n gira in locale con Node.js invece che con Docker: resta gratuito e raggiungibile su localhost.
- (3 ottobre 2026) Tutti i lead valutati, anche Tier C e scartati, stanno in data/leads.json e rispettano lo stesso schema. Servono al report di funnel, che deve mostrare anche gli scartati e il motivo; a n8n si esportano solo A e B.

## Scoring
- (4 ottobre 2026) "Vende all'estero" resta com'è e non toglie punti a nessuno. Il problema era il contrario: solo l'export dava il bonus "forte", quindi una catena o un rivenditore che vende solo in Italia partiva con circa 8 punti in meno. Le nuove righe della mappa: "rete di 3 o più punti vendita o sedi" (forte, strutturale) e "nuova apertura o acquisizione" (evento datato). Il target non è solo l'e-commerce che esporta.
- (3 ottobre 2026, sostituisce la regola dei 6 mesi) Un buying signal vale punti pieni fino a 12 mesi, metà punti (arrotondati per difetto) tra 12 e 18 mesi, zero oltre i 18 mesi o senza data verificabile. Con 6 mesi anche un'azienda perfetta senza notizie recenti restava sotto 65, e le PMI producono poche notizie datate. La data resta obbligatoria: un segnale senza data non dice che la complessità sta crescendo adesso.
- (3 ottobre 2026) Un annuncio di lavoro ancora online senza data di pubblicazione vale come datato al giorno della consultazione: se è online, l'azienda sta cercando persone adesso. Vale solo per le righe che un annuncio può mostrare (assunzioni, lavoro da remoto o ibrido, freelance, ruoli per mercati esteri), e una stessa pagina di annunci conta come un solo segnale, quello che vale di più: altrimenti una sola pagina careers produrrebbe da sola tre segnali.
- Se la fonte dà solo mese o anno, l'età si calcola dal primo giorno del mese o dell'anno. È la scelta prudente: il segnale risulta più vecchio, non più giovane.
- "Aziende innovative" significa solo: iscritte alla sezione speciale del Registro delle imprese come PMI innovativa. Senza questa verifica il criterio non si applica. Il termine era troppo vago per essere applicato in modo verificabile. (3 ottobre 2026) Tolta l'iscrizione come startup innovativa.
- (3 ottobre 2026) Il modello "B2B" generico resta nell'elenco così com'è: un'azienda B2B prende i punti del modello anche senza un canale digitale.
- (4 ottobre 2026) Regole fissate: ICP e scoring alla versione 5. Da qui i lead cambiano solo per fatti nuovi, non per regole nuove; un cambio di regola si propone e si decide prima di applicarlo, poi si rivalutano tutti i lead.

## Verifica
- (3 ottobre 2026) Niente controllo manuale su ogni lead: non regge oltre poche decine di aziende. Ogni lead qualificato passa da scripts/verify_sources.py, che riapre le fonti e cerca, in modo tollerante e nello stesso tratto di testo, la frase copiata dalla fonte (`evidence_quote`) per ogni segnale che dà punti e il nome del buyer.
- (3 ottobre 2026) Al revisore arriva un lead ("Da rivedere") solo in due casi: un indizio concreto di esclusione non risolto (`doubts`), oppure un tier che cambierebbe togliendo i fatti non confermati. Una pagina bloccata o un fatto secondario non confermato che non cambia il tier resta una nota. Niente controllo a campione. La soglia è volutamente larga: la persona interviene solo dove una decisione sbagliata cambierebbe l'esito.
- (4 ottobre 2026) Un buyer trovato da Clay ("Find contacts at company", filtro Founder, Owner, Partner, C-suite) con il suo profilo LinkedIn vale come confermato: LinkedIn blocca la lettura automatica e il profilo è la fonte. Se il ruolo restituito da Clay non è quello chiesto (es. uno sviluppatore), il buyer non si usa. Quando possibile si conferma il nome sul sito aziendale o in un articolo.
- (3 ottobre 2026) Un'informazione vista solo in un'anteprima di ricerca non è un dubbio da rivedere (es. l'aumento di capitale di 4 FOOD): non è una fonte.
- (3 ottobre 2026) Passaggio al sales automatico: un Tier A con Verifica "Superata" o "Rivista a mano" va in "Pronto per sales" (flusso HANDOFF_SALES). L'ultimo controllo umano resta la revisione delle bozze di outreach, che si fa comunque.
- (4 ottobre 2026) Nel CRM l'esito di una revisione si chiama "Rivista a mano", senza nomi di persona: chi rivede può cambiare.

## Clienti attuali
- I quattro clienti citati sul sito servono a correggere l'ICP, non a ridisegnarlo: sono pochi e almeno due provengono dalla stessa rete personale, quindi probabilmente non rappresentano il mercato.
- Dai clienti attuali entrano nell'ICP due correzioni: la dimensione internazionale (clienti o contratti su più paesi) come segnale forte, e un buyer che non è sempre il founder.

## Aperte
- Soglia X di fatturato oltre la quale un'azienda è fuori perimetro.
