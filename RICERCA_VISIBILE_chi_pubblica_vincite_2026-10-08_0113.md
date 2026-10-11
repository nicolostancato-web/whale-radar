# Ricerca Grok — chi_pubblica_vincite

Modello grok-4.7. Costo: ZERO (abbonamento, nessuna chiave API). Tempo: 183s. 2/2 sotto-domande con risposta.

---

### Su X, chi pubblica guadagni su Robinhood Chain o su Pons mostrando l'indirizzo del portafoglio o il link alla transazione? Dammi i profili e un esempio di post.

Cerco su X i post pubblici in cui qualcuno mostra guadagni su Robinhood Chain o su Pons insieme all’indirizzo del portafoglio o al link della transazione.I primi risultati sono quasi tutti claim e airdrop. Cerco post in cui qualcuno mostra un guadagno reale, con indirizzo o link alla transazione.Su X i guadagni su Robinhood Chain e su Pons li pubblicano soprattutto account che mostrano il portafoglio di qualcun altro, con indirizzo o link. I post in prima persona del tipo «ho guadagnato io» quasi mai includono l’indirizzo o la transazione.

**@kkashi_yt (Kakashi)** è il profilo più costante. Pubblica il profitto e, nel messaggio subito sotto, il wallet. Il 15 luglio 2026: «This wallet turned $29 to over $133,000 profit on $Pons». Nella risposta scrive che il profitto è in realtà oltre $151.000, e indica i due indirizzi:

- acquisto: `0xd73d6b8b9e875569c0f03c572a3806e619bcbec2`
- wallet a cui ha mandato i token: `0x2c3af5d870f2f0704b44c4bd02016a8cb752399f`

Post: https://x.com/kkashi_yt/status/2077351837196484612

Lo rifà ancora. Il 17 settembre: da $2.667 a oltre $1.000.000 su $PONS, wallet `0x81b98a0e207726584ce1ac687fcae6059b35ebcf`. Il 30 settembre: oltre $1.121.000 sullo stesso token, wallet `0x82797a749189f3b99556191d395bfbef709a44c4`. Nella bio avvisa che parte di questi profitti può essere di insider. Non dice che sono trade suoi.

**@coromaroco (Miss Bao)** fa la stessa cosa, su cifre piccole. Il 7 ottobre 2026: «someone turned just $61 into $940 on $BCI», e nel messaggio sotto il wallet su GMGN:

https://gmgn.ai/robinhood/address/6KxYIQs3_0xfe657a36ceef09011eba0551dae96ae07dd38518

Post: https://x.com/coromaroco/status/2107757221341970789

**@_Kriptopia (PIA)** è uno dei pochi in prima persona. Il 14 settembre 2026: «Thanks $PONS. I just made $425», con screenshot e la procedura per lanciare un token su Pons (wallet vecchio, tax fee al 2%). Nel testo non ci sono né indirizzo né transazione.

Post: https://x.com/_Kriptopia/status/2099632251961008638

Due cose da non confondere con questi post. Il flex di **@kenji_hl** («i made $8M on $PONS», 7 ottobre) non ha né wallet né transazione. E i post «claim $PONS, collega il wallet» che girano in queste ore sono spam di airdrop finti, non rendiconti di guadagni.

### Esistono classifiche pubbliche di portafogli vincenti su Robinhood Chain? Dammi i link e di' se i dati sono controllabili sulla chain.

Cerco classifiche pubbliche di portafogli su Robinhood Chain e verifico se i numeri si possono ricontrollare on-chain.Ho trovato diverse board. Controllo quali pubblicano indirizzi e metodologia, e quali sembrano numeri generati.Sì. Esistono classifiche pubbliche di wallet su Robinhood Chain (chain ID 4663, L2 Arbitrum). Nessuna è ufficiale di Robinhood. Il profitto non è un campo della chain: gli swap e i saldi sì, il PnL è un calcolo di chi ha fatto la classifica.

## Cosa si può ricontrollare

