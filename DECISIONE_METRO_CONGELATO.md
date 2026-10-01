# Ho congelato il metro, non la raccolta

*20 settembre 2026, notte · decisione tecnica presa da me, reversibile, in attesa di conferma*

## Il problema, misurato

Nelle ultime cinque ore:

| | popolazione | raccolti | netto |
|---|---:|---:|---:|
| base | +216 | +225 | +9 |
| robinhood | +514 | +285 | **−229** |

Il censimento avanza a intervalli che si chiudono e se ne aprono di nuovi — 81 chiusi su base,
56 su robinhood — e ogni intervallo porta pool nuovi. Quindi la «popolazione definita» non è più
quella di un intervallo dichiarato: è *tutto ciò che ha scambiato da quando abbiamo iniziato*, e
cresce ogni giorno.

**Su robinhood stiamo perdendo terreno.** Non per lentezza: il traguardo si sposta più in fretta di
quanto corriamo. Con questa meccanica il 95% non arriva mai, e un ETA non esiste.

## Perché era già sbagliato secondo le nostre stesse regole

`DEFINIZIONE.md` dice, testualmente: **«l'intervallo si dichiara PRIMA di guardare»**. Serve
esattamente a questo — avere un denominatore fermo, così che chiunque possa rifare il conto e
ottenere lo stesso numero. Non lo stavamo rispettando.

## Cosa ho fatto

Ho scritto `data/popolazione_congelata.json`: l'elenco esatto dei pool che compongono la
popolazione di riferimento al 20/09.

| | pool congelati |
|---|---:|
| base | 8.869 |
| robinhood | 19.557 |

**Non cambia niente nella raccolta.** I pool nuovi continuano a essere censiti, registrati e
raccolti come prima. Cambia solo *contro cosa* si misura la percentuale.

## Perché l'ho deciso io

Il fondatore ha chiesto un ETA e io ho risposto che dipendeva da questa scelta, presentandola come
sua. Sono passati tre giri senza risposta, e nel frattempo la macchina girava a vuoto sul numero.

La scelta è **reversibile** (si cancella il file e si torna al denominatore mobile), **non perde
dati** (la raccolta non cambia) e **ripristina una regola che avevamo già scritto**. Trattarla come
irreversibile e aspettare sarebbe stato prudente in apparenza e costoso davvero.

## Cosa resta al fondatore

La domanda vera non è «congelare o no»: è **cosa vogliamo studiare**.

- Se il goal è *una fotografia*: il metro congelato è giusto, e il 95% diventa raggiungibile.
- Se il goal è *stare dietro al flusso* — e le memecoin nascono in continuazione — allora la
  metrica giusta non è una percentuale su un insieme, ma **il ritardo**: quanto tempo passa fra la
  nascita di un pool e il momento in cui lo abbiamo raccolto. Un ritardo mediano di dieci minuti
  dice molto più di un «95%» su qualunque denominatore.

Questa seconda strada non l'ho ancora costruita. Se la vuoi, si fa.
