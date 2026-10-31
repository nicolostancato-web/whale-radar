# La persistenza, passata al test piu' stretto: una chain, trenta portafogli, intervalli che si sfiorano

*5 ottobre 2026 · le tre obiezioni di Astra, affrontate tutte e tre in un test solo*

## Il test, e perche' chiude le tre obiezioni insieme

Astra aveva detto che «due meta' disgiunte non garantiscono un vero esperimento temporale», con
tre domande: *quando* sarebbe stata disponibile la selezione? Le posizioni della seconda meta'
erano **gia' aperte**? Gli stessi gettoni compaiono in **entrambe**?

Una data unica **T** le chiude tutte e tre:

- si seleziona usando **solo posizioni CHIUSE prima di T** — un multiplo si conosce solo alla
  chiusura, quindi a T quell'informazione esisteva davvero;
- si misura **solo su posizioni APERTE dopo T** — nessuna era in corso quando si e' scelto;
- si **escludono i gettoni gia' visti prima di T** — non si rimisura lo stesso affare.

Piu' il costo minimo di 10$ per posizione (vedi `COSTO_QUASI_ZERO.md`).

## Come ho scelto T, e il primo tentativo fallito

Primo criterio: **meta' del periodo coperto**. Ha dato **0 portafogli su base e 3 su robinhood**:
l'attivita' e' concentrata nel tempo, quindi tagliare il calendario a meta' non divide
l'attivita' delle persone.

Secondo criterio, dichiarato prima di guardare gli esiti: **la data in cui meta' delle posizioni
risulta chiusa**. Dipende dal volume dei dati, non dai risultati. Scegliere T per massimizzare i
portafogli utilizzabili sarebbe stato scegliere sui dati, ed e' il modo in cui si trova sempre
qualcosa cercando.

## Il risultato

| | portafogli | prima di T | **dopo T** | >=2X nel dopo (al 95%) |
|---|---|---|---|---|
| **base** | **4 contro 4** | — | — | **non giudicabile** |
| robinhood, bravi a T | 30 | 3,64X | **3,68X** | 93,3% (**80,5–98,8%**) |
| robinhood, scarsi a T | 10 | 1,38X | **2,02X** | 50,0% (**22,2–77,8%**) |

**Su base il test non si puo' fare**: 154 portafogli su 183 non hanno tre posizioni chiuse prima
di T. Non e' un verdetto negativo, e' assenza di materiale — e va detto cosi'.

**Su robinhood regge, ma piu' debole di come l'avevo riferito:**

- il divario scende da **3,48 contro 1,07** a **3,68 contro 2,02**;
- gli intervalli **si sfiorano**: 80,5% contro 77,8%, separati di due punti e mezzo;
- e i **mediocri sono migliorati da soli**, da 1,38X a 2,02X. Quindi una parte del 3,68X dei
  bravi **e' il periodo, non la bravura** — e questa e' la cosa che il test precedente non
  poteva vedere, perche' mancava un gruppo di controllo contemporaneo.

## Dove si e' fermata l'affermazione

Partita ieri sera come **«la bravura persiste fuori campione, su due chain»**. Dopo tre attacchi
— il costo quasi-zero, gli intervalli di conteggio, la data unica — resta:

> **su una chain, su trenta portafogli, con intervalli separati di due punti e mezzo, e con una
> parte del divario attribuibile al periodo.**

Non e' niente, ed e' molto meno di quello che avevo detto. Nessuna delle tre riduzioni viene da
un ripensamento: tutte e tre vengono da uno strumento o da una domanda che ieri non avevo.

## Cosa serve perche' diventi un risultato

Piu' date di selezione, non una: la stessa regola applicata a T multipli, con il gruppo di
controllo contemporaneo misurato ogni volta. Se il divario sopravvive a dieci date diverse non
e' il periodo. E su base serve copertura: 154 portafogli esclusi per mancanza di posizioni
chiuse sono un problema di dati, non un verdetto.
