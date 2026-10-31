"""Quanto vale in euro una liquidazione, e qual e' il premio?

Morpho: idToMarketParams(bytes32) -> (loanToken, collateralToken, oracle, irm, lltv)
Il premio = valore del collaterale preso / valore del debito ripagato - 1.
Per valutare il collaterale serve il suo prezzo: si prende dall'oracolo del
mercato stesso, price(), che Morpho usa con 36+decimali di scala.
"""
import sys, json, urllib.request, collections
sys.path.insert(0,"agents"); from keccak import firma, keccak256
import dato_obbligatorio as DO
RPC="https://rpc.mainnet.chain.robinhood.com"
T=firma("Liquidate(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)")
SEL_MP="0x"+keccak256(b"idToMarketParams(bytes32)").hex()[:8]
SEL_PRICE="0x"+keccak256(b"price()").hex()[:8]
SEL_SYM="0x"+keccak256(b"symbol()").hex()[:8]
SEL_DEC="0x"+keccak256(b"decimals()").hex()[:8]
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
def call(to,d): return rpc("eth_call",[{"to":to,"data":d},"latest"])
def testo(h):
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace").strip()
    except Exception: return "?"
ult=int(rpc("eth_blockNumber",[]),16); FIN=1200000; PASSO=5000
ev=[]
for b in range(ult-FIN, ult, PASSO):
    for L in rpc("eth_getLogs",[{"topics":[T],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        d=L["data"][2:]
        ev.append((L["address"].lower(), L["topics"][1], int(d[0:64],16), int(d[128:192],16)))
cache={}
print(f"{len(ev)} liquidazioni\n")
print("   prestito  collaterale   ripagato      preso        premio")
prem=[]
for contr,mid,rip,preso in ev:
    if mid not in cache:
        r=call(contr, SEL_MP+mid[2:])
        if not r or len(r)<2+64*5: cache[mid]=None
        else:
            w=[r[2+i*64:2+(i+1)*64] for i in range(5)]
            lt="0x"+w[0][-40:]; ct="0x"+w[1][-40:]; orac="0x"+w[2][-40:]
            ld=DO.intero(call(lt,SEL_DEC), "i decimali del gettone"); cd=DO.intero(call(ct,SEL_DEC), "i decimali del gettone")
            pr=call(orac,SEL_PRICE); pr=int(pr,16) if pr else None
            cache[mid]=(testo(call(lt,SEL_SYM)), testo(call(ct,SEL_SYM)), ld, cd, pr)
    m=cache[mid]
    if not m: continue
    sl,sc,ld,cd,pr = m
    deb = rip/10**ld
    if pr:
        coll = preso/10**cd * pr/10**(36+ld-cd)
        p = coll/deb-1 if deb>0 else None
        prem.append(p)
        print(f"   {sl:<9} {sc:<12} {deb:>10.4f}  {preso/10**cd:>12.4f}  {p*100:+7.2f}%")
    else:
        print(f"   {sl:<9} {sc:<12} {deb:>10.4f}  {preso/10**cd:>12.4f}   oracolo muto")
if prem:
    import statistics as st
    print(f"\n   premio mediano: {st.median(prem)*100:+.2f}%  su {len(prem)} casi")
