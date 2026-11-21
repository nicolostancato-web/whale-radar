"""Il mestiere del mercante paga? Si segue il denaro (lezione del 23/10).

Se mettere liquidita' rende, chi lo fa ACCUMULA nativo. Si guarda il saldo di
ogni mercante adesso e qualche ora fa. Richiede stato storico: se l'RPC
risponde 403 su blocchi vecchi, e' il confine d'archivio, non un errore.
Nota: il saldo cambia anche per altri motivi; serve solo a vedere il SEGNO su
piu' indirizzi insieme, non a fare la contabilita' di uno.
"""
import json, urllib.request, collections, statistics as st
RPC="https://rpc.mainnet.chain.robinhood.com"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
MODL="0xf208f4912782fd25c7f114ca3723a2d5dd6f3bcc3ac8db5af63baa85f711d5ec"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception as e: return {"__err":str(e)}

ult=int(rpc("eth_blockNumber",[]),16)
INDIETRO=int(__import__('sys').argv[1]) if len(__import__('sys').argv)>1 else 20000
tx=collections.OrderedDict()
for b in range(ult-3000, ult, 100):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[MODL],
          "fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
        tx.setdefault(L["transactionHash"], True)
chi=collections.Counter()
for h in list(tx)[:200]:
    t=rpc("eth_getTransactionByHash",[h])
    if isinstance(t,dict) and t.get("from"): chi[t["from"].lower()]+=1
print(f"{len(chi)} mercanti distinti\n")

var=[]
for a,n in chi.most_common(18):
    ora=rpc("eth_getBalance",[a,hex(ult)])
    pri=rpc("eth_getBalance",[a,hex(ult-INDIETRO)])
    if not isinstance(pri,str) or not isinstance(ora,str):
        print("   stato storico non disponibile (confine d'archivio)"); break
    d=(int(ora,16)-int(pri,16))/1e18
    var.append(d)
    print(f"   {a[:20]}…  {n:>3} mosse   saldo {d:+.4f} nativi in finestra")
if var:
    pos=sum(1 for x in var if x>0)
    print(f"\n   in guadagno: {pos}/{len(var)} | mediana {st.median(var):+.4f} | somma {sum(var):+.4f}")
    print("   -> " + ("I MERCANTI ACCUMULANO: il mestiere paga, vale provarlo"
          if st.median(var) > 0 else "NON accumulano: il mestiere non paga come sembra"))
