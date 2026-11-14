# Solana è fuori dal cancello, e lo dichiaro invece di lasciarlo capire

*19 settembre 2026 · scritto perché il fondatore ha chiesto «Solana che fine ha fatto?» e la
risposta onesta era: non l'avevo guardata.*

## Cosa c'è, cosa non c'è

| | stato |
|---|---|
| trades | 4.734 file, aggiornati in continuazione |
| pulse | 220 file, aggiornati |
| **candele** | 1.702 file, **la più recente è di 44 ore fa** |
| censimento | **assente** |
| coppie di token | **assente** |
| nascita dalla catena | **assente** |
| storico / vivo (scambi grezzi) | **assenti** |

Cioè: Solana non ha **niente** della macchina costruita per base e robinhood in questi giorni.
È rimasta all'architettura precedente, quella basata su candele e trade da servizi esterni.

## Perché non è un abbandono per distrazione

Solana era la chain originale, e il verdetto del 6 agosto era stato che lì l'edge non c'era: il
segnale whale era un artefatto, la media forward negativa. Da quel verdetto è nato il pivot su
Robinhood e base. Quindi la scelta di non portarla avanti è deliberata.

**Ma era rimasta accesa a metà, e questo sì era un difetto.**

## Cosa ho spento, e perché

`strategy_optimizer_solana` girava su una serie di prezzo ferma da 44 ore. Un ottimizzatore che
lavora su dati fermi non fallisce: produce risultati che sembrano validi e non lo sono — la stessa
forma del guardiano che vedeva tutto verde mentre sette corsie erano giù, e della eth_call che
rispondeva vuoto senza dire che era un errore.
Spento.

## Cosa resta acceso, e perché

`solana_helius` continua a raccogliere i trade. Costa zero (repo pubblico, nessuna API a pagamento)
e accumula dati che un domani potrebbero servire. Fermarlo non farebbe risparmiare niente e
butterebbe via continuità.

## Cosa NON faccio adesso

Non porto Solana allo standard di base e robinhood — censimento, coppie, nascite, scambi grezzi.
Sarebbe triplicare il lavoro proprio mentre il cancello si sta chiudendo sulle altre due, e per una
chain su cui il verdetto è già stato negativo una volta.
Quando il cancello sarà chiuso, la domanda si potrà riaprire con dati veri invece che con memoria.

## La regola generale che ne ricavo

Un reparto acceso a metà è peggio di uno spento: continua a produrre numeri che nessuno sa essere
vecchi. D'ora in poi, quando una parte del sistema esce dallo scopo, va **dichiarata fuori** per
iscritto e spenta dove produce risultati — non lasciata a girare perché «tanto non fa male».
