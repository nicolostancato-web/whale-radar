"""Quale delle firme rare e' il diploma? Quella che cade NELLO STESSO BLOCCO in
cui nasce un pool: il diploma e' la nascita del pool definitivo.
Si guarda su una finestra larga, perche' con due eventi in mezz'ora non si
decide niente (lezione: una cella con due soggetti non e' una misura).
"""
import json, urllib.request, collections
RPC="https://rpc.mainnet.chain.robinhood.com"
FAB="0x7ed598bcef8bd9edd8c97a195c6d13f40801ec7e"; HOOK="0xe5e702641ea86f4ae6cc3cdaed2b886f976be044"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
RARE={"0x308c390ed1ab5873392818e036cabdf408bc8ad042fbaead3108954ff75ba980":"fab-308c",
      "0xcdb72f157fd3666758a6ce201387ffb52038c7562e4fff352828da1096c4b6b4":"fab-cdb7",
      "0xa0a18f5bf205becee8b268d7cf69addab8548ae8ef361791464cf0e0e17c1361":"fab-a0a1",
      "0x0a44ef75df69c534f43cd6c1aa3ef8983065fe5fe79ef9e79f6494e6f258c259":"fab-0a44",
      "0x01bf263a1db1652580721573296e1a1fa70b3d4c87f61d02a69c4e1109d2d573":"hook-01bf",
      "0x2f3c43579b9064b6f28edcf41608f3815792d274a56afe024359703cb4ea9b30":"hook-2f3c"}
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None

ult=int(rpc("eth_blockNumber",[]),16); FIN=60000; PASSO=1000   # passo largo: i log filtrati per indirizzo sono pochi
nascite={}; evt=collections.defaultdict(list)
for b in range(ult-FIN, ult, PASSO):
    a=hex(min(b+PASSO-1,ult))
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],"fromBlock":hex(b),"toBlock":a}]) or []:
        nascite[int(L["blockNumber"],16)] = L["topics"][1]
    for ind in (FAB,HOOK):
        for L in rpc("eth_getLogs",[{"address":ind,"fromBlock":hex(b),"toBlock":a}]) or []:
            t=L["topics"][0]
            if t in RARE: evt[t].append(int(L["blockNumber"],16))
ore=FIN*0.093/3600
print(f"finestra ~{ore:.1f} ore | nascite di pool: {len(nascite)}\n")
print("   firma        eventi   /giorno   nello stesso blocco di una nascita")
for t,bl in sorted(evt.items(), key=lambda x:len(x[1])):
    ins=sum(1 for b in bl if b in nascite)
    print(f"   {RARE[t]:<11} {len(bl):>6}   {len(bl)/ore*24:>7.0f}   {ins}/{len(bl)}"
          + ("   <-- IL DIPLOMA" if bl and ins/len(bl)>0.8 else ""))
