# Il giro su GitHub delegato a Grok — 24 settembre 2026

*Primo giro con il secondo revisore. Costo: ZERO (abbonamento, nessuna chiave API).*

## Perche' delegarlo

Il giro su GitHub era fermo dal 23/09 alle 11:27: l'avevo lasciato indietro io, assorbito dal
lavoro sulle misure. Delegandolo a Grok i due lavori smettono di competere — lui cerca la' fuori
mentre io scavo nei dati.

## LA COSA PIU' IMPORTANTE: il muro dell'83% e' caduto

Ieri avevo scritto che l'83% dei pool di robinhood sono Uniswap V4, non hanno indirizzo proprio e
**non espongono le riserve**. Vero per la strada che stavo usando (l'evento `Sync`), falso in
generale.

**Esiste un contratto apposta, `StateView`**, che dato l'identificativo del pool restituisce prezzo
e liquidita', anche su un blocco passato. Indirizzo su base: `0xA3c0c9b65baD0b08107Aa264b0f3dB444b867A71`.

**Verificato sui nostri dati, non solo letto:**

```
0xb7af3f156e4f…  prezzo 1,939e+06  liquidita 162.563.243.159.620.115.441
0xbff46f249d61…  prezzo 1,123e+07  liquidita 0          <- pool vuoto
```

Per arrivarci serviva il codice a 4 byte con cui si chiama la funzione, che si calcola con keccak —
non installabile sul cloud. Scritto in Python puro: `agents/keccak.py`, 60 righe, verificato contro
il selettore noto di `getSlot0` (`0xc815641c`, coincide esattamente).

**Ed e' la QUINTA volta in tre giorni** che un «non si puo' avere» si rivela un «non l'ho ancora
provato». La lezione di `LEZIONE_IMPOSSIBILE.md` continua a presentare il conto.

## Le due cose che non sapevamo di non sapere

**1. Su V4 un pool puo' bloccare l'uscita anche avendo scambi veri da molti portafogli.**
Esiste un componente aggiuntivo (l'hook) i cui permessi stanno nei bit bassi del suo indirizzo,
leggibili dall'evento `Initialize`. `beforeSwap` puo' far fallire una sola direzione;
`afterSwapReturnDelta` puo' trattenere l'output. **Il nostro controllo di vendibilita' non vede
questa famiglia di trappole**: vede solo chi non ha mai venduto.

**2. Chi toglie la liquidita' non fa uno scambio.**
Su V4 la fuga con la cassa passa dall'evento `ModifyLiquidity` con delta negativo. Non lo
raccogliamo, quindi e' invisibile. E la liquidita' scritta nell'ultimo `Swap` diventa falsa appena
qualcuno ritira senza scambiare.

## Il wash trading a piu' portafogli

Il nostro 26% di trappole cattura solo l'auto-scambio (un wallet che compra e nessuno vende).
Esistono il giro fra due indirizzi e i volumi che si corrispondono nel tempo (Victor e Weintraud,
The Web Conference 2021). **Se nel campione «pulito» sono rimaste coppie finanziate dallo stesso
indirizzo, il guadagno finto si e' solo spostato.**

## Studi con numeri, da provare

- **Marino, Naviglio, Tarantelli, Lillo, «Predicting the success of new crypto-tokens»**
  (arXiv:2602.14860): 655.770 token, 4.338 graduati (0,63%). Il predittore forte non e' il numero
  di scambi: **a parita' di capitale entrato, chi ci arriva con pochi scambi grandi ha probabilita'
  molto piu' alta di chi ci arriva con centinaia di scambi piccoli.** E' un rapporto, non una
  soglia sui conteggi — quindi non e' la famiglia che abbiamo gia' scartato.
- **MELT** (arXiv:2602.13480): 41.000 lanci, 122 variabili pre-migrazione. Il **finanziatore comune**
  dei wallet: al momento della migrazione il 36,5% della supply e' in account coordinati.
- **Cernera et al., USENIX Security 2023**: la **recidiva del deployer** (quanti token ha gia'
  creato, e se ha ritirato la liquidita'). L'1% degli indirizzi crea il 20-25% dei token.

## Metodologia anti-illusione (ci serve dopo le tre giornate di miraggi)

- **Deflated Sharpe Ratio** (Bailey, Lopez de Prado, 2014): confronta lo Sharpe osservato col massimo
  atteso fra N strategie SENZA vantaggio. **N deve includere ogni configurazione provata**, comprese
  le famiglie gia' scartate — altrimenti la correzione non morde.
- **Purged cross-validation ed embargo** (*Advances in Financial ML*, cap. 7 e 12): la finestra di
  purge e' l'orizzonte dell'etichetta, non un numero a piacere.
- **Harvey, Liu, Zhu (2016)**: con centinaia di fattori provati, la soglia ragionevole su un t-stat
  nuovo e' **3**, non 2.
- Codice: `skfolio/skfolio` (`CombinatorialPurgedCV`), mantenuto.

## L'avvertimento di Grok, che vale da solo il giro

> *Non ho trovato niente di solido, specifico per memecoin EVM appena nati su V4, che preveda il
> rendimento eseguibile dai primi minuti con un numero che sopravviva a una correzione per tentativi
> multipli. Chi pubblica accuracy sopra 0,99 su questo mercato sta misurando la base rate.*

## L'ordine di lavoro che ne esce

1. **Leggere i permessi dell'hook e indicizzare `ModifyLiquidity`** — prima di qualunque modello.
   Sull'83% dei pool il blocco dell'uscita e il ritiro della liquidita' **non stanno negli swap**, e
   senza quelli l'etichetta «si poteva uscire» e' falsa proprio dove si concentrano i guadagni finti.
2. **Simulare la vendita** invece di dedurla: il nostro flag vede solo chi non ha mai venduto, non
   chi vende e riceve una frazione, o chi trova la tassa accesa dopo.
3. **Solo dopo**, una variabile nuova sotto Deflated Sharpe. *«Uno Sharpe corretto su un'etichetta
   sporca e' un numero pulito su un risultato sbagliato.»*

---

# X come strumento di scoperta — 24/09 pomeriggio

*Idea di Nicolo: usare Grok non solo su GitHub ma su X, dove la gente discute strategie, articoli e
mette i link ai repository. **Non** per leggere «cosa sta per esplodere».*

Ha funzionato meglio di GitHub, e ha trovato una trappola che ci riguarda **direttamente**.

## Il caso OLEAF (23/09, sulla NOSTRA chain) — la trappola a due pool

Un token con il contratto pulito: nessuna blacklist, proprieta' rinunciata, tutti gli scanner verdi,
acquisto regolare. Ma:

- la pool **dominante** WETH/OLEAF ha un hook con `beforeSwap`: **la vendita fallisce** se non
  arriva da un router autorizzato;
- esiste una **seconda pool piccola, senza hook**, sulla stessa coppia;
- gli scanner provano a vendere **di la'**, la vendita passa, e il token risulta vendibile.

**La liquidita' vera e' nella pool da cui non si esce.**

Indirizzi pubblicati: token `0xEB0cB580D8cD0f2848293C0d5DdaA0083f6924CD`,
hook `0xa3e60c5803c02e424dfe5f41da31430bfe6bca80`,
router `0xc955efd62944fcea581194ba722db08592865b8b`.

**Perche' ci colpisce in pieno.** Il nostro controllo di vendibilita' chiede «ci sono state vendite
riuscite?». Su un token cosi' la risposta e' **si'** — solo nella pool sbagliata. E' costruito
esattamente contro il metodo che usiamo.

## Il buco che ha rivelato nei nostri dati

Per accorgersene serve sapere **quali due token** scambia ogni pool. Nei nostri scambi c'e' tutto —
chi, quanto, quando, in che blocco — **tranne la coppia**.

**Sesta volta in quattro giorni** che un buco nei dati si scopre solo provando a usarli. E ogni
volta l'ha rivelato una fonte esterna: prima Astra, poi Grok su GitHub, adesso un post su X.

Risolto senza raccolta nuova: la coppia sta **nello stesso evento** da cui gia' leggevamo l'hook
(`currency0` e `currency1` sono indicizzati, quindi nei topic). Una chiamata, due informazioni.

## Il contorno, che conferma il meccanismo

Il 15 settembre Uniswap, 0x e Paradigm hanno discusso pubblicamente di hook malevoli con transazioni
alla mano: un hook che estrae il 4,8% di una gamba dello swap, e l'osservazione che **la simulazione
non basta, perche' l'hook riconosce di essere simulato**. Hayden Adams (Uniswap) non contesta che
gli hook malevoli esistano: contesta chi debba filtrarli.

## Cosa NON c'era su X, e va detto

- **Nessun bot con numeri veri.** Le percentuali pubblicate sono lanci di prodotto: dove c'e' una
  percentuale non c'e' un campione etichettato ne' i falsi positivi. Un post dichiara «1.292
  honeypot su 9.172 scan, accuratezza 99,9%» — 1.292/9.172 e' una quota di segnalazioni (14%), non
  un'accuratezza.
- **Nessuno ha misurato che il long su memecoin nuove abbia valore atteso negativo.** I post «il 99%
  va a zero» non hanno campione, orizzonte ne' regola d'ingresso.

Parole di Grok: *«la tua misura (9.600 pool, 35% trappole, pool sani +0,8% netto) e' piu' rigorosa
di qualunque cosa abbia trovato su X.»*

## La regola operativa che ne esce

X serve per **scoprire meccanismi e trovare link**, non per leggere previsioni. Le tre fonti che
finora ci hanno spostato davvero sono: studi con i numeri, codice che risolve un problema tecnico
preciso, e i due revisori. I post valgono quando descrivono **come funziona una trappola**, non
quando dicono cosa comprare.
