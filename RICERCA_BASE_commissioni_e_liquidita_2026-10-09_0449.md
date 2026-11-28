# Ricerca Grok — Base — commissioni_e_liquidita

Modello grok-4.7. Costo: ZERO (abbonamento). Tempo: 153s. 2/2 con risposta.

---

### Quali commissioni si pagano comprando e vendendo sulla curva della principale piattaforma di lancio di Base, e chi le incassa? Col link.

Cerco le commissioni sulla curva della piattaforma di lancio principale di Base e chi le incassa, con la fonte ufficiale.I dati di volume indicano Bankr come piattaforma dominante su Base. Verifico se usa una curva e come sono ripartite le fee.**Su Bankr, la piattaforma di lancio più grande su Base, comprare e vendere costa l’1,75% del volume, uguale in entrambe le direzioni.** La curva è un pool Uniswap v4 di Doppler (multicurve): si scambia lì dal primo secondo, senza una fase bonding curve separata e senza graduation.

Fonte: [Fee Structure, Bankr](https://docs.bankr.bot/token-launching/overview#fee-structure). Bankr è prima per fee di lancio su Base: 1,05 M$ in 30 giorni, il 34,9% del totale della chain al 7 ottobre 2026 ([MemeFees / DefiLlama](https://memefees.com/chains/base)).

Su un lancio Doppler attuale l’1,75% si divide così:

| Chi incassa | Quota del volume |
|---|---|
| Creator del token (prelevabile) | 0,665% |
| Liquidità bloccata nel pool del token | 0,285% |
| Bankr (protocol fee) | 0,475% |
| Buyback di BNKR e liquidità BNKR del protocollo | 0,2375% |
| Doppler | ~0,0875% |

Il creator, di default il wallet che ha lanciato, incassa la sua quota in token e in WETH (o solo nella quote currency, se il lancio è quote-only). La quota LP non si preleva: resta nel pool. La schedule è fissata al lancio: i token più vecchi tengono la fee con cui sono nati (0,7% pool, 95% al creator, più una fee Bankr separata in WETH).

Nei primi **14 secondi** la fee parte dall’**80%** e scende fino all’1,75%. Quella maggiorazione la incassa Bankr.

### Alla graduazione la liquidita' viene bloccata? Esiste una funzione per sbloccarla? Col link.

Cerco nel progetto e nelle fonti cosa succede alla liquidità alla graduazione, e se esiste una funzione di sblocco.Nel progetto c’è già una ricerca sulla graduazione. La apro e verifico sul codice se la liquidità resta bloccata e se esiste uno sblocco.La nota interna dice che la posizione finisce in un locker senza unlock. Controllo il sorgente del contratto, così il link è sulla funzione vera.Sì. Alla graduazione di Pons v2 la liquidità viene bloccata per sempre. Non esiste una funzione per sbloccarla.

Il pool Uniswap v4 nasce full-range e la posizione (l'NFT che rappresenta la liquidità) viene mintata direttamente dentro `PonsV2LaunchLocker`. Il contratto dichiara di non esporre né un prelievo né una chiamata arbitraria, quindi né il creatore né un amministratore possono togliere quella liquidità.

Le uniche funzioni del locker sono di chiusura, non di apertura:

- [`lockPosition`](https://github.com/ponsdotdev/pons-labs/blob/main/contractsV2/src/v2/PonsV2LaunchLocker.sol#L91-L106) registra la custodia permanente dell'NFT.
- [`lockTokenSupply`](https://github.com/ponsdotdev/pons-labs/blob/main/contractsV2/src/v2/PonsV2LaunchLocker.sol#L104-L117) blocca i gettoni in eccesso che non entrano nel pool, altrimenti il prezzo di apertura scenderebbe.
- [`isLocked`](https://github.com/ponsdotdev/pons-labs/blob/main/contractsV2/src/v2/PonsV2LaunchLocker.sol#L118-L122) dice solo se è già bloccato.

La frase sta nell'intestazione del contratto: [niente withdrawal](https://github.com/ponsdotdev/pons-labs/blob/main/contractsV2/src/v2/PonsV2LaunchLocker.sol#L10-L20). Sulla chain il locker è [`0x267444D099b10fB5Ed7c3Cc7B7c767AdcA574952`](https://robinhoodchain.blockscout.com/address/0x267444D099b10fB5Ed7c3Cc7B7c767AdcA574952).

[`rescueSweptGraduation`](https://github.com/ponsdotdev/pons-labs/blob/main/contractsV2/src/v2/PonsV2LaunchFactory.sol#L1254-L1285) non è uno sblocco. Parte solo se il pool non è mai nato (fase `Swept`), dopo 7 giorni, e solo dall'owner. Appena la fase è `PoolCreated`, quella chiamata fallisce.
