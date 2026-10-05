# Clay nel sistema

Clay fa la parte di dati aziendali: trovare aziende, dipendenti, pagina LinkedIn, persone da contattare, annunci aperti e notizie. Claude Code fa segnali, buyer, punteggio e verifica. Ogni dato di Clay è un punto di partenza da confermare su una fonte, non un fatto.

## Come si usa

| Uso | Strumento di Clay | Cosa entra nel lead |
| --- | --- | --- |
| Trovare candidati | Find Companies (Italia, 2-50 dipendenti, settore) e, dal connettore, `search-companies` | Nome, dominio, LinkedIn, fascia di dipendenti, città |
| Trovare il buyer | Find contacts at company (Founder, Owner, Partner, C-suite) | Nome e ruolo, poi confermati su sito o articolo quando possibile |
| Cercare segnali | Open Jobs e Recent News (`add-company-data-points`) | Solo dopo aver aperto la fonte e copiato la frase esatta |

Clay è collegato a Claude Code con il connettore (workspace "Diego's Workspace"), quindi l'agente lancia ricerche e arricchimenti senza passare da file. Gli export CSV, quando servono, si importano con `scripts/import_clay.py`, che esclude in automatico gli studi legali e prepara la lista dei candidati.

## Regole sui dati di Clay

- Numero o fascia di dipendenti tutta dentro 1–50, con fonte: dipendenti verificati.
- Fonti in conflitto o dato stimato: dipendenti non verificati e, se il conflitto decide il perimetro, un dubbio da rivedere (`docs/decisions.md`).
- Un dato di Clay senza fonte non vale come verifica: Clay aggrega provider diversi e non sempre dice da dove viene il numero.
- "employee_count" di Clay a volte non coincide con la fascia dichiarata (in un caso 82 persone contro 11-50): vale come dubbio, non come dato.
- Una fonte scritta sui dipendenti vale più della fascia LinkedIn. Ottica Foppa risultava "11-50", ma la stampa locale scrive "oltre 110 dipendenti".
- Se il ruolo restituito da Find contacts non è quello chiesto (es. uno sviluppatore), la persona non si usa.

## Cosa ha funzionato e cosa no

- **Find Companies** ha diversificato le fonti, che all'inizio venivano quasi tutte da articoli su Amazon e Temu. "Find contacts at company" su 50 aziende: circa 25 crediti, 22 persone, 3 scartate per ruolo sbagliato.
- **Open Jobs e Recent News** su 21 lead in Tier B e C: annunci aperti per una sola azienda (Ottica Dalpasso, poi verificati sulla pagina). Le PMI piccole pubblicano poco su LinkedIn.
- **Segmenti servizi e sanità:** su 17 agenzie, società IT e strutture sanitarie solo You Medical aveva annunci aperti, ed è entrata in Tier A. Le agenzie non pubblicano annunci su LinkedIn e le loro "notizie" sono articoli del blog. Per questo segmento le pagine "lavora con noi" hanno dato più segnali di Clay (Secret Key, Bottega52).
- Gli annunci di una società di selezione sono per i suoi clienti: non sono assunzioni dell'azienda.

## Ricerca dal connettore

`search-companies` usa una query DSL. Funzionano `industry`, `domain` ed `employee_count`; il paese no. Per l'Italia si filtra sul dominio:

```
select from companies where industry in ("Medical Practices", "Professional Training and Coaching")
  and domain ends_with ".it" and employee_count >= 8 and employee_count <= 45 limit 25
```

Nei risultati vanno tolti a mano associazioni, società scientifiche, gruppi grandi e filiali estere.

## Dati personali

Dai file di Clay entrano nel repository solo le persone scelte come buyer, in `data/leads.json` con la loro fonte.
