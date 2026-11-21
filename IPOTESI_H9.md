# H9 — la successione di pattern, col bersaglio giusto

*29 settembre 2026. Registrata PRIMA di misurare. È l'ipotesi che Nicolò aveva chiesto fin
dall'inizio: non un attributo, ma **la combinazione**.*

## Perché nasce adesso

Le ultime ipotesi guardavano **un attributo alla volta** — il ritmo (H6), la capienza (H7). Nicolò
aveva chiesto una **successione di pattern**: pressione, concentrazione, ritmi, portafogli, tempi,
tutti insieme. La macchina per farlo esiste da giorni (`agents/modello.py`, 33 caratteristiche) ma
stava allenando su un metro rotto.

Oggi le misure sono riparate: verso, finestra, criterio di scarto, taglia, e soprattutto la
**simulazione di vendere davvero** una posizione da 500 dollari.

## L'esplorazione già fatta, e va dichiarata

Col bersaglio *«fa +50%»* il modello **sa ordinare**: 0,723 sul futuro, decimo migliore 2,6 volte
sopra la media. Ma i rendimenti erano **invertiti**: il gruppo migliore perdeva di più (−64,8%
contro −40,1%). Stava trovando i pool **volatili**, non quelli redditizi.

Il bersaglio era sbagliato: «fa +50% qualche volta» e «rende» non sono la stessa cosa.

## La regola, congelata

Chain **robinhood**. Caratteristiche: tutte quelle note **al momento della decisione**.
**Bersaglio: il rendimento incassabile** (`_uscita_500`, cioè simulando di vendere 500 dollari nel
flusso vero), non una soglia.
Addestramento sui primi **70% per tempo**; giudizio sull'ultimo 30%, **mai visto**.
Si valuta il **decimo migliore** secondo il modello.

## Le condizioni di morte, scritte adesso

Sul blocco mai visto, il decimo migliore deve:

1. avere un rendimento medio **sopra quello di tutti** di almeno **15 punti**;
2. avere la media **tolto l'1% più alto** sopra **−15%** (cioè non reggersi su due fortunati);
3. essere **monotono**: i decili peggiori non devono rendere più dei migliori.

**Se una sola fallisce, H9 è morta**, e non si cambia bersaglio né soglia per salvarla.

## La trappola che mi aspetto

Che il modello trovi di nuovo la **volatilità** travestita: pool che ogni tanto esplodono e di
solito muoiono. Con il rendimento come bersaglio dovrebbe essere impossibile — ma è esattamente
quello che pensavo del metro pesato, e mi sbagliavo. Se il decimo migliore ha media alta e mediana
pessima, è quello, e va detto.

## Cosa NON dimostrerebbe, anche se vivesse

Che si possono fare soldi. Resta il muro misurato ieri: con 500 dollari esce il 77% della posizione.
Una sequenza che vince deve trovare pool **sia redditizi sia capienti** — e il rendimento su cui è
allenata li tiene già dentro tutti e due, perché simula l'uscita vera.
