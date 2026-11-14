# Il campione guardava dove gli artefatti non sono — 7 ottobre, notte

## Cosa è successo, in ordine

1. I dati del mercato dopo la quotazione sono diventati **puliti**: 42.302 righe, tutte versione
   8, zero righe vecchie. Le due correzioni di stasera (potatura nella corsia + fusione
   consapevole della versione nel pubblicatore) hanno funzionato sulla pipeline vera.
2. La misura è girata e **il cancello l'ha prima bloccata**: un caso su 16 non combaciava. Il
   difetto era **nel controllo, non nel dato**: il verificatore assumeva 18 decimali, e quella
   moneta si paga in un asset a **6** (letti dal suo contratto). 121,70698 veniva letto come
   0,0498. *Un falso allarme è grave come un falso via libera*: ferma una misura giusta e manda
   a cercare un difetto che non c'è. Ora i decimali viaggiano dentro la prova.
3. Con i decimali giusti: **19 casi su 19 combaciano**, verdetto scritto. `1,0718x` di ritorno
   sul capitale, 17,4% mai uscito, 12,6% sopra 2x, **0,5% sopra 10x**.
4. Poi ho guardato i primi otto per moltiplicatore. **Sette su otto sono falsi.**

| dichiarato | incassato secondo noi | secondo la chain | |
|---|---|---|---|
| 2.855x | 14,873 | **0,00625** | falso |
| 2.373x | 3,675 | **0,0015** | falso |
| 2.304x | 3,005 | **0,00110** | falso |
| 2.247x | 9,95 | **9,95e-12** | falso (scala 10¹²) |
| 665x | 26,59 | **0,0099** | falso |
| 470x | 22,25 | **0,00907** | falso |
| 386x | 71,94 | **0,0298** | falso |
| 3.466x | — | tre prove su tre combaciano | da guardare meglio |

Il quarto è lo **stesso portafoglio e lo stesso importo** (`0,00130428`) del caso che Nicolò ha
smontato stamattina aprendo un sito: l'artefatto era ancora lì, sotto un'altra forma.

## La lezione, che è sul metodo di controllo

Il campione era **casuale**, e ha passato 19 casi su 19. Ma gli artefatti non stanno in mezzo
alla distribuzione: stanno **in cima**, perché ordinare per rapporto li seleziona per costruzione.
Un campione casuale è un controllo che guarda dove gli artefatti non sono — e dà un timbro di
garanzia proprio ai numeri che non ha guardato.

Corretto: la prova ora contiene **sempre i primi per moltiplicatore**, più qualcuno a caso. Con
questa regola la misura di stasera **non passa** (20 su 22), e il verdetto è stato cancellato
invece di restare agli atti.

## Dove sta il difetto vero, che si ripara domani

La firma è chiara: `9,95` contro `9,95e-12` è esattamente **10¹²**, cioè 18 decimali usati dove
servivano 6. Il difetto sta nei decimali con cui il lato denaro viene convertito dentro
`chi_tiene_i_graduati`, non nella lettura degli eventi. È la stessa famiglia che ci ha già
morso due volte: *un numero senza la sua unità è indistinguibile da uno con l'unità sbagliata*.

## Cosa resta vero stasera

- i dati sono di una sola generazione, e questo è nuovo;
- il cancello funziona e ha bloccato **due** verdetti in un'ora, uno per colpa sua (decimali) e
  uno per colpa dei dati (scala);
- **nessun numero sul mercato dopo la quotazione è da considerare valido**, nemmeno l'1,0718x;
- il «metro» (il test che distingue l'abilità dal caso) non è stato prodotto: anche se i numeri
  fossero giusti, non direbbero ancora che qualcuno è bravo.
