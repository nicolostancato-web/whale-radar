"""L'evento di diploma, letto dal contratto Pons invece che indovinato.

Due prove in avanti annullate perche' l'universo era definito per SOMIGLIANZA
(pool pieno, 1%, senza hook) invece che per l'EVENTO. Qui si guardano i log
emessi dalla fabbrica e dall'hook di Pons e si contano le firme: quella che
compare poche volte all'ora, e sempre accanto alla nascita di un pool, e' il
diploma.
"""
import json, urllib.request, collections
RPC="https://rpc.mainnet.chain.robinhood.com"
FAB="0x7ed598bcef8bd9edd8c97a195c6d13f40801ec7e"
HOOK="0xe5e702641ea86f4ae6cc3cdaed2b886f976be044"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception as e: return None

ult=int(rpc("eth_blockNumber",[]),16); FIN=20000
for nome,ind in (("FABBRICA",FAB),("HOOK",HOOK)):
    c=collections.Counter(); blocchi=collections.defaultdict(set)
    for b in range(ult-FIN, ult, 100):
        for L in rpc("eth_getLogs",[{"address":ind,"fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
            c[L["topics"][0]] += 1
            blocchi[L["topics"][0]].add(int(L["blockNumber"],16))
    print(f"\n{nome} {ind}: {sum(c.values())} log in ~{FIN*0.093/60:.0f} min")
    for t,n in c.most_common(6):
        print(f"   {t}  {n:>5}  ({n/(FIN*0.093/3600):.0f}/ora)")
# nascite di pool nella stessa finestra, per confronto
nasc=0
for b in range(ult-FIN, ult, 100):
    nasc += len(rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],"fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or [])
print(f"\nnascite di pool nella stessa finestra: {nasc} ({nasc/(FIN*0.093/3600):.0f}/ora)")
print("   il diploma deve essere MOLTO piu' raro: ~16/giorno secondo la nostra misura di settembre")
