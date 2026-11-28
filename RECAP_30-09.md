# Recap del 30 settembre

## 1. La scoperta

Per quindici verdetti abbiamo misurato **un quinto dei pool** — e precisamente il quinto che perde.

L'insieme ufficiale giudicava **8.792 pool** su robinhood ed escludeva **34.359**. La categoria
grossa: 28.507 pool che smettono di essere scambiati prima delle due ore. La regola «compro a
+2h» sembrava una scelta di tempismo; era un filtro che teneva solo i sopravvissuti lenti.

E i sopravvissuti lenti sono quelli che hanno gia' pompato e stanno scendendo:

| robinhood | N | media | in pari |
|---|---|---|---|
| visti dalla regola delle 2 ore | 4.611 | −4,5% | 32% |
| **scartati dalla regola** | **10.336** | **+11,1%** | **65%** |

## 2. Il primo numero positivo del progetto

**$25 su ogni pool, al suo 5° scambio, liquidando entro una settimana.** Nessuna selezione.

| | robinhood | base |
|---|---|---|
| media (portafoglio in parti uguali) | **+19,4%** | +1,6% |
| mediana | +1,1% | +0,2% |
| togliendo l'1% migliore | +12,0% | −2,2% |
| pool | 20.789 | 14.007 |

**La forma:** il 90% dei pool perde il 4,5%; il 10% che raddoppia porta +23,5%. Non e' «trovare
quello giusto»: e' comprare piccolo su tutto e avere abbastanza posizioni.

**Perche' base non funziona:** identica sulle perdite, ma i vincitori sopra +100% sono il 3,0%
invece del 9,9%. Non perde di piu': **produce meno vincitori grossi.**

## 3. Sette tentativi di ucciderlo

| sospetto | esito |
|---|---|
| rientro dall'impatto di una vendita | escluso: il modello cerca slancio, non prezzi schiacciati |
| rimbalzo immediato | escluso: il guadagno regge su tutta la finestra |
| pochi fortunati | escluso: 2.062 pool sopra il raddoppio |
| troncamento al tetto del calcolo | escluso: solo 2 pool al tetto |
| sopravvivenza dei morti precoci | escluso: costano 8 punti e sono dentro la misura |
| il gas | misurato: netto +19,0%, e +11,4% anche nell'impennata di settembre |
| **il prezzo d'ingresso mediano** | **era un artefatto MIO**, che avevo festeggiato per mezz'ora |

Il settimo e' il piu' istruttivo: avevo introdotto il prezzo mediano *per uccidere* un possibile
artefatto, ha migliorato i numeri (+19,4% → +24,8%) e ho letto il miglioramento come conferma.
Era un artefatto nuovo, nella direzione che mi faceva piacere: alla nascita il prezzo sale a
scatti, quindi la mediana dei primi cinque sta SOTTO il prezzo che si paga davvero.

> **Una correzione che migliora il risultato va sospettata prima di essere celebrata.**

## 4. Il giudice che non posso corrompere

`agents/prova_avanti.py` conta ogni giorno i pool nati **dopo il 30/09**, e **non stampa il
rendimento** finche' non arriva a **5.000 per chain**. Poi scrive il verdetto una volta e non lo
ricalcola.

La soglia e' stata alzata da 1.500 a 5.000 **prima di vedere un solo esito**, dopo aver misurato
il ritmo (~2.000 pool giudicabili al giorno): alzare l'asta prima di guardare e' lecito,
abbassarla dopo no.

**Verdetto atteso: 10 ottobre 2026.** Nessun euro rischiato prima.

## 5. La macchina

| | ieri | oggi |
|---|---|---|
| giri falliti | decine al giorno | **0** |
| giri in coda | 16 | 2 |
| repository | 7,13 GB e in salita | **3,9 GB**, crescita fermata |
| corsie attive | 60 dichiarate, 16 vive | 40 dichiarate, ~25 vive |

**Il guasto delle email** aveva una causa sola: un file cresciuto oltre il limite GitHub di 100 MB
bloccava OGNI salvataggio, per tutti, per tre ore. Compresso: 5,6 MB, 175.845 righe intatte.

**Il repository cresceva di 6,2 GB al giorno** per una riga: il censimento riscriveva l'archivio
ordinandolo per numero di scambi — che cambia ogni giro — quindi rimescolava centomila righe.
Misurato: ordine stabile 0,1 MB, rimescolato 12,8 MB. **Centoventotto volte.**

**Trentatre' corsie non giravano dal 27 agosto** e nessuno se n'era accorto: una corsia che
fallisce manda una email, una che smette di esistere non manda niente.

## 6. Cosa ho imparato di me

Tre volte oggi ho costruito una spiegazione plausibile e l'ho raccontata come un fatto:
- «la compressione impedisce a git di fare le differenze» → falso (avrebbe portato a riscrivere
  quattordici file per il problema sbagliato);
- «il timbro in testa fa divergere il flusso» → falso, e stavo per lasciarlo scritto nel codice;
- «una cancellazione ha ucciso cinque corsie» → erano state spente a mano.

> **Spento non e' rotto. Un miglioramento parziale non e' una soluzione. Una spiegazione
> plausibile non e' una causa.**

E il filo che lega tutta la giornata, dati e macchina insieme:

> **Ogni correzione ha una dose, e la dose non si legge nel difetto: si misura dopo.**
