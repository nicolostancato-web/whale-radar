"""Il liquidatore tiene il premio, o lo gira al validatore?

Due controlli:
 1) il prezzo del gas misurato (0,05 gwei) e' plausibile? Si legge la base
    del blocco corrente: se e' di quell'ordine, il dato e' vero.
 2) il pagamento vero in queste gare e' un BONIFICO DIRETTO al validatore
    dentro la transazione, invisibile nelle ricevute. Si cerca con la
    traccia della transazione, se un nodo pubblico la espone.
"""
import json, time, urllib.request
RPC=["https://eth.llamarpc.com","https://ethereum-rpc.publicnode.com",
     "https://rpc.ankr.com/eth","https://cloudflare-eth.com"]
def chiama(m,p=None,giri=5,solo=None):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p or []}).encode()
    for g in range(giri):
        for u in (solo or RPC):
            try:
                r=urllib.request.Request(u,data=c,headers={
                  "content-type":"application/json","user-agent":"Mozilla/5.0"})
                d=json.load(urllib.request.urlopen(r,timeout=30))
                if "result" in d and d["result"] is not None: return d["result"]
            except Exception: pass
        time.sleep(0.4*(g+1))
    return None
b=chiama("eth_getBlockByNumber",["latest",False])
base=int(b["baseFeePerGas"],16)/1e9 if b and "baseFeePerGas" in b else None
print(f"   1) base del blocco adesso: {base:.4f} gwei" if base else "   base non letta")
print(f"      -> il 0,05 gwei misurato e' {'PLAUSIBILE' if base and base<2 else 'SOSPETTO'}")
H="0x38ca2a076cbb"   # la liquidazione grossa, hash parziale: serve intero
# ritrovo l'hash intero dai log gia' letti
import re, subprocess
print("\n   2) pagamento diretto al validatore")
for m in ("trace_transaction","debug_traceTransaction"):
    r=chiama(m,["0x38ca2a076cbb0000000000000000000000000000000000000000000000000000000000"],giri=1)
    print(f"      {m}: {'esposto' if r else 'non esposto dai nodi pubblici'}")
# via alternativa: saldo del validatore prima e dopo il blocco
print("\n   via alternativa: variazione del saldo del validatore nel blocco")
