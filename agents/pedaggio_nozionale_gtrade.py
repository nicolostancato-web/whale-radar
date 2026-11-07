"""IL PEDAGGIO VERO su gTrade, sul nozionale e non sul margine.

Errore corretto: avevo diviso la commissione per il MARGINE, ottenendo 7,2%
con una dispersione da 1,3% a 44,5% — la forma di una tariffa fissa vista
attraverso leve diverse.
La leva si legge dal contratto: getTrade(address,uint32), parola 3, precisione
1e3. Verifica che i campi siano quelli giusti: la parola 6 vale 3, e il
contratto dichiara separatamente che il collaterale 3 e' USDC. Coincidono.

pedaggio sul nozionale = commissione / (margine x leva)
"""
import sys, json, urllib.request, collections, statistics as st
sys.path.insert(0,"agents"); from keccak import keccak256
RPC="https://arb1.arbitrum.io/rpc"; D="0xff162c694eaa571f685030649814282ea457f169"
GOV="0x"+keccak256(b"GovFeeCharged(address,uint8,uint256)").hex()
TRASF="0x"+keccak256(b"Transfer(address,address,uint256)").hex()
USDC="0xaf88d065e77c8cc2239327c5edb3a432268e5831"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=45) as f: return json.load(f).get("result")
    except Exception: return None
def sel(s): return "0x"+keccak256(s.encode()).hex()[:8]
ult=int(rpc("eth_blockNumber",[]),16)
ev=[]
for b in range(ult-30000, ult, 4000):
    r=rpc("eth_getLogs",[{"address":D,"topics":[GOV],"fromBlock":hex(b),"toBlock":hex(min(b+3999,ult))}])
    if isinstance(r,list):
        ev += [(x["transactionHash"], "0x"+x["topics"][1][-40:], int(x["data"],16))
               for x in r if int(x["topics"][2],16)==3]
print(f"{len(ev)} commissioni in USDC | ne elaboro 45\n")
leve=[]; pedaggi=[]; senza=0
for h,trader,fee in ev[:45]:
    w=trader[2:].rjust(64,"0")
    res=rpc("eth_call",[{"to":D,"data":sel("getTrade(address,uint32)")+w+(0).to_bytes(32,'big').hex()},"latest"])
    if not res or len(res)<2+64*7: senza+=1; continue
    d=res[2:]
    lev=int(d[64*3:64*4],16)/1000.0
    if lev<=0: senza+=1; continue
    r2=rpc("eth_getTransactionReceipt",[h])
    if not r2: senza+=1; continue
    mosse=[int(L["data"],16)/1e6 for L in r2["logs"]
           if L.get("topics") and L["topics"][0]==TRASF and L["address"].lower()==USDC and len(L["topics"])>=3]
    if not mosse: senza+=1; continue
    margine=max(mosse)
    if margine<=0: senza+=1; continue
    leve.append(lev); pedaggi.append((fee/1e6)/(margine*lev))
if pedaggi:
    pedaggi.sort(); leve.sort()
    print(f"   {len(pedaggi)} giri misurati ({senza} scartati)")
    print(f"   leva: mediana {st.median(leve):.1f}x   da {min(leve):.1f}x a {max(leve):.1f}x")
    print(f"\n   COMMISSIONE DI GOVERNANCE SUL NOZIONALE:")
    print(f"      mediana {st.median(pedaggi)*100:.4f}%   quartili "
          f"{pedaggi[len(pedaggi)//4]*100:.4f}% / {pedaggi[3*len(pedaggi)//4]*100:.4f}%")
    print("\n   NB: e' una voce sola. Il pedaggio totale comprende anche spread,")
    print("       commissione di apertura/chiusura e costo di mantenimento.")
    print(f"   Per confronto: sulle monetine il pedaggio TOTALE era il 6%.")
