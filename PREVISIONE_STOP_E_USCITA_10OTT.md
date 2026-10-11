# Previsione registrata: lo stop a 0,30 e il bersaglio più alto

**Scritta il 10 ottobre con 21 chiusure, PRIMA di misurare sulle prossime.** Vale su posizioni
che oggi non esistono ancora. Se la pubblico dopo, non è una previsione: è un racconto.

## Cosa ho misurato sulle 21 chiuse

La simulazione cammina sul prezzo di ogni posizione e riproduce la regola viva con uno scarto
massimo di **3 punti**: è il cancello che mi autorizza a leggere il resto. (Al primo tentativo
lo scarto era 76 punti su un caso — il cammino campionava un prezzo ogni cinque scambi e il
tocco del raddoppio di `0x9f47c581011d`, max 2,01, cadeva fra due campioni. Ora ogni campione
porta il minimo e il massimo del suo intervallo: versione 2 del database.)

### Lo stop in perdita

| stop | media | intervallo 95% | vinte | fermate | raddoppi |
|---|---|---|---|---|---|
| niente | +6,5% | ±34,0 | 10 | 0 | 9 |
| 0,20 | +7,5% | ±33,4 | 10 | 6 | 9 |
| **0,30** | **+10,2%** | ±32,0 | **10** | 6 | **9** |
| 0,40 | −1,6% | ±30,0 | 8 | 9 | 7 |
| 0,50 | +2,3% | ±28,5 | 8 | 11 | 7 |
| 0,70 | +2,1% | ±24,4 | 6 | 14 | 6 |

**Tutti gli intervalli contengono lo zero: nessuna riga dimostra niente.** Quello che si vede non
è una media, è una **forma**: fino a 0,30 non muore nessuna vincente (10 restano 10, 9 raddoppi
restano 9) e si fermano 6 perdenti; da 0,40 si rompe. Il motivo è strutturale e non è un
adattamento: la discesa peggiore **prima** del raddoppio, fra le dieci vincenti, ha mediana
0,817x e minimo **0,165x**. Lo spazio fra 0,165 e 0,40 è un corridoio vuoto, non un picco
trovato provando.

### Dove uscire

| regola | media | intervallo | vinte | migliore |
|---|---|---|---|---|
| 2x secco (la regola viva) | +6,5% | ±34,0 | 10 | +90% |
| 3x secco | +25,7% | ±50,4 | 9 | +185% |
| 5x secco | +25,4% | ±67,3 | 8 | +375% |
| 2x poi cordino −30% | +3,8% | ±35,0 | 10 | +175% |
| 2x poi cordino −50% | −4,4% | ±32,6 | 9 | +149% |
| 2x poi cordino −60% | −14,6% | ±26,9 | 8 | +99% |
| **2x + stop 0,30** | **+10,2%** | **±32,0** | 10 | +90% |

Il cordino che segue il massimo **peggiora** tutto, e più è largo più peggiora: queste monete
non scendono, crollano, e il cordino restituisce più di quanto cattura. È il contrario
dell'intuito, ed è la cosa più solida di questa tabella perché è monotona su tre valori.

### Perché spostare il bersaglio non paga quanto sembra

| arrivata a | arriva a | quante | il passo moltiplica | attesa |
|---|---|---|---|---|
| 1,5x | 2x | 9/13 = 69% | ×1,33 | 0,92 |
| 2x | 3x | 6/9 = 67% | ×1,50 | 1,00 |
| 3x | 4x | 6/6 = 100% | ×1,33 | 1,33 |
| 4x | 5x | 3/6 = 50% | ×1,25 | 0,62 |

L'attesa oscilla intorno a 1: la coda è grassa quanto basta a rendere **quasi indifferente** dove
si incassa. Il +25,7% del «3x secco» vive su sei casi e ha un intervallo di ±50: non è un
risultato, è rumore con una media simpatica.

## Quanto campione serve davvero

Dispersione misurata: **80 punti per posizione**. Quindi, per distinguere due regole:

| differenza da distinguere | posizioni per braccio | da oggi (16,7 al giorno) |
|---|---|---|
| 50 punti | 19 | 1 giorno |
| 20 punti | 122 | 6 giorni |
| 10 punti | 486 | 27 giorni |

**La differenza fra «niente stop» e «stop 0,30» è di 3,7 punti: non è distinguibile nemmeno
con 486 posizioni.** Questo è il fatto più importante della giornata, e non riguarda lo stop:
riguarda il metodo. Cercare il parametro migliore su questa distribuzione è inutile — la
dispersione è troppo grande e tutte le varianti vivono dentro di essa. Si possono scoprire solo
effetti **grandi**, da 50 punti in su.

## La previsione, perché sia falsificabile

Sulle **prossime 29 chiusure** (per arrivare a 50), prevedo:

1. **«2x + stop 0,30» non batterà «2x secco» di più di 10 punti.** Mi aspetto una differenza
   compresa fra −10 e +10 punti. Se la batte di più di 20 punti, la mia lettura è sbagliata e
   lo scriverò.
2. **Il cordino resterà peggiore del 2x secco**, in tutte e tre le larghezze. Questa è la
   previsione che mi gioco: è monotona oggi e deve restare monotona.
3. **La media del 2x secco resterà indistinguibile da zero** (intervallo che contiene lo zero)
   anche a 50 chiusure.

Se la 3 cade — cioè se a 50 chiusure la media è solidamente positiva — allora abbiamo qualcosa
e si passa alla domanda della capienza. Se regge, la strada non è il parametro: è la selezione
(già bocciata una volta) o un mercato diverso.

## Cosa NON cambio

Niente. La regola viva resta 2x secco senza stop, e resta congelata. Cambiarla adesso
renderebbe le posizioni nuove non confrontabili con le vecchie, bruciando il solo campione
pulito che abbiamo — e lo farei sulla base di 3,7 punti di differenza dentro un intervallo di 32.
