# RECOVERY — whale-radar

*Aggiornato la notte del 26 settembre 2026, 02:00. Sostituisce la versione di agosto, che
descriveva un sistema e dei numeri che non esistono più.*

## Cosa stiamo facendo, in una frase

Cerchiamo un vantaggio misurabile nel comprare memecoin appena nati su due chain EVM
(**robinhood**, **base**), su dati raccolti gratis, senza mai rischiare un euro — e ogni volta che
una strategia muore, ripariamo anche lo strumento che l'aveva fatta sembrare viva.

## Lo stato vero, oggi

**Otto strategie provate, otto morte, zero euro rischiati.** Il 25–26 settembre abbiamo scoperto che
**quattro misure su cui decidevamo erano rotte**, e le abbiamo riparate tutte:

| difetto | cosa faceva | dove è riparato |
|---|---|---|
| finestra di osservazione | misurava esiti a 24h su dati di 6h | `insieme.py` |
| criterio di scarto | scartava i pool morti, cioè le trappole | `insieme.py`, `cercatore.py` |
| **verso dei prezzi** | contava gli **acquisti come vendite** nel 73% dei pool | `verso.py` (nuovo) |
| taglia mai misurata | un 10x che scambia 32 $ sembrava un'uscita | `insieme.py` |

**Il quadro corretto (robinhood):** pool da cui non si esce mai **17,1%**, fondale **−9,5%**, miglior
condizione gratuita fuori campione **−2,9%**. Monotona e pulita, mai sopra zero. Base resta muta
(media +1,8% che tolto l'1% alto diventa −0,3%).

## Gli ultimi cinque passi

1. corretto il verso dei prezzi e sospeso i due verdetti che ne dipendevano;
2. separato il **decreto** («meno di 5 vendite = −98%») dalla **misura**: era il 95% del risultato;
3. registrato H6 e H6b con la condizione di morte scritta prima, e **uccise entrambe** in quattro ore
   (`VERDETTO_H6.md`);
4. scoperto che i pool con volume alto rendono +24,9% — e che è **volume misurato dopo l'entrata**,
   cioè guardare il futuro. Rifatto con ciò che si sa prima: negativo in ogni fascia;
5. la raccolta ora tiene `sq` (prezzo del pool) e `liq` (**profondità**) dai log V3/V4 — li
   decodificavamo e li buttavamo da un mese. Indici verificati sulla catena, scarto 0,05–1%.

## Il prossimo passo, che aspetta una decisione

Tutte le domande su *questa* direzione sono chiuse con strumenti di cui ci si può fidare.
La scelta su dove guardare adesso è di Nicolò. Le tre strade sull'ordine del giorno:

- **uscita a orologio** invece che sulla mediana delle stampe, ora possibile grazie a `sq`
  (è il suggerimento di Grok del 25/09: «la mappa che dice se un orizzonte qualunque ha il centro
  sopra zero»);
- **profondità come filtro** con `liq`, che finalmente misura quanto un pool può contenere;
- **un'altra direzione** del tutto — le prime due restano dentro «comprare memecoin nuovi da taker».

**Quanto costa aspettare, misurato il 26/09 alle 04:15.** La profondità esiste solo sui pool nati
dopo stanotte, quindi le strade 1 e 2 vanno alimentate dal nuovo. Robinhood fa **385 pool al
giorno**: 300 pool con profondità in **meno di un giorno**, 1.000 in **2,6 giorni**. Base ne fa 129:
2,3 e 7,8 giorni. Rileggere lo storico non serve — **si aspetta un giorno, non una settimana.**

## Le corsie che girano da sole

13 corsie con riarmo automatico. La nuova è **`insieme.yml`**: ricostruisce l'insieme di analisi
ogni ~27 minuti nel cloud. Prima lo costruivo a mano sul Mac ed è andato perso con una pulizia del
disco: era il terzo file importante perso così.

## Come si riprende

Copia di lavoro: clone leggero con `--depth 1 --filter=blob:none` e sparse-checkout su
`agents .github data/loop1` (l'intero repo riempie il disco). Si pubblica **solo** con
`./pubblica.sh "messaggio"`, che si rifiuta di spingere se qualcosa non compila.
Revisori: Astra (max 3/giorno, a pagamento) e Grok (illimitato, dall'abbonamento, **mai via API**).
