# H7 — «la capienza», registrata PRIMA di guardare i dati

*26 settembre 2026, sera. Scritta mentre i pool con profondità sono 168: troppo pochi per
concludere, abbastanza per essere tentato di sbirciare. Per questo si scrive adesso.*

## Perché si registra prima

Stanotte H6b sembrava viva: +11% fuori campione, positiva anche tolta la coda, intervallo tutto
sopra zero. È morta quando ho misurato **quanti soldi passavano davvero** a quei prezzi: trentadue
dollari in mediana. Il guadagno c'era solo se vendevi dentro trentadue dollari di domanda.

Da quella morte è nata la misura nuova — `liq`, quanto il pool può assorbire — che **non avevamo
mai avuto** perché la buttavamo al momento della raccolta. Ora ce l'abbiamo, e si accumula.

**Il rischio adesso è l'opposto di stanotte.** Non più «un numero che sembra buono», ma
«guardo venti tagli finché uno non funziona». Con centosessantotto casi qualcosa che funziona lo
trovo di sicuro, e non vorrà dire niente. Quindi la prova si scrive **ora**, e non si tocca più.

## La domanda, una sola

**La capienza del pool, misurata PRIMA di comprare, predice l'esito?**

Non «esiste un taglio della capienza che rende». Quella è una domanda a cui i dati dicono sempre sì.

## La regola, per intero e congelata

Chain **robinhood**. Solo pool **giudicabili** (nati almeno 24h prima della fine della raccolta) e
con **`_liq_copertura > 0,9`**, cioè la profondità osservata su quasi tutti gli scambi prima della
decisione. Entrata 2h dopo il primo scambio, costo 1,8%. Uscita al prezzo mediano delle vendite
vere entro 24h; **nessuna vendita = −98%**.

La capienza è `_liq_prima`, **mediana** della profondità negli scambi prima della decisione.
Si divide il campione in **tre terzi per capienza**: bassa, media, alta. Tagli fissati sui
**terzili del campione stesso**, non scelti a mano.

## Quando si guarda

**Mai prima di 600 pool** che rispettano i requisiti. Oggi sono 168. Al ritmo attuale
(~150 al giorno) si arriva fra tre o quattro giorni.

Se guardo prima, il risultato non vale — e lo scrivo qui perché fra tre giorni me lo sarò
dimenticato.

## Cosa dichiaro viva, cosa dichiaro morta

H7 è **viva** solo se, sul terzo più capiente:

1. la quota di pool **senza alcuna uscita** è almeno **8 punti** sotto quella del terzo meno
   capiente (oggi il fondale generale è 17,1%);
2. la media **tolto l'1% più alto** è sopra **−2%** (stanotte la migliore regola stava a −3,7%);
3. la relazione è **monotona**: terzo basso ≤ medio ≤ alto su entrambe le misure. Un salto solo
   nell'estremo è un artefatto, non un meccanismo.

**Se anche una sola fallisce, H7 è morta.** Non si sposta la soglia, non si prova «i quartili
invece dei terzi», non si aggiunge un filtro per salvarla. È così che sono morte le sei prima di lei.

## La trappola che mi aspetto

Che la capienza predica **la sopravvivenza ma non il guadagno** — cioè che i pool grossi muoiano
meno e rendano uguale. Sarebbe comunque utile (togliere il 17% di perdite totali vale molto), ma
**non sarebbe un vantaggio**, e va detto con quelle parole invece di venderlo come una vittoria.

L'altra trappola, quella vera: che il terzo più capiente renda di più **perché ci sono dentro i
token che sono esplosi**, e la capienza l'abbiano guadagnata esplodendo. La misura è presa PRIMA
della decisione, quindi non può succedere — ma è esattamente l'errore che ho commesso stamattina
con il volume misurato dopo l'entrata, e lo scrivo per non ripeterlo.
