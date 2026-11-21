# Verdetto sulle combinazioni incrociate — il metodo funziona, il vantaggio non c'e'

**Notte fra il 30/09 e l'1/10. Primo uso del motore chiesto da Nicolo' il 23/09.**

## Cosa e' stato fatto

10.700 combinazioni di 1-3 condizioni incrociate, su attributi noti **prima** di comprare.
Tre pezzi di tempo: si cerca sul 45%, si scegli sul 27%, si giudica sul 28% **mai toccato**.
Controllo sul rumore: la stessa ricerca su esiti mescolati, cinque volte.
E l'esito misurato col **prezzo ottenibile**, non con quello osservato.

## Esito, in una tabella

| configurazione | le dieci migliori sul pezzo mai visto | fondale | verdetto |
|---|---|---|---|
| robinhood, latenza 1 scambio | **+14,3%** | −11,1% | +25 punti — segnale |
| robinhood, latenza 2 scambi | non batte il rumore | — | niente |
| robinhood, latenza 3 scambi | −14,0% | −8,5% | niente |
| base, latenza 1 scambio | −17,1% | −21,4% | +4 punti — niente |

**Un caso positivo su quattro.** E' quello che il caso produce da solo: la regola che ci siamo
dati — serve su tutte e due le chain, e deve reggere alle variazioni — dice **rumore**.

## Le tre cose che il motore ha fatto BENE, e che valgono piu' del verdetto

**1. Ha preso il sovra-adattamento in flagrante.** Nel primo giro la combinazione migliore
faceva **+116,8%** sul pezzo di scelta e batteva il rumore. Sul terzo pezzo: **−26,4%**, peggio
del fondale. Senza il terzo pezzo avrei portato un'altra illusione.

**2. Ha cambiato natura quando la misura e' diventata onesta.** Con il prezzo osservato trovava
lanci a raffica — sei portafogli in sessanta secondi, +207%, irraggiungibili. Con il prezzo
ottenibile ha smesso di cercarli e ha trovato **pool lenti** (nove minuti fra scambi, oltre due
ore di vita): raggiungibili. Il motore ha seguito la misura, non l'entusiasmo.

**3. Le dieci migliori invece della prima.** Con 10.700 tentativi, la migliore e' anche la piu'
fortunata. Guardare le dieci mostra la dispersione — e li' si e' visto che le tre che
fallivano avevano tutte lo stesso ingrediente (`gap_mediano>535`), cosa invisibile guardando
una sola.

## Il nucleo che resta da guardare

Tutte le dieci migliori su robinhood contenevano **momento**: `rendimento_finora > 23%` o
`massimo_finora > 27%`. Il pool e' gia' salito prima che io entri.

Non basta a fare una strategia — l'ho appena misurato — ma e' l'unico ingrediente che ricorre
in ogni configurazione, comprese quelle fallite. Se c'e' qualcosa in questo mercato, e' da
qualche parte dentro il momento, e non l'abbiamo ancora isolato bene.

## Il vincolo che governa tutto, e che ora e' scritto nel codice

> **Il prezzo che vedi non e' il prezzo che paghi.** Paghi quello dello scambio dopo, e su un
> mercato veloce e' il 38% in piu' in mediana.

Questo ha ucciso, nella stessa notte: il +17,6% del recap di ieri, il +193,8% della prima
combinazione, e ogni numero costruito sul prezzo osservato. E' una decisione protetta da un
controllo (`agents/decisioni.py`), quindi non si puo' dimenticare come si e' dimenticato tutto
il resto.
