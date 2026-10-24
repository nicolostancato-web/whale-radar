"""Il test piu' economico di Grok: le donazioni agli LP battono il gas?

Se il gas speso per muovere la liquidita' e' >= di quello che l'hook restituisce
agli LP, questo movimento NON e' un mestiere di commissioni, e si chiude qui
senza ricostruire nessuna posizione.

Nota di metodo (Grok, 23/10): la vita di 4,7 s di una posizione e' ~50 blocchi
su una chain da 100 ms, cioe' un mercante che RICENTRA, non che chiude. Quindi
non si conta mossa per mossa: si sommano i totali sulla finestra.
"""
import json, urllib.request, collections
RPC="https://rpc.mainnet.chain.robinhood.com"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
MODL="0xf208f4912782fd25c7f114ca3723a2d5dd6f3bcc3ac8db5af63baa85f711d5ec"
DONA="0x29ef05caaff9404b7cb6d1c0e9bbae9eaa7ab2541feba1a9c4248594c08156cb"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
def s256(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v

ult=int(rpc("eth_blockNumber",[]),16)
FIN=6000      # ~9 minuti
don_tot=0.0; n_don=0; tx_mod=collections.OrderedDict()
for b in range(ult-FIN, ult, 100):
    a=hex(min(b+99,ult))
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[DONA],"fromBlock":hex(b),"toBlock":a}]) or []:
        d=L["data"][2:]
        # Donate(id indexed, sender indexed, amount0, amount1)
        a0=s256(d[0:64]) if len(d)>=64 else 0
        don_tot += abs(a0)/1e18; n_don += 1
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[MODL],"fromBlock":hex(b),"toBlock":a}]) or []:
        tx_mod.setdefault(L["transactionHash"], True)

print(f"finestra {FIN} blocchi (~{FIN*0.093/60:.0f} min)")
print(f"   Donate: {n_don} eventi, {don_tot:.6f} nativi restituiti agli LP")
print(f"   transazioni che muovono liquidita': {len(tx_mod)}")

gas=0.0; letti=0
for h in list(tx_mod)[:120]:
    r=rpc("eth_getTransactionReceipt",[h])
    if not r: continue
    gas += int(r["gasUsed"],16)*int(r.get("effectiveGasPrice","0x0"),16)/1e18; letti+=1
if letti:
    medio=gas/letti; stima=medio*len(tx_mod)
    print(f"   gas: {letti} ricevute lette, medio {medio:.8f} nativi")
    print(f"   gas TOTALE stimato sulla finestra: {stima:.6f} nativi")
    print(f"\n   donazioni / gas = {don_tot/max(stima,1e-12):.2f}")
    print("   -> " + ("NON e' un mestiere di commissioni: il gas si mangia le donazioni"
          if don_tot < stima else "le donazioni battono il gas: vale il registro per entita'"))
