"""Quanto incassa il LOCALE, misurato dove il flusso passa davvero.

Due correzioni rispetto al tentativo precedente:
  - gli importi degli Swap v4 sono int128 ma SCRITTI su 256 bit gia' estesi:
    vanno letti come interi con segno a 256, non a 128 (errore da 10^38).
  - la curva di Pons NON e' un pool del PoolManager: e' un contratto a se'.
    Cercare pool con quell'hook dava giustamente zero. Il flusso della curva si
    misura sugli eventi del contratto di Pons.
"""
import sys, json, urllib.request, collections
sys.path.insert(0,"agents")
from keccak import firma
RPC="https://rpc.mainnet.chain.robinhood.com"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
HOOK="0xe5e702641ea86f4ae6cc3cdaed2b886f976be044"
SWAP=firma("Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)")
PRINC="0xc532c43b3423e14ef72748f1c8291238829ca0af8ba9b67975ad1483485a4b4d"  # 9.054/ora sull'hook
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
def s256(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ETH=3030.0
ult=int(rpc("eth_blockNumber",[]),16); FIN=int(3600/0.093); PASSO=2000
print(f"una ora di chain ({FIN:,} blocchi)\n")
# 1) il mercato dopo il diploma, sul PoolManager
vol=0.0; n=0
for b in range(ult-FIN, ult, PASSO):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        vol+=abs(s256(L["data"][2:][0:64]))/1e18; n+=1
print(f"   DOPO il diploma (PoolManager): {n:,} scambi, {vol:,.2f} ETH = {vol*ETH:,.0f} EUR/ora")
print(f"      -> {vol*ETH*24:,.0f} EUR al giorno di volume")
for q,et in ((0.01,"1,00%"),(0.003,"0,30%"),(0.0015,"0,15% (app che instrada)")):
    print(f"      chi prende il {et:<26} {vol*ETH*24*q:>9,.0f} EUR/giorno")
# 2) la curva, sul contratto di Pons
vol2=0.0; n2=0
for b in range(ult-FIN, ult, PASSO):
    for L in rpc("eth_getLogs",[{"address":HOOK,"topics":[PRINC],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        d=L["data"][2:]; n2+=1
        # prima parola plausibile come importo nativo
        for i in range(0, min(len(d),64*4), 64):
            v=abs(s256(d[i:i+64]))/1e18
            if 1e-6 < v < 1000: vol2+=v; break
print(f"\n   SULLA CURVA (contratto Pons): {n2:,} eventi, ~{vol2:,.2f} ETH = {vol2*ETH:,.0f} EUR/ora")
print(f"      -> ~{vol2*ETH*24:,.0f} EUR al giorno di volume")
print(f"      chi prende l'1,00% (il locale):   {vol2*ETH*24*0.01:>9,.0f} EUR/giorno")
print("\n   NB: sulla curva l'importo e' dedotto dalla prima parola plausibile:")
print("       ordine di grandezza, non contabilita'.")
