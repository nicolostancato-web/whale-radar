"""Il mio test sulla posizione nel blocco ha senso?

Se i blocchi sono pieni, la posizione misura la competizione: chi paga di
piu' sta davanti. Se sono mezzi vuoti, entra chiunque ovunque e la
posizione non misura NIENTE — e la mia conclusione «non e' una gara di
latenza» sarebbe letta da un segnale inesistente.

Si guarda il riempimento (gas usato su limite) e la mancia tipica.
"""
import json, time, urllib.request, statistics as st
RPC=["https://eth.llamarpc.com","https://ethereum-rpc.publicnode.com",
     "https://rpc.ankr.com/eth","https://cloudflare-eth.com"]
def chiama(m,p=None,giri=6):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p or []}).encode()
    for g in range(giri):
        for u in RPC:
            try:
                r=urllib.request.Request(u,data=c,headers={
                  "content-type":"application/json","user-agent":"Mozilla/5.0"})
                d=json.load(urllib.request.urlopen(r,timeout=30))
                if "result" in d and d["result"] is not None: return d["result"]
            except Exception: pass
        time.sleep(0.4*(g+1))
    return None
ult=int(chiama("eth_blockNumber"),16)
piene=[]; basi=[]
for i in range(0, 40, 2):
    b=chiama("eth_getBlockByNumber",[hex(ult-i), False])
    if not b: continue
    u=int(b["gasUsed"],16); l=int(b["gasLimit"],16)
    piene.append(u/l*100); basi.append(int(b.get("baseFeePerGas","0x0"),16)/1e9)
    time.sleep(0.1)
print(f"   {len(piene)} blocchi recenti")
print(f"   riempimento: mediana {st.median(piene):.0f}%  "
      f"min {min(piene):.0f}%  max {max(piene):.0f}%")
print(f"   base del gas: mediana {st.median(basi):.4f} gwei")
pieno = st.median(piene) > 85
print(f"\n   -> i blocchi sono {'PIENI: la posizione misura la competizione' if pieno else 'NON pieni: la posizione NON misura la competizione'}")
if not pieno:
    print(f"      Quindi il mio test «non e' una gara di latenza» e' SENZA")
    print(f"      FORZA: con blocchi al {st.median(piene):.0f}% entra chiunque")
    print(f"      ovunque, e la posizione non dice chi ha vinto una corsa.")
    print(f"      La domanda resta aperta e serve un'altra misura.")
