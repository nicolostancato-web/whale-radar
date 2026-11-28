"""Esiste un mercato del prestito su questa chain? Si cercano le LIQUIDAZIONI.

Firme calcolate, non ricordate (agents/keccak.py). Si guardano i tre protocolli
piu' diffusi piu' una firma generica. Se in dieci ore non ce n'e' nessuna, la
strada si chiude per capienza come UniswapX, senza studiare altro.
"""
import sys, json, urllib.request, collections
sys.path.insert(0,"agents"); from keccak import firma
RPC="https://rpc.mainnet.chain.robinhood.com"
FIRME={
 "Morpho Blue": "Liquidate(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)",
 "Aave v3":     "LiquidationCall(address,address,address,uint256,uint256,address,bool)",
 "Compound v3": "AbsorbDebt(address,address,uint256,uint256)",
 "Euler":       "Liquidate(address,address,address,uint256,uint256,uint256)",
 "generica":    "Liquidation(address,address,uint256,uint256)",
}
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
ult=int(rpc("eth_blockNumber",[]),16); FIN=600000; PASSO=5000
ore=FIN*0.093/3600
print(f"finestra ~{ore:.1f} ore\n")
for nome,ev in FIRME.items():
    t=firma(ev); tot=0; dove=collections.Counter()
    for b in range(ult-FIN, ult, PASSO):
        for L in rpc("eth_getLogs",[{"topics":[t],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
            tot+=1; dove[L["address"].lower()]+=1
    print(f"   {nome:<12} {t[:18]}…  {tot:>4} eventi" +
          (f"   contratti: {[a[:12] for a,_ in dove.most_common(2)]}" if tot else ""))
print("\n   -> se tutto zero: nessun mercato del prestito attivo. Strada chiusa per capienza.")