Su [Blockscout](https://robinhoodchain.blockscout.com) e sull’RPC pubblico `https://rpc.mainnet.chain.robinhood.com` si vedono transazioni, transfer e saldi di qualsiasi indirizzo `0x…`. Dune indicizza gli stessi swap in `dex.trades` con `blockchain = 'robinhood'`.

Un PnL è ricostruibile solo se la board pubblica l’indirizzo completo e dice come calcola il costo (vendite incrociate con gli acquisti, prezzo, quali DEX, realizzato o anche non realizzato). Bot, MEV, airdrop, bridge e token illiquidi spostano il numero senza che la chain “smentisca” la transazione.

## Board con indirizzi o SQL pubblico

| Board | Link | Cosa ordina | Controllabile on-chain |
|---|---|---|---|
| Dune, alpha traders 30g | [query 7940623](https://dune.com/queries/7940623) dentro [questa dashboard](https://dune.com/geggonen/robinhood-chain-analytics) | PnL realizzato su memecoin, ultimi 30 giorni. SQL pubblico. Ultimo run visto il 7–8 ottobre 2026. In testa, al momento del fetch: `0x942b…27fd` con circa $27,1M realizzati | Sì, la parte solida. Gli swap sono in `dex.trades`. Il dollaro dipende dal prezzo che Dune assegna. L’autore scrive che il conto è “on paper”, finestra corta, e può includere bot e MEV. Molti indirizzi `0x4337…` sono smart account (account abstraction), spesso bot |
| Stessa dashboard, moonshot | [geggonen/robinhood-chain-analytics](https://dune.com/geggonen/robinhood-chain-analytics) | Singola posizione vincente (token, capitale, multiplo), non il portafoglio intero | Stesso criterio: trade ricostruibili, multiplo dipendente dal prezzo |
| GMGN, CopyTrade / 牛人榜 | [gmgn.ai/?chain=robinhood](https://gmgn.ai/?chain=robinhood) e [gmgn.ai/trade?chain=robinhood](https://gmgn.ai/trade?chain=robinhood) | Wallet per PnL realizzato, win rate e numero trade, finestre 1 / 7 / 30 giorni. Lo descrive il [blog GMGN](https://gmgn.ai/blog/zh-cn/how-to-buy-new-robinhood-chain-launches/) | Swap sì, formula PnL no: è interna a GMGN. Si verifica aprendo l’indirizzo su Blockscout |
| Stalkchain KOL | [stalkchain.com/robinhood/kols/](https://stalkchain.com/robinhood/kols/) | KOL con wallet collegati, finestre 24h / 7g / 30g / all-time | Parziale. Sulla board aperta oggi quasi tutte le prime righe portano la dicitura “basis incomplete · unrealized partial”: il più in alto (circa +$1,55M) ha realizzato $0. Il loro stesso [articolo](https://stalkchain.com/blog/robinhood-chain-kol-tracker) dice di non usare la copertura incompleta come segnale |
| Stalkchain whale | [stalkchain.com/robinhood/whales](https://stalkchain.com/robinhood/whales) | Wallet per USD netto speso (acquisti − vendite), non per profitto | La spesa netta si può ricalcolare dagli swap. La “posizione stimata” è saldo × prezzo e loro la marcano solo come display |
| Nock Scout | [nockterminal.com/wallets](https://nockterminal.com/wallets) | Simulazione: quanto avrebbe fatto un follower da 1–3 ETH, non il profitto assoluto del wallet. Regole pubblicate (copia 2%, tetto 0,05 ETH, liquidità minima 0,75 ETH, penale 1% di latenza) | Indirizzi completi e link al wallet, e loro indicano Blockscout. I PnL restano stime del loro indexer. Sulla pagina di oggi lo scorer dice 1.090 swap su 300 wallet, mentre la riga #1 dichiara 3.926 trade: i due numeri non stanno insieme |

Distribuzione aggregata, senza nomi: [Dune di bigcent02](https://dune.com/bigcent02/robin-hood-chain-profitability-metrics) ([query](https://dune.com/queries/8099793)). È un istogramma di giugno–luglio 2026 (ultimo run circa 23 giorni fa): 1.833 wallet sopra i $10k realizzati, circa $85,8M di profitto in quel secchio. Utile come contesto, non come lista di portafogli.

## Da non prendere per una classifica

- [ponscopytrading.com/leaderboard](https://www.ponscopytrading.com/leaderboard). Indirizzi troncati (`0xfb21...31a9`), quindi non apribili. Il PnL scende di circa 6 ETH a ogni posto, ROI e win rate salgono in progressione quasi regolare e il win rate si incolla al 94%. È il disegno di una tabella generata. Senza indirizzo completo non c’è nulla da controllare.
- [Robinhood Investor Index](https://robinhood.com/us/en/investor-index). È l’indice delle azioni più tenute dai clienti del broker, aggiornato il 1° ottobre 2026. Non è Robinhood Chain e non è on-chain.
- [Top 10.000 wallet su Dune](https://dune.com/neveresleep_crypto/robinhood-chain). Ordina per numero di transazioni e volume nativo, non per guadagno.
- [API holder di Bitquery](https://docs.bitquery.io/docs/blockchain/robinhood/robinhood-token-holders-api/). Classifica chi detiene un token, per saldo.

Per un controllo rapido: prendi un indirizzo intero dalla query Dune, incollalo su `https://robinhoodchain.blockscout.com/address/<indirizzo>` e confronta gli swap del periodo con il PnL dichiarato. Se i numeri non tornano, la differenza sta nel prezzo o nel criterio di costo, non in una transazione nascosta.
