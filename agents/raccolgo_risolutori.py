"""Raccoglitore: guadagno vero dei risolutori UniswapX, accumulato a ogni giro.

Vincolo scoperto: l'RPC tiene lo stato storico solo per ~5.000-20.000 blocchi
(8-30 minuti). Quindi ogni giro puo' misurare solo i riempimenti recentissimi,
e il campione si costruisce nel tempo. Scrive una riga per riempimento.

Perche' serve il saldo NATIVO: l'ether non emette un evento di trasferimento,
e contando solo gli ERC20 si vedono le uscite del risolutore ma non i suoi
incassi (0 positivi su 42: referto di guasto, non risultato).
"""
# SPENTO il 24/10. Non per stanchezza: per aritmetica.
#  - il mercante: scarto 30 punti per posizione, servirebbero ~14.000 posizioni
#    per distinguere lo 0,6% cercato. Con 200 l'intervallo e' +/-4,2%: il test
#    NON PUO' concludere. E la strada e' gia' chiusa per altra via (concentrata
#    -2,9% +/- 0,4).
#  - i risolutori UniswapX: la torta intera della chain e' ~40 EUR al giorno.
# Tenere in piedi una misura su una strada chiusa non e' prudenza: e' lavoro
# che si autoalimenta. Se la strada riapre, si riaccende togliendo questo blocco.
import sys as _sys
print("SPENTO: vedi la nota in cima al file"); _sys.exit(0)


import json, os, urllib.request, collections, statistics as st
RPC="https://rpc.mainnet.chain.robinhood.com"
FILL="0x78ad7ec0e9f89e74012afa58738b6b661c024cb0fd185ee2f616c0a28924bd66"
TRASF="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
USDG="0x5fc5360d0400a0fd4f2af552add042d716f1d168"; WETH="0x0bd7d308f8e1639fab988df18a8011f41eacad73"
DEC={USDG:6, WETH:18}; EUR={USDG:0.92, WETH:3030.0}; ETH_EUR=3030.0
FUORI="data/multichain/robinhood/risolutori.jsonl"; VISTI="data/multichain/robinhood/risolutori_visti.json"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
visti=set(json.load(open(VISTI))) if os.path.exists(VISTI) else set()
ult=int(rpc("eth_blockNumber",[]),16)
fills=[]
for b in range(ult-4500, ult, 1500):
    for L in rpc("eth_getLogs",[{"topics":[FILL],"fromBlock":hex(b),"toBlock":hex(min(b+1499,ult))}]) or []:
        if len(L["topics"])>2 and L["transactionHash"] not in visti:
            fills.append((L["transactionHash"], "0x"+L["topics"][2][-40:], int(L["blockNumber"],16)))
nuovi=0
for h,solver,bn in fills:
    visti.add(h)
    r=rpc("eth_getTransactionReceipt",[h])
    pri=rpc("eth_getBalance",[solver,hex(bn-1)]); dopo=rpc("eth_getBalance",[solver,hex(bn)])
    if not r or not isinstance(pri,str) or not isinstance(dopo,str): continue
    d_nat=(int(dopo,16)-int(pri,16))/1e18*ETH_EUR
    netto=collections.Counter()
    for L in r["logs"]:
        if not L.get("topics") or L["topics"][0]!=TRASF or len(L["topics"])<3: continue
        tok=L["address"].lower(); da="0x"+L["topics"][1][-40:]; a="0x"+L["topics"][2][-40:]
        try: v=int(L["data"],16)
        except Exception: continue
        if da==solver or a==solver: netto[tok]+= v if a==solver else -v
    resid=[t for t,v in netto.items() if t not in DEC and abs(v)>0]
    erc=sum(v/10**DEC[t]*EUR[t] for t,v in netto.items() if t in DEC)
    with open(FUORI,"a") as f:
        f.write(json.dumps({"tx":h,"solver":solver,"eur":round(d_nat+erc,4),
                            "magazzino": bool(resid)})+"\n")
    nuovi+=1
json.dump(sorted(visti), open(VISTI,"w"))
print(f"nuovi riempimenti misurati: {nuovi}")
if os.path.exists(FUORI):
    r=[json.loads(x) for x in open(FUORI)]
    puliti=[x["eur"] for x in r if not x["magazzino"]]
    print(f"TOTALE: {len(r)} riempimenti | senza magazzino: {len(puliti)}")
    if len(puliti)>1:
        print(f"   guadagno: mediana {st.median(puliti):+.4f} EUR | media {st.mean(puliti):+.4f}"
              f" | positivi {sum(1 for x in puliti if x>0)}/{len(puliti)}")
