# 📥 PIANO DI ACCUMULO — cosa raccogliere, e in che ordine

*14/09/2026 · conseguenza di DATABASE_AUDIT_FINAL.md · bozza in attesa della revisione avversariale*

## Il criterio di priorità

Non «cosa sarebbe interessante», ma:

> **Cosa, se non lo catturiamo adesso, sarà impossibile ricostruire fra un mese?**

Raccogliere domani ciò che si può raccogliere anche fra un mese ha priorità **bassa**. Raccogliere
oggi ciò che evapora ha priorità **assoluta**.

---

## MUST HAVE — evapora, e senza non si risponde a niente

### M1. I primi scambi dei token appena nati

| | |
|---|---|
| **cosa** | ogni scambio delle prime ore di vita: istante, compratore/venditore, importo, wallet |
| **perché** | è l'unica sede possibile del segnale secondo l'audit: **chi** compra, in che ordine, con che tempi |
| **fonte** | GeckoTerminal `/pools/{addr}/trades` (gratis) |
| **evapora?** | **SÌ**: la fonte conserva solo gli ultimi ~300 scambi. Per un token maturo i primi non esistono più |
| **chiave** | indirizzo pool + `tx` |
| **timbro** | `acq` (aggiunto oggi) |
| **frequenza** | i pool nati da meno di 8h vanno interrogati **a ogni giro** |
| **stato** | 🟡 parziale: la priorità ai pool già valutabili è stata messa oggi, ma la copertura resta bassa |

### M2. I token che muoiono in fretta

| | |
|---|---|
| **cosa** | serie di prezzo e scambi anche dei pool che vivono meno di 3 ore |
| **perché** | oggi le serie escluse vivono **1 ora** in mediana e le ammesse **23**: ogni rendimento che calcoliamo è condizionato alla sopravvivenza. Senza i morti, tutti i numeri sono ottimisti di una quantità ignota |
| **evapora?** | **SÌ**: un pool morto sparisce dagli elenchi della fonte |
| **ostacolo noto** | `pulse.py` raccoglie solo sopra **$5.000** di liquidità, e `MIN_CANDLES=5` esclude chi non arriva a 5 candele |
| **stato** | 🔴 **non raccolto**. È il buco più grave dopo l'embargo |

### M3. Il timbro di acquisizione

| | |
|---|---|
| **cosa** | `acq` = quando il dato è entrato da noi, dentro ogni record |
| **perché** | senza, la domanda «ce l'avevamo al momento della decisione?» non ha risposta — e ricostruirla da git è impossibile da quando il GC ha schiacciato la storia |
| **stato** | 🟢 **fatto oggi** su scambi, battito e candele |

### M4. La liquidità al momento della decisione

| | |
|---|---|
| **cosa** | riserva del pool campionata nel tempo, **senza soglia minima** |
| **perché** | la liquidità non è **mai** una feature oggi, ed è la variabile che decide quanto costa uscire. Sotto $5.000 non la raccogliamo proprio — cioè esattamente dove il costo esplode |
| **evapora?** | **SÌ**: è uno stato istantaneo, non ricostruibile a posteriori |
| **stato** | 🔴 raccolta solo sopra $5.000 |

---

## SHOULD HAVE — non evapora subito, ma serve

### S1. Preventivi di vendita eseguibili
Il costo d'uscita misurato **al momento**, non in calma: è il consiglio esterno del 4 settembre, mai
eseguito. Oggi abbiamo 815 misure Solana e 376 on-chain EVM, tutte «in calma».

### S2. Identità dei wallet nel tempo
`wallet_scores.json` esiste (9.743 wallet) ma **non è letto da nessun modello**, e soprattutto non è
point-in-time: usarlo così com'è sarebbe fuga di informazione, non miglioramento.

---

## NICE TO HAVE

Segnali sociali, dati degli holder, grafo di finanziamento fra wallet. Tutti richiedono fonti nuove:
**non si toccano** finché i MUST non sono verdi.

---

## NON NECESSARIO

Allargare le chain. Aumentare il numero di pool scoperti (ne scopriamo già 15-20mila e ne
analizziamo il 3-11%: il collo di bottiglia **non è la scoperta**).

---

## Come sapremo che basta

Il database si può dichiarare **GIALLO** quando:

1. una chain ha ≥400 righe con scambi **veri** prima dell'entrata (non il valore di ripiego);
2. l'embargo è coerente con il momento d'entrata — la finestra è **positiva**;
3. i token morti entro 3h **entrano** nel campione con il loro esito;
4. `acq` è presente su tutti i record nuovi e la distribuzione `acq − ts` è misurabile.

**VERDE** quando in più il costo d'uscita è misurato al momento dello stop, non in calma.

> Finché non siamo almeno gialli, ogni ora spesa a ottimizzare strategie produce numeri che non
> significano quello che sembrano significare — e ne abbiamo già la prova.
