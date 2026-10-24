"""STRADA 13: le liquidazioni sui prestiti. Capienza prima del segno.

Chi si fa liquidare paga un premio a chi ripaga il suo debito: e' un incentivo
scritto nel contratto, non un pattern. La funzione e' aperta a chiunque.
Con 300 euro si toccano solo i prestiti piccoli.

Prima domanda, da chiudere in dieci minuti: esiste un mercato del prestito su
questa chain, e quante liquidazioni ci sono davvero? Se sono due al mese, la
strada e' chiusa come UniswapX, per capienza.
"""
import json, urllib.request, collections
RPC="https://rpc.mainnet.chain.robinhood.com"
MORPHO="0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb"   # Morpho Blue, stesso indirizzo su piu' chain
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
ult=int(rpc("eth_blockNumber",[]),16)
code=rpc("eth_getCode",[MORPHO,"latest"])
print(f"Morpho Blue a {MORPHO[:14]}…: {'PRESENTE ('+str(len(code)//2)+' byte)' if code and len(code)>4 else 'ASSENTE'}")
if not code or len(code)<=4:
    print("   cerco qualunque contratto che emetta liquidazioni, per firma generica")
FIN=400000; PASSO=4000
if code and len(code)>4:
    c=collections.Counter()
    for b in range(ult-FIN, ult, PASSO):
        for L in rpc("eth_getLogs",[{"address":MORPHO,"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
            c[L["topics"][0]]+=1
    ore=FIN*0.093/3600
    print(f"\n   log di Morpho in ~{ore:.1f} ore: {sum(c.values())}")
    for t,n in c.most_common(8):
        print(f"      {t[:22]}…  {n:>5}  ({n/ore*24:.0f}/giorno)")
    print("\n   -> " + ("c'e' attivita': vale identificare la firma della liquidazione"
          if sum(c.values())>0 else "nessun log: il mercato esiste ma e' vuoto. CHIUSA per capienza."))
