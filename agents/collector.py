#!/usr/bin/env python3
"""
COLLECTOR UNICO E PACATO — storage ROBUSTO (file immutabili per giro, mai append su file condiviso).
Accumula STORICO seriale (niente 429): per ~150 pool (top volume), UNO alla volta con pausa 2.6s:
  - candele DAILY (1000gg ~3 anni) + ORARIE (~40gg)  -> data/raw/candles/run_<ts>.jsonl.gz (NUOVO ogni giro)
  - whale-buy >= $10k (wallet+$) + PRESSIONE buy/sell -> data/raw/whales/run_<ts>.jsonl.gz
Dedup scandendo i file esistenti. Resumable (checkpoint). Compresso. Gratis. NO live.
IMPORTANTE: un file scritto UNA volta e chiuso -> impossibile corromperlo (bug precedente: writer concorrenti su .gz condiviso).
"""
import urllib.request, json, time, os, gzip, glob
GT="https://api.geckoterminal.com/api/v2"; PAUSE=2.6; WHALE=10000; NPOOL=150
CK="data/collector_checkpoint.json"
def get(url):
    last=None
    for a in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}), timeout=35))
        except Exception as e: last=e; time.sleep(4.0*(a+1))
    raise last

os.makedirs("data/raw/candles", exist_ok=True); os.makedirs("data/raw/whales", exist_ok=True)
ck=json.load(open(CK)) if os.path.exists(CK) else {}
now=int(time.time())

def load_keys(folder, keyfn):
    keys=set()
    for f in glob.glob(f"{folder}/*.jsonl.gz"):
        try:
            for l in gzip.open(f,"rt"):
                if l.strip():
                    try: keys.add(keyfn(json.loads(l)))
                    except: pass
        except EOFError: pass
    return keys
seen_c=load_keys("data/raw/candles", lambda d: f"{d['pool']}_{d['ts']}_{d['tf']}")
seen_w=load_keys("data/raw/whales", lambda d: d.get("tx"))
print(f"gia' in archivio: {len(seen_c)} candele, {len(seen_w)} whale/press")

# top pool per volume (pacato)
pools=[]
for pg in range(1,10):
    try:
        d=get(f"{GT}/networks/robinhood/pools?page={pg}"); rows=d.get("data",[])
        if not rows: break
        for p in rows:
            a=p.get("attributes",{})
            pools.append({"addr":a.get("address"),"name":a.get("name"),"vol":float((a.get("volume_usd") or {}).get("h24") or 0)})
        time.sleep(PAUSE)
    except Exception as e: print(f"pool pg{pg} {str(e)[:30]}"); break
pools=sorted([p for p in pools if p["addr"]], key=lambda x:-x["vol"])[:NPOOL]
print(f"pool da processare: {len(pools)}", flush=True)

# FILE NUOVI di questo giro (immutabili)
cf=f"data/raw/candles/run_{now}.jsonl.gz"; wf=f"data/raw/whales/run_{now}.jsonl.gz"
fc=gzip.open(cf,"wt"); fw=gzip.open(wf,"wt")
nc=nw=0
for i,p in enumerate(pools):
    addr=p["addr"]
    if now-ck.get(addr,0) < 20*3600: continue
    for tf in ("day","hour"):
        try:
            d=get(f"{GT}/networks/robinhood/pools/{addr}/ohlcv/{tf}?aggregate=1&limit=1000")
            c=d.get("data",{}).get("attributes",{}).get("ohlcv_list",[]); time.sleep(PAUSE)
        except: continue
        for x in c:
            sid=f"{addr}_{int(x[0])}_{tf}"
            if sid in seen_c: continue
            seen_c.add(sid); nc+=1
            fc.write(json.dumps({"pool":addr,"tf":tf,"ts":int(x[0]),"o":x[1],"h":x[2],"l":x[3],"cl":x[4],"v":round(x[5])})+"\n")
    try:
        d=get(f"{GT}/networks/robinhood/pools/{addr}/trades"); tr=d.get("data",[]); time.sleep(PAUSE)
    except: tr=[]
    buyv=sellv=0.0
    for t in tr:
        a=t.get("attributes",{}); usd=float(a.get("volume_in_usd") or 0)
        if a.get("kind")=="buy": buyv+=usd
        elif a.get("kind")=="sell": sellv+=usd
        tx=a.get("tx_hash")
        if a.get("kind")=="buy" and usd>=WHALE and tx and tx not in seen_w:
            seen_w.add(tx); nw+=1
            fw.write(json.dumps({"tx":tx,"ts":a.get("block_timestamp"),"pool":addr,"name":p["name"],
                                 "wallet":a.get("tx_from_address"),"usd":round(usd)})+"\n")
    if buyv+sellv>0:
        fw.write(json.dumps({"tx":f"press_{addr}_{now}","ts":now,"pool":addr,"kind":"pressure",
                             "buy":round(buyv),"sell":round(sellv),"ratio":round(buyv/(sellv or 1),2)})+"\n")
    ck[addr]=now
    if (i+1)%10==0: json.dump(ck,open(CK,"w")); print(f"  ...{i+1}/{len(pools)} | +{nc} candele +{nw} whale", flush=True)
fc.close(); fw.close(); json.dump(ck,open(CK,"w"))
# se il giro non ha prodotto nulla, togli i file vuoti
if nc==0: os.remove(cf)
if nw==0: os.remove(wf)
tot_c=len(seen_c); tot_w=len(seen_w)
print(f"\n✅ +{nc} candele +{nw} whale | ARCHIVIO totale: {tot_c:,} candele, {tot_w:,} whale/press", flush=True)
