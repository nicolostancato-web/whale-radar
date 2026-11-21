"""Quanto vale il locale gTrade: le commissioni vere pagate da chi scambia.

GovFeeCharged(address indexed trader, uint8 indexed collateralIndex,
              uint256 amountCollateral)  -- firma CONFERMATA per nome.
Il dato e' l'importo; l'indice del collaterale dice in che moneta e' espresso,
e quello va risolto, non assunto (un importo senza la sua moneta non e' un
numero). Su gTrade i collaterali sono tipicamente DAI/WETH/USDC: si verifica
leggendo il contratto, e se non si riesce si DICHIARA.
"""
import sys, json, urllib.request, collections, statistics as st
sys.path.insert(0,"agents"); from keccak import keccak256
RPC="https://arb1.arbitrum.io/rpc"; D="0xff162c694eaa571f685030649814282ea457f169"
GOV="0x"+keccak256(b"GovFeeCharged(address,uint8,uint256)").hex()
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=45) as f: return json.load(f).get("result")
    except Exception: return None
def sel(s): return "0x"+keccak256(s.encode()).hex()[:8]
def testo(h):
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace").strip()
    except Exception: return None
# risolvo i collaterali chiedendoli al contratto
coll={}
for i in range(1,6):
    r=rpc("eth_call",[{"to":D,"data":sel("getCollateral(uint8)")+hex(i)[2:].rjust(64,"0")},"latest"])
    if r and len(r)>=66:
        a="0x"+r[2:66][-40:]
        if a!="0x"+"0"*40:
            sym=testo(rpc("eth_call",[{"to":a,"data":sel("symbol()")},"latest"]))
            dec=rpc("eth_call",[{"to":a,"data":sel("decimals()")},"latest"])
            coll[i]=(sym, int(dec,16) if dec else None, a)
print("collaterali risolti dal contratto:", {k:(v[0],v[1]) for k,v in coll.items()} or "NESSUNO")
ult=int(rpc("eth_blockNumber",[]),16); BL=60000     # ~4,2 ore
per=collections.defaultdict(list)
for b in range(ult-BL, ult, 4000):
    r=rpc("eth_getLogs",[{"address":D,"topics":[GOV],"fromBlock":hex(b),"toBlock":hex(min(b+3999,ult))}])
    if isinstance(r,list):
        for L in r:
            idx=int(L["topics"][2],16)
            per[idx].append(int(L["data"],16))
ore=BL*0.25/3600
print(f"\n{sum(len(v) for v in per.values())} commissioni in ~{ore:.1f} ore\n")
EUR={"USDC":0.92,"DAI":0.92,"WETH":3030.0,"USDT":0.92,"ETH":3030.0}
tot=0.0; ignoti=0
for idx,v in sorted(per.items()):
    if idx in coll and coll[idx][0] in EUR and coll[idx][1]:
        sym,dec,_=coll[idx]
        s=sum(v)/10**dec*EUR[sym]
        tot+=s
        print(f"   collaterale {idx} ({sym}): {len(v):>4} commissioni, {s:>10,.2f} EUR")
    else:
        ignoti+=len(v)
        print(f"   collaterale {idx}: {len(v):>4} commissioni, moneta NON RISOLTA -> non valutate")
if tot:
    print(f"\n   commissioni di governance: {tot:,.0f} EUR in {ore:.1f} ore = {tot*24/ore:,.0f} EUR al giorno")
    print(f"   (e' UNA voce sola: le altre commissioni di gTrade non sono contate qui)")
if ignoti: print(f"   non valutate: {ignoti} commissioni")
