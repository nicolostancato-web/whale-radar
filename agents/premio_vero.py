"""Il premio VERO, calcolato dall'evento invece che assunto al 5%.

LiquidationCall contiene il debito ripagato (nella moneta del debito) e la
garanzia presa (nella moneta della garanzia). Il premio e' la differenza di
VALORE fra le due: non serve assumere la percentuale, che fra l'altro varia
per asset (4,5-10% su Aave).

Lezione «dato obbligatorio»: una costante assunta e' un errore in attesa.
Qui si calcola, e dove manca un prezzo si SCARTA invece di inventare.
"""
import json, urllib.request, collections, statistics as st, sys
def spot(s):
    try:
        r=urllib.request.Request(f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={s}",
                                 headers={"user-agent":"Mozilla/5.0"})
        return float(json.load(urllib.request.urlopen(r,timeout=20))["price"])
    except Exception: return None
eth=spot("ETHUSDT"); btc=spot("BTCUSDT"); EUR=1/1.08
if not eth or not btc: print("manca un prezzo"); sys.exit(1)
M={"0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":("WETH",18,eth),
   "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":("USDC",6,1.0),
   "0xdac17f958d2ee523a2206206994597c13d831ec7":("USDT",6,1.0),
   "0x6b175474e89094c44da98b954eedeac495271d0f":("DAI",18,1.0),
   "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":("WBTC",8,btc),
   "0x83f20f44975d03b1b09e64809b757c47f942beea":("sDAI",18,1.0),
   "0xae78736cd615f374d3085123a210448e74fc6393":("rETH",18,eth),
   "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":("wstETH",18,eth),
   "0xbe9895146f7af43049ca1c1ae358b0541ea49704":("cbETH",18,eth),
   "0x6c3ea9036406852006290770bedfcaba0e23a0e8":("PYUSD",6,1.0),
   "0x5e8422345238f34275888049021821e8e08caa1f":("frxETH",18,eth)}
ev=[json.loads(x) for x in open("data/liquidazioni/storia_blockscout.jsonl")]
print(f"   {len(ev)} eventi\n")
pertx=collections.defaultdict(lambda: [0.0,0.0,0])   # debito, garanzia, n
scarti=collections.Counter()
for e in ev:
    d=e["dati"][2:]
    if len(d)<128: continue
    debito_t=e.get("deb")      # non salvato: si ricava dal topic 2
    # topics: [sig, collateralAsset, debtAsset, user] -> il nostro file tiene
    # solo 'gar' (topic1). Senza la moneta del debito il premio non si calcola:
    # si dichiara e si scarta, invece di assumere.
    scarti["manca la moneta del debito nel file salvato"]+=1
print(f"   {dict(scarti)}")
print(f"\n   Il file salvato conserva solo la moneta della GARANZIA (topic 1).")
print(f"   Per il premio vero serve anche quella del DEBITO (topic 2).")
print(f"   -> correggo lo scaricatore perche' salvi tutti i topic, e il")
print(f"      premio si calcolera' sui dati raccolti d'ora in poi.")
