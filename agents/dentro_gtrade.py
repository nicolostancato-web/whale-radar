"""Che cosa succede dentro gTrade, il mercato decentralizzato di valute e
materie prime su Arbitrum.

Indirizzo verificato, non ricordato: il token dichiara "Gains Network" e il
diamante emette migliaia di eventi all'ora.

Primo passo puramente descrittivo: quali firme emette e con che frequenza.
Le firme note di gTrade si provano per NOME (calcolato, non ricordato) e si
vede quali combaciano: cosi' l'identificazione e' verificabile.
"""
import sys, json, urllib.request, collections
sys.path.insert(0,"agents"); from keccak import keccak256
RPC="https://arb1.arbitrum.io/rpc"
D="0xff162c694eaa571f685030649814282ea457f169"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=45) as f: return json.load(f).get("result")
    except Exception: return None
def firma(s): return "0x"+keccak256(s.encode()).hex()
ult=int(rpc("eth_blockNumber",[]),16)
BL=40000      # Arbitrum ~0,25 s/blocco -> ~2,8 ore
c=collections.Counter()
for b in range(ult-BL, ult, 4000):
    r=rpc("eth_getLogs",[{"address":D,"fromBlock":hex(b),"toBlock":hex(min(b+3999,ult))}])
    if isinstance(r,list):
        for L in r: c[L["topics"][0]]+=1
ore=BL*0.25/3600
print(f"gTrade diamond | {sum(c.values()):,} eventi in ~{ore:.1f} ore\n")
# dizionario di firme CALCOLATE dai nomi plausibili dell'ABI pubblico
prova={}
for n in ("MarketExecuted(address,uint32,(address,uint32,uint16,uint24,bool,bool,uint8,uint120,uint64,uint64,uint64,uint192),bool,uint64,uint256,uint256,int256,uint256,uint256)",
          "LimitExecuted(address,uint32,uint32,address,uint8,(address,uint32,uint16,uint24,bool,bool,uint8,uint120,uint64,uint64,uint64,uint192),(address,uint32,uint16,uint24,bool,bool,uint8,uint120,uint64,uint64,uint64,uint192),uint64,uint256,uint256,int256,uint256,uint256,bool)",
          "PositionSizeIncreaseExecuted(bytes32,uint256)",
          "BorrowingFeeCharged(address,uint8,uint256)",
          "GovFeeCharged(address,uint8,uint256)",
          "TriggerFeeCharged(address,uint8,uint256)",
          "FeeCharged(address,uint8,uint256)",
          "OpenOrderPlaced(address,uint32,uint32)",
          "TradeClosed(bytes32)"):
    prova[firma(n)] = n.split("(")[0]
print("   firma                                                               volte   nome se riconosciuto")
for t,n in c.most_common(10):
    print(f"   {t}  {n:>6}   {prova.get(t,'?')}")
noti=sum(n for t,n in c.items() if t in prova)
print(f"\n   eventi riconosciuti per nome: {noti}/{sum(c.values())}")
print("   (le firme non riconosciute vanno decodificate dall'ABI pubblico:")
print("    non si tira a indovinare il significato di un evento)")
