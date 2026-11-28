# -*- coding: utf-8 -*-
"""A QUALE FAMIGLIA APPARTIENE OGNI GETTONE, in un posto solo.

Perche' esiste (4/11 mattina). Questa tabella stava dentro
prepara_vendite.py, e tre agenti la leggevano RASCHIANDOLA dal file con
un'espressione regolare. Appena ho aggiunto una riga con un commento in
coda, l'espressione ha preso anche il codice dopo e tutto e' crollato con
un NameError. Una tabella che tutti leggono vuole un posto suo.

A COSA SERVE: la salute di una posizione e' garanzia*soglia/debito, quindi
si muove solo se garanzia e debito stanno in famiglie DIVERSE. In un dump
ETH e i suoi derivati scendono insieme, le stabili restano:
  garanzia ETH / debito stabile  -> la salute scende, CADE
  garanzia ETH / debito ETH      -> non si muove, NON cade
  garanzia stabile / debito ETH  -> la salute SALE, piu' sicura

LE FAMIGLIE CHE SCENDONO sono ETH, BTC e VOL. VOL sono i volatili che non
derivano da ETH ma scendono comunque (LINK, AAVE): trattarli come stabili
diceva che una posizione LINK/USDC non cade mai, ed e' l'errore nella
direzione PERICOLOSA -- ci faceva sembrare coperti mentre cadono davvero.
Tutto il resto e' "USD" per difetto, e sta bene: i gettoni non elencati
sono stati verificati sulla catena il 4/11 e sono tutti stabili (EURC,
GHO, DAI, PYUSD, RLUSD, USDtb, USDS, USDG, USDe, USDC, USDT, sUSDe,
syrupUSDT) piu' XAUt, che e' oro e va per conto suo.
"""
SCENDONO = ("ETH", "BTC", "VOL")
TABELLA = {
 # --- famiglia ETH: costano come ETH e si muovono con ETH
 "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0": "ETH",   # wstETH
 "0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee": "ETH",   # weETH
 "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": "ETH",   # WETH
 "0xae78736cd615f374d3085123a210448e74fc6393": "ETH",   # rETH
 "0xf1c9acdc66974dfb6decb12aa385b9cd01190e38": "ETH",   # osETH
 "0xbe9895146f7af43049ca1c1ae358b0541ea49704": "ETH",   # cbETH
 "0xa35b1b31ce002fbf2058d22f30f95d405200a15b": "ETH",   # ETHx
 "0xd9a442856c234a39a81a089c06451ebaa4306a72": "ETH",   # pufETH
 # rsETH: AGGIUNTO il 4/11. Costa 2.463 dollari, e la tabella lo trattava
 # come un dollaro: una posizione rsETH/WETH veniva contata come se
 # cadesse in un dump, mentre garanzia e debito si muovono insieme.
 # Gonfiava di 1,7 milioni il premio che dicevo esposto al dump.
 "0xa1290d69c65a6fe4df752f95823fae25cb99e5a7": "ETH",   # rsETH
 # --- famiglia BTC
 "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": "BTC",   # WBTC
 "0x8236a87084f8b84306f72007f36f2618a5634494": "BTC",   # LBTC
 "0x18084fba666a33d37592fa2633fd49a74dd93a88": "BTC",   # tBTC
 "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf": "BTC",   # cbBTC
 # --- volatili che scendono comunque (AGGIUNTI il 4/11)
 "0x514910771af9ca656af840dff83e8264ecf986ca": "VOL",   # LINK
 "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9": "VOL",   # AAVE
}
def famiglia(gettone):
    return TABELLA.get((gettone or "").lower(), "USD")
def scende(gettone):
    """In un dump questo gettone perde valore?"""
    return famiglia(gettone) in SCENDONO
def coppia_uguale(garanzia, debito):
    """Garanzia e debito nella stessa famiglia -> la salute non si muove."""
    return famiglia(garanzia) == famiglia(debito)
