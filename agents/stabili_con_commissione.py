"""La categoria giusta: incassare una commissione scritta nel contratto, su una
coppia dove il prezzo non puo' divergere.

Fornire liquidita' e' gia' «commissione contrattuale», ma l'avevo provata male
due volte: sulle monetine mi uccideva il crollo (motivo esterno alla
categoria), sui dollari di Base la commissione era ~0.
Qui si cerca la combinazione che conta: coppia STABILE + commissione VERA +
volume VERO, su piu' chain. Il rendimento e' commissioni/capitale, e la perdita
da divergenza e' minima per costruzione.
Ogni costante e' derivata dove si usa.
"""
import sys, json, urllib.request, collections, statistics as st
sys.path.insert(0,"agents"); from keccak import keccak256
SWAP3="0x"+keccak256(b"Swap(address,address,int256,int256,uint160,uint128,int24)").hex()
CH={"Base":"https://base.drpc.org","Arbitrum":"https://arb1.arbitrum.io/rpc",
    "Polygon":"https://polygon.drpc.org"}
STAB={"USDC","USDT","DAI","USDC.E","USDBC","FRAX","LUSD","USDS","EURC","GHO","USDE","CRVUSD"}
def rpc(u,m,p):
    r=urllib.request.Request(u,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=35) as f: return json.load(f).get("result")
    except Exception: return None
def sel(s): return "0x"+keccak256(s.encode()).hex()[:8]
def testo(h):
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace").strip()
    except Exception: return "?"
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
for nome,u in CH.items():
    ult=rpc(u,"eth_blockNumber",[])
    if not ult: print(f"\n{nome}: non raggiungibile"); continue
    ult=int(ult,16)
    PASSO=100; GIRI=12
    per=collections.Counter()
    for i in range(GIRI):
        b=ult-(i+1)*PASSO
        L=rpc(u,"eth_getLogs",[{"topics":[SWAP3],"fromBlock":hex(b),"toBlock":hex(b+PASSO-1)}])
        if isinstance(L,list):
            for x in L: per[x["address"].lower()]+=1
    print(f"\n{nome}: {sum(per.values())} scambi in {GIRI*PASSO} blocchi, {len(per)} pool")
    trovati=0
    for p,n in per.most_common(40):
        t0=rpc(u,"eth_call",[{"to":p,"data":sel("token0()")},"latest"])
        t1=rpc(u,"eth_call",[{"to":p,"data":sel("token1()")},"latest"])
        if not t0 or not t1: continue
        a="0x"+t0[-40:]; b_="0x"+t1[-40:]
        sa=testo(rpc(u,"eth_call",[{"to":a,"data":sel("symbol()")},"latest"])).upper()
        sb=testo(rpc(u,"eth_call",[{"to":b_,"data":sel("symbol()")},"latest"])).upper()
        if sa not in STAB or sb not in STAB: continue
        fe=rpc(u,"eth_call",[{"to":p,"data":sel("fee()")},"latest"])
        fee = int(fe,16) if fe else None
        trovati+=1
        print(f"   {sa}/{sb:<7} {n:>4} scambi  fee={'non leggibile' if fee is None else f'{fee/10000:.3f}%'}  {p[:14]}…")
        if trovati>=6: break
    if not trovati: print("   nessuna coppia stabile fra i pool piu' attivi")
