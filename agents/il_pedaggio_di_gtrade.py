"""Quanto costa un giro su gTrade? E' il numero che ha ucciso 15 strade.

Si prende una transazione che paga GovFeeCharged e si guardano TUTTI i suoi
eventi e i trasferimenti di collaterale: la commissione e' nota, la taglia
della posizione si ricava dal movimento di USDC verso/da il diamante.
Rapporto fra i due = il pedaggio in percentuale.
Niente assunzioni sulla tariffa pubblicata: si misura.
"""
import sys, json, urllib.request, collections, statistics as st
sys.path.insert(0,"agents"); from keccak import keccak256
RPC="https://arb1.arbitrum.io/rpc"; D="0xff162c694eaa571f685030649814282ea457f169"
USDC="0xaf88d065e77c8cc2239327c5edb3a432268e5831"   # USDC nativo Arbitrum (da verificare sotto)
GOV="0x"+keccak256(b"GovFeeCharged(address,uint8,uint256)").hex()
TRASF="0x"+keccak256(b"Transfer(address,address,uint256)").hex()
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
# il collaterale 3 l'ha gia' dichiarato il contratto: lo ri-leggo per averne l'indirizzo
r=rpc("eth_call",[{"to":D,"data":sel("getCollateral(uint8)")+(3).to_bytes(32,'big').hex()},"latest"])
USDC="0x"+r[2:66][-40:] if r else USDC
print(f"collaterale 3 = {USDC}  ({testo(rpc('eth_call',[{'to':USDC,'data':sel('symbol()')},'latest']))})")
ult=int(rpc("eth_blockNumber",[]),16)
tx=[]
for b in range(ult-30000, ult, 4000):
    r=rpc("eth_getLogs",[{"address":D,"topics":[GOV],"fromBlock":hex(b),"toBlock":hex(min(b+3999,ult))}])
    if isinstance(r,list):
        tx += [(x["transactionHash"], int(x["data"],16)) for x in r if int(x["topics"][2],16)==3]
tx=list(dict.fromkeys(tx))
print(f"{len(tx)} transazioni con commissione in USDC | ne leggo 40\n")
rapporti=[]
for h,fee in tx[:40]:
    r=rpc("eth_getTransactionReceipt",[h])
    if not r: continue
    mosse=[]
    for L in r["logs"]:
        if L["address"].lower()!=USDC.lower() or not L.get("topics"): continue
        if L["topics"][0]!=TRASF or len(L["topics"])<3: continue
        try: v=int(L["data"],16)/1e6
        except Exception: continue
        mosse.append(v)
    if not mosse: continue
    taglia=max(mosse)
    if taglia<=0: continue
    rapporti.append((fee/1e6)/taglia)
if rapporti:
    rapporti.sort()
    print(f"   {len(rapporti)} giri misurati")
    print(f"   commissione di governance / taglia della posizione:")
    print(f"      mediana {st.median(rapporti)*100:.4f}%   quartili "
          f"{rapporti[len(rapporti)//4]*100:.4f}% / {rapporti[3*len(rapporti)//4]*100:.4f}%")
    print("\n   NB: e' SOLO la voce 'governance'. Il pedaggio totale include")
    print("       spread, commissione di apertura/chiusura e costo di mantenimento.")
