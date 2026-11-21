# Ricerca Grok — Base — dati_pubblici_base

Modello grok-4.7. Costo: ZERO (abbonamento). Tempo: 168s. 2/2 con risposta.

---

### Quali fonti dati gratuite esistono per Base: endpoint RPC pubblici, limiti di blocchi per chiamata su eth_getLogs, explorer con API. Dammi i numeri e i link.

Cerco i numeri aggiornati su RPC pubblici di Base, limiti di `eth_getLogs` e API degli explorer.I documenti ufficiali confermano il tetto di circa 2.000 blocchi sull’RPC di Base. Verifico i rate limit numerici e le API degli explorer.

### Su Base, l'indirizzo del gestore dei pool di Uniswap v4 e il factory di Uniswap v3: dammi gli indirizzi, col link alla fonte.

Cerco gli indirizzi ufficiali del PoolManager di Uniswap v4 e della factory di Uniswap v3 su Base, con la fonte.Su Base mainnet (chain id 8453):

**Uniswap v4 — PoolManager** (il singleton che gestisce tutti i pool; in v4 non c’è una factory)

`0x498581fF718922c3f8e6A244956aF099B2652b2b`

Fonte: [Uniswap v4 Deployments, sezione Base: 8453](https://developers.uniswap.org/docs/protocols/v4/deployments) · [contratto su Basescan](https://basescan.org/address/0x498581ff718922c3f8e6a244956af099b2652b2b)

**Uniswap v3 — UniswapV3Factory**

`0x33128a8fC17869897dcE68Ed026d694621f6FDfD`

Fonte: [Uniswap v3 Base Deployments](https://developers.uniswap.org/docs/protocols/v3/deployments/v3-base-deployments) · [contratto su Basescan](https://basescan.org/address/0x33128a8fC17869897dcE68Ed026d694621f6FDfD)

Sono gli indirizzi di Base mainnet. Su Base Sepolia sono diversi.
