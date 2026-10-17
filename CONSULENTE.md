# 🔭 IL CONSULENTE ESTERNO — cosa ha detto, e se aveva ragione

*Aggiornato a mano dopo ogni consulenza. Serve a rispondere con un numero, non con un'impressione,
alla domanda: **il consulente vale il posto che occupa nell'architettura?***

## Che cosa risponde davvero (10/09/2026)

Lo chiamiamo "Astra", ma **non è più gpt-6-astra**. Dopo il cambio di piano, l'account rifiuta
qualsiasi modello richiesto per nome:

| modello chiesto | risposta |
|---|---|
| `gpt-6-astra` | ❌ non supportato con un account ChatGPT |
| `gpt-6` | ❌ non supportato |
| `gpt-5.2-codex` | ❌ non supportato |
| `gpt-5-codex` | ❌ non supportato |
| *(nessun modello: il default)* | ✅ risponde |

Quindi: **abbiamo un modello Codex, non Astra**, e non possiamo sceglierlo. Il nostro script per
fortuna non ha mai chiesto un modello per nome — imposta solo lo sforzo di ragionamento — ed è per
questo che ha continuato a funzionare senza che ce ne accorgessimo.

> **Il nome non è la cosa.** Chiamarlo Astra quando non lo è è la stessa trappola del "sembra attivo
> perché lo script esiste". Vale per quello che produce, non per come si chiama.

## Il registro

| data | affermazione principale | verificata? | cosa abbiamo fatto |
|---|---|---|---|
| 04/09 | «misurate i costi a taglia $25, allineati al momento, **durante la fuga**» | non verificata: **mai eseguita** | ❌ niente — ed è ancora il blocco principale, richiamato il 10/09 |
| 06/09 | consulenza costruita a mano (unica arrivata dal loop automatico) | — | impianto poi rotto per 4 giorni |
| 10/09 | «il metro dei costi è misurato solo su Jupiter, cioè solo su Solana, e con quello classificate Base e Robinhood» | ✅ **VERA** — 815 misure in archivio, **0 su indirizzi EVM**; copertura reale base 0%, robinhood 0%, solana 33% | ✅ costruito `due_gambe.py`, che marca morte come evidenza le classifiche non coperte |

## Come si giudica

Una consulenza conta se produce **un'affermazione che possiamo verificare da soli** e che, verificata,
cambia cosa facciamo. Le frasi che starebbero identiche nella consulenza di un altro progetto non
contano, anche se sono vere.

Finora: **1 affermazione verificata vera su 1 verificabile**, e ha invalidato la classifica su cui
stavamo decidendo. Il posto se lo è guadagnato — ma su tre consulenze in cinque giorni, non sulle due
al giorno che dovrebbe fare.
