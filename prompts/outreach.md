# Prompt: bozza di sequenza outbound

Uso: per ogni lead Tier A (e B, se richiesto) dopo la verifica delle fonti. Il sistema **non invia nulla**. Le bozze vanno rilette e corrette a mano (`docs/decisions.md`, Output).

## Principi

1. **I segnali sono per noi, non per l'email.** Paesi, assunzioni, marketplace e articoli servono a scegliere chi contattare e quando. Nel testo non si citano e non si parafrasano: suonerebbero come un'AI che ripete quello che ha appena letto (`docs/decisions.md`).
2. **Niente esempi di casi legali** e niente frasi che spiegano al lettore cosa potrebbe succedergli.
3. **Registro di mezzo.** "Buongiorno" e "tu", chiusura con "Un saluto". Niente formule troppo confidenziali ("Ciao", "non ti disturbo più", "dimmelo pure") e niente formule rigide da lettera. Frasi corte, nessun gergo legale, nessun complimento.
4. **Chi siamo in una frase, poi una domanda sul suo modo di lavorare oggi**, cioè avvocato chiamato quando serve o riferimento fisso. La domanda apre una conversazione e non chiede tempo (Josh Braun).
5. **Breve.** Email 1 sotto le 70 parole, follow-up sotto le 50. Le email corte ricevono più risposte e si leggono dal telefono (dati Lavender).
6. **Oggetto neutro**, di 2-3 parole, che sembri un'email tra colleghi.
7. **Il follow-up aggiunge un elemento del servizio** (costo noto, disdetta, piani) e lascia una via d'uscita.
8. **LinkedIn: nessuna vendita** nella richiesta di collegamento.
9. **La personalizzazione sta nel destinatario, non nel testo**: la versione cambia solo in base al ruolo (titolare o finanza).
10. **Trasparenza sul contatto.** La prima email chiude con una riga che dice da dove viene il contatto e come non riceverne altri (`docs/decisions.md`, Contatti).

## Vincoli del progetto

- Su Iusful solo fatti di `docs/iusful_product.md`, possibilmente con le parole del sito: "il partner legale per la tua impresa", avvocato dedicato in abbonamento, "anticipa le questioni invece di reagire", costo noto in anticipo, nessun costo senza approvazione, recesso con 30 giorni di preavviso.
- Non scrivere che l'abbonamento sostituisce le parcelle o rende fisse le spese legali. Il piano include una quota di attività (10 richieste e 3 ore di call al mese); il lavoro in più, o di uno specialista, si paga a parte su preventivo approvato (pagina Piani, verificata il 4 ottobre 2026).
- Mai dire o lasciar intendere che l'azienda ha un problema legale.
- Firma con un segnaposto (`[Nome], Iusful`): chi invia è il team commerciale di Iusful.

## Fonti consultate

- Josh Braun, CTA delle cold email: https://joshbraun.com/cold-email-ctas/
- Josh Braun, Ditch the Pitch, Poke the Bear: https://joshbraun.com/ditch-the-pitch-poke-the-bear/
- Lavender, Cold Email 101: https://lavender.ai/blog/cold-email-101
- Perché una cold email sembra scritta da un'AI (dati Lavender): https://somethinginc.com/blog/cold-email-sounds-like-ai-lavender-data/
