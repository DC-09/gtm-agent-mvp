# Controllo settimanale dei segnali

Nell'MVP si lancia a mano. È pensato per partire da solo ogni lunedì come attività pianificata dell'app Claude (istruzioni in fondo): l'attività è stata creata e provata il 4 ottobre 2026, poi tolta per non farla girare davvero. Lavora nella cartella del repository. Valgono tutte le regole di `CLAUDE.md`: nessun fatto inventato, ogni segnale con URL e data, un'anteprima di ricerca non è una fonte, nessun invio di outreach.

Obiettivo: trovare cosa è cambiato da una settimana all'altra nelle aziende già valutate, aggiornare i punteggi e il CRM, e lasciare una sintesi leggibile. Non si cercano aziende nuove: quello è un altro lavoro.

## Passi

1. **Ramo di lavoro.**
   - Se esiste una pull request aperta il cui ramo inizia con `claude/settimanale-`, parti da quel ramo.
   - Altrimenti aggiorna `main` e crea `claude/settimanale-<AAAA-MM-GG>`.
   - Non fare mai il merge: lo decide il revisore.
2. **Parte meccanica.** Esegui `python scripts/watch_signals.py` e leggi `data/weekly/novita_<data>.json`:
   - `page_changes`: frasi nuove nelle pagine sorvegliate (annunci di lavoro, comunicati);
   - `aging`: lead che cambiano punteggio solo perché i segnali sono invecchiati;
   - `page_errors`: pagine non raggiungibili, da segnalare nella sintesi.
3. **Annunci e notizie con Clay.**
   - Per tutti i lead con status `QUALIFIED` o `RESERVE`, cerca le aziende per dominio con il connettore Clay (`search-companies`).
   - Aggiungi i dati "Open Jobs" e "Recent News" (`add-company-data-points`) e leggi i risultati con `get-task-context`.
   - Considera solo annunci e notizie non già presenti tra i `signals` del lead (stesso URL o stesso fatto).
4. **Decidere se una novità è un segnale.** Per ogni frase nuova, annuncio o notizia applica `prompts/trigger_research.md` e la mappa di `docs/icp.md` §4.1:
   - apri la fonte e copia la frase esatta in `evidence_quote`;
   - la data deve essere scritta nella fonte, oppure è un annuncio senza data, che vale come datato al giorno della consultazione;
   - una notizia senza voce corrispondente nella mappa non è un segnale: va solo nella sintesi;
   - se una fonte fa nascere un dubbio di esclusione (oltre 50 dipendenti, fondo VC, gruppo estero), aggiungilo in `doubts` e non decidere da solo.
5. **Aggiornare i lead.**
   - Aggiungi i segnali nuovi in `data/leads.json`.
   - Per ogni lead toccato, o presente in `aging`, porta `evaluation_date` a oggi e ricalcola `score`, `tier`, `status` e le `score_reason` con le regole di `docs/scoring.md`.
   - Un lead che passa da C a B deve avere `legal_pains` e `outreach_angle`.
6. **Controlli e invio.** In ordine, fermandoti se uno fallisce:
   - `python scripts/validate_leads.py`
   - `python scripts/verify_sources.py`
   - scrivi la sintesi (passo 7)
   - `python scripts/export_payload.py`
   - `python scripts/push_n8n.py --handoff`

   Se n8n non risponde (`http://localhost:5678/healthz`), salta l'invio e scrivilo nella sintesi.
7. **Sintesi.** Scrivi `data/weekly/sintesi_<data>.txt`, al massimo 1.500 caratteri, in italiano semplice:
   - nuovi segnali, con azienda, fatto e fonte;
   - lead saliti o scesi di tier;
   - lead da rivedere e perché;
   - pagine non raggiungibili;
   - crediti Clay usati, se il connettore li indica.

   `export_payload.py` la mette nel report del funnel su Notion, campo "Novità della settimana".
8. **Commit e pull request.**
   - Committa `data/` e la sintesi sul ramo, con un messaggio che dica cosa è cambiato.
   - Apri la pull request verso `main`, o aggiorna quella aperta.
   - Non toccare codice, prompt o regole: se servono modifiche, scrivile nella sintesi come proposta.

## Quando non c'è nulla di nuovo

Si fa comunque il giro completo. La sintesi dice "nessuna novità" e il report del funnel registra la settimana.

## Come si attiva in automatico

Nell'app Claude, sezione "Scheduled", si crea un'attività con pianificazione `5 8 * * 1` (ogni lunedì alle 8:05, ora locale) e questo testo:

```
Lavora nel repository del progetto Iusful GTM Agent. Leggi prima CLAUDE.md,
poi segui alla lettera prompts/settimanale.md: è la procedura del controllo settimanale dei segnali.
Regole: non inventare fatti; un'anteprima di ricerca non è una fonte; non inviare email o messaggi;
non modificare codice, prompt o regole del punteggio; i dubbi di esclusione si segnano in doubts.
Alla fine rispondi in italiano semplice: cosa è cambiato, lead saliti o scesi, da rivedere, link alla PR.
```

Gira solo con l'app aperta; se è chiusa, parte alla riapertura. Alla prima esecuzione conviene usare "Run now", per approvare una volta i permessi di Clay e GitHub.
