# Il giro su GitHub — cosa ho trovato e cosa abbiamo preso

*23 settembre 2026. Il riassunto che avevi chiesto. Niente logiche interne: cosa e' entrato in casa
nostra, cosa e' stato buttato, e quanto e' valso.*

---

## La cosa piu' importante, prima di tutto

**Nessuno la' fuori aveva la nostra risposta.** Non esiste il progetto che fa quello che vogliamo
fare e che basta copiare. Lo dico subito perche' era la speranza implicita del giro.

Quello che ho trovato e' un'altra cosa, e vale di piu': **quattro strumenti che ci mancavano**, e —
soprattutto — **la prova che tre nostre idee erano sbagliate**, scoperta guardando dove gli altri
hanno gia' sbattuto.

---

## Preso e gia' in funzione: quattro cose

### 1. Controllare che il token si possa RIVENDERE
Esistono token progettati perche' tu entri e non esca. I bot seri lo verificano prima di comprare,
pagando un servizio esterno; noi lo ricaviamo dai nostri stessi dati, gratis.

**Quanto pesava:** **un pool su sei** e' uno da cui praticamente nessuno riesce a uscire. Li stavamo
contando come guadagni, perche' vedevamo il prezzo salire e registravamo la salita.

### 2. Misurare quanto costa davvero comprare, invece di indovinarlo
Il vecchio motore dava per scontato un costo del **15%** su ogni pool. Misurato sui nostri
912.628 scambi veri: **0,45%**.

Trentatre volte sbagliato — e in una strategia che campa su margini sottili, quel numero decide da
solo se qualcosa sembra funzionare o no.

### 3. Chi si infila davanti ai nostri ordini
C'e' chi compra un istante prima di te per farti pagare di piu' e rivende subito dopo. Misurato:
**circa uno scambio su cento**. Costo reale ma piccolo.

**L'avvertimento vale piu' del numero:** costoro scelgono gli ordini grossi. Se il nostro segnale
funzionasse, i nostri ordini sarebbero proprio quelli. L'uno per cento e' la media del mercato, non
sara' la nostra.

### 4. Il primo controllo dei nostri dati contro un metro ESTERNO
Questa e' la piu' importante delle quattro, e non e' uno strumento: e' una verifica.

Il dubbio serio era: *e se il nostro database sembrasse perfetto solo perche' ha perso proprio i
casi difficili?* Ho preso uno studio pubblico su **832.941 token** di un'altra chain, fatto da altri,
e ho confrontato la quota di token che muoiono entro un giorno:

| | token morti entro 24 ore |
|---|---|
| **i nostri dati** | **68,2%** |
| **lo studio esterno, 832.941 token** | **68,7%** |

**Mezzo punto di distanza.** E' la prima volta che i nostri numeri vengono misurati con un metro
nato completamente fuori da casa nostra.

---

## Provato e NON regge: tre idee nostre, morte con un numero

Questa e' la parte che vale di piu', anche se non sembra.

1. **Il lancio coordinato** (piu' indirizzi che comprano nello stesso primo blocco) — non predice
   niente.
2. **Seguire i portafogli vincenti** — misurato: non c'e'. Conferma, da una terza via, il verdetto
   di agosto sul copy-trading.
3. **Il «difetto nei prezzi»** che credevo di aver visto — non esisteva: era un difetto della mia
   misura.

Ognuna di queste avrebbe potuto mangiarsi una settimana. **Sono morte in poche ore perche' qualcun
altro ci aveva gia' sbattuto e lo aveva scritto.**

---

## Buttato: tre cose che vanno di moda e non ci servono

- **Il dibattito fra agenti AI** (il progetto TradingAgents, quello che mi avevi mandato): tanti
  modelli che discutono fra loro. Costoso, lento, e non aggiunge niente a una decisione che si puo'
  misurare con un numero.
- **Le librerie per calcolare i costi**: danno formule esatte alimentate da dati che non abbiamo.
  Precisione finta.
- **Tutto quello che e' specifico di Solana**: chiusa ad agosto, non si riapre.

---

## Cosa resta da provare

Due idee buone che non ho ancora verificato sui nostri dati: **quanto sono concentrati i primi dieci
detentori** di un token, e **chi ha il potere di emetterne altri o di bloccarti**. Entrambe si
possono ricavare da dati che gia' abbiamo.

---

## Il bilancio, secco

Il giro e' costato **zero euro**. Ha prodotto quattro strumenti in funzione, un controllo esterno
che il nostro database ha passato, e la morte rapida di tre idee sbagliate.

**Avevi ragione tu a insistere.** Lo scrivo perche' quando avevi detto *«li fuori su GitHub c'e'
qualcosa che ci puo' aiutare al 100%»*, io ero scettico.

Non ci ha dato la risposta. Ci ha dato la strumentazione per accorgerci che tre nostre risposte
erano sbagliate — che a questo punto del progetto vale di piu'.
