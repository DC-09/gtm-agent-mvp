# Revisione dei lead dubbi

Dal 3 ottobre 2026 i lead non si controllano più uno per uno (`docs/decisions.md`, sezione Verifica). `scripts/verify_sources.py` verifica le fonti di ogni lead qualificato; qui arrivano solo quelli con Verifica **Da rivedere** nel CRM Notion.

## Quando un lead è "Da rivedere"

| Motivo | Esempio | Cosa fare |
| --- | --- | --- |
| Possibile esclusione non risolta | Un articolo cita un fondo di venture capital, ma non è chiaro se abbia investito | Cerca la conferma (visura, comunicato, sito del fondo). Se l'esclusione è vera, il lead va scartato; se non lo è, scegli **Rivista a mano** |
| Il tier dipende da un fatto non confermato | La pagina del segnale principale non si apre più, e senza quel segnale il lead scenderebbe da A a C | Apri la fonte: se il fatto c'è, scegli **Rivista a mano**; se non c'è più, dillo all'agente, che rivaluta il lead |

Il motivo preciso è nel campo **Motivo verifica** dell'azienda. Dopo la revisione, scegli **Rivista a mano**: i successivi invii da n8n non sovrascrivono la scelta. Se la decisione vale anche per i casi futuri, va scritta in `docs/decisions.md`.

## Cosa non arriva qui

- Pagine bloccate o fatti non confermati che non cambiano il tier: restano note nel Motivo verifica.
- Dati semplicemente mancanti (fatturato, città): sono già penalizzati nello score.
- Informazioni viste solo in anteprime di ricerca: non sono fonti.

## Storico

Il 3 ottobre 2026 sono stati verificati a mano su ufficiocamerale i dipendenti di UNALOE (1), SD Calabria (1), Cuore Lavico (2), 4 FOOD SRL (4) e Dmora (19). La prima verifica automatica sui 5 lead qualificati ha dato 5 su 5 "Superata".

Il 4 ottobre 2026 è arrivato il primo lead "Da rivedere": All4cycling, controllata all'80% da Sportler spa. Decisione: le controllate di gruppi italiani non sono escluse (`docs/decisions.md`, Perimetro). Il lead resta in Tier B con Verifica "Rivista a mano".
