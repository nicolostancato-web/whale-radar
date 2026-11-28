# I gettoni tornano — 6 ottobre 2026, 14:00

## La prova, in una tabella

Su 66 posizioni confrontabili di portafogli nostri:

| misura | solo col pool | **con la curva** |
|---|---|---|
| gettoni venduti / gettoni comprati (mediana) | 1,50 | **0,98** |
| casi impossibili (vende e non ha mai comprato) | **43** | **0** |
| posizioni che quadrano entro il 5% | — | **35 su 66 (53%)** |

**Tutti e 43 i casi impossibili hanno trovato la loro provenienza.** L'anomalia che ci ha tenuti
fermi tre giorni — «vendono gettoni che non hanno mai comprato» — non era un difetto del nostro
conto: era un mercato che non leggevamo.

## Perché questa misura e non un multiplo in euro

Per dire «ha guadagnato X» serve un **prezzo**, e un prezzo sbagliato ha già prodotto due disastri
qui: un valore di 16 milioni inesistente il 3 ottobre, e stamattina una somma di importi in 72
valute diverse che stavo per scrivere in euro.

Questa misura non ne ha bisogno. Chiede solo: **i pezzi venduti erano stati comprati?** È un
conteggio, non una valutazione. Se i pezzi non tornano, qualunque multiplo è finto. Se tornano, il
multiplo si calcola dopo, con calma e con le unità giuste.

In più: i memecoin hanno sempre 18 decimali, quindi **questa misura non è stata toccata**
dall'errore sulle valute. Il lato gettoni era giusto anche quando il lato denaro era sbagliato.

## Il caso che si verifica a mano

Portafoglio `0x59d173dd7606d1d172c186e9edf59e83a39e013f`, moneta
`0x2ad522452ea0a85774a6c6a8ae0e9f4fec3b2ce1`:

| cosa | quando | prova |
|---|---|---|
| compra sulla curva: paga 0,05 (valuta nativa), riceve **3.007.275** gettoni | 25 ago 2026, 23:26 UTC, blocco 46.121.624 | `0xe29021e1…05bc1b` |
| vende nel pool: **3.007.275** gettoni, la stessa quantità esatta | 13 secondi dopo, blocco 46.121.748 | `0xa9d98d10…2edca44` |

Verificato sulla chain: entrambe esistono, entrambe riuscite, **entrambe firmate dal portafoglio
stesso** (non da un router). Rapporto venduti/comprati: **1,0000**.

### E questo spiega il controllo che era fallito

Il 5 ottobre Nicolò aveva verificato un nostro risultato su DexScreener e non aveva trovato
l'acquisto. Aveva anche detto la cosa giusta: *«se non vedo neanche la transazione su DexScreener,
vuol dire che hanno comprato ancora prima, però nella chain»*.

Aveva ragione. Quell'acquisto **su DexScreener non c'è**, perché non è uno scambio del pool: è un
acquisto sulla curva, che DexScreener non mostra. Si vede solo sull'esploratore della chain.

**Quindi, per verificare un caso a mano serve l'esploratore, non DexScreener.** Su DexScreener si
vede la vendita, non l'acquisto.

## Cosa NON è ancora dimostrato, dichiarato

- **66 posizioni sono poche.** Tre fette su dieci della finestra storica sono coperte al 31-74%:
  i contatori sono stati azzerati stamattina per riparare l'errore delle unità. Servono due o tre
  giri perché il numero cresca.
- **Il 47% che non quadra** ha una spiegazione candidata e **non verificata**: gettoni spostati fra
  due portafogli della stessa persona (un trasferimento, nessuno swap). Va misurato, non assunto —
  è la spiegazione che viene in mente per prima, quindi quella da sospettare.
- **11.733 coppie non si sono potute confrontare** perché la moneta non ha un pool nel nostro
  registro. Probabile che siano monete morte sulla curva senza arrivare al mercato: anche questo
  va misurato.
- **Niente di tutto questo è ancora un guadagno.** Chi compra sulla curva **paga**: questi
  acquisti possono solo abbassare i multipli, mai alzarli.

## Il meccanismo

`agents/riconcilia_gettoni.py`, collegato alla corsia `curva_lanci` — nello stesso lavoro che
produce l'elenco dei lanci, perché la riconciliazione ha bisogno di quell'elenco fresco e metterla
in una corsia a parte vorrebbe dire aspettare lo scrittore unico del ramo.

Dichiara sempre quante posizioni **non** ha confrontato e perché: un confronto saltato in silenzio
diventa «quadra», che è la conclusione più comoda e quella sbagliata.
