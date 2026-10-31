# Il campione era storto, e il +18,9% è sotto revisione — 8 ottobre 2026

## Cosa ho trovato

Il nostro registro dei pool copre **un pool su dodici** (il tasso di diploma vero è l'8%, non lo
0,77%). Allora ho costruito un campione di diplomate **dalla chain**: 400 lanci casuali → 31
diplomate (7,8%), e per ognuna l'id del pool preso dall'evento `Initialize` nella transazione del
diploma.

Misurando su quelle, il quadro è un altro mondo:

| | diplomate casuali (35) |
|---|---|
| pool **senza nessuno scambio** | **27** |
| comprabili dalla regola (≥5 scambi nel primo minuto) | **6 (17%)** |
| non comprabili (meno di 5 scambi) | 2 |

Verificato che non fosse un mio difetto di lettura: su 10 controllate una per una, 5 hanno un pool
con **zero** scambi, le altre hanno 1, 4, 559, 1.775, 15.567. Non è la mia finestra di blocchi:
**quei pool non scambiano.**

## Cosa significa per il risultato di stamattina

Il **+18,9%** (e il +15,2% con lo scivolamento) era misurato su monete estratte dal nostro
registro, cioè **le più attive** — quelle che i raccoglitori avevano visto scambiare. Sul campione
casuale, sulle 6 comprabili il risultato è **−23,9% di media**.

**Sei monete non decidono niente**, e non le uso per smentire 334. Ma sono abbastanza per dire una
cosa: **il +18,9% è sotto revisione, e non lo userò per nessuna decisione finché non è rifatto su
un campione casuale abbastanza grande.**

## La parte che resta valida, e non è poca

La condizione d'entrata — **almeno 5 scambi nel primo minuto** — si conosce **al momento di
comprare**, non dopo. Quindi non è uno sguardo al futuro: è un filtro legittimo. La strategia non è
«compro ogni diplomata», è «compro ogni diplomata **che scambia subito**», e quelle sono il 17%.

Questo rende il lavoro più piccolo e più onesto: su 100 lanci, 8 si diplomano e circa 1,4 sono
comprabili.

## Cosa sto facendo

1. Sta girando il campione grande: 1.600 lanci casuali → circa 125 diplomate → circa 21
   comprabili. Non basta ancora: ne servono ~80, cioè ~6.000 lanci. Continua.
2. **La prova in avanti resta il giudice vero**: riconosce i pool in diretta dagli scambi del
   gestore, quindi vede tutte le diplomate e non eredita questo difetto.

## La lezione, perché è la terza volta in due giorni

Un campione preso da «quello che abbiamo già raccolto» non è un campione del mondo: è un campione
di **noi**. Le prime due volte era la finestra di blocchi (vedevamo un quarto della storia di ogni
moneta) e il filtro sui 40 scambi. Questa è la stessa famiglia, al livello del registro.

Da ora, per ogni misura: **da dove viene il campione, e cosa esclude per costruzione?** Scritto
come domanda obbligatoria, non come buona abitudine.
