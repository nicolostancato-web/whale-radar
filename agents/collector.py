#!/usr/bin/env python3
"""
COLLECTOR — BATCH PICCOLO, FAIL-FAST (adatto a GitHub Actions, niente run cancellati).
Ogni giro: processa max 25 pool (i piu' arretrati), veloce. Su tanti giri (ogni 4h) copre tutti i pool
e accumula lo storico. File IMMUTABILI per giro (no corruzione). Lista pool CACHATA (no 9 chiamate/giro).
Candele daily+orarie + whale $10k + pressione. Compresso, dedup, resumable. Gratis. NO live.
"""
import urllib.request, json, time, os, gzip, glob
GT="https://api.geckoterminal.com/api/v2"; PAUSE=2.6; WHALE=10000; BATCH=25
CK="data/collector_checkpoint.json"; POOLS="data/pools.json"
def get(url, tries=2):
    last=None
    for a in range(tries):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}), timeout=25))
        except Exception as e: last=e; time.sleep(2.0*(a+1))
    return None   # fail-fast: niente eccezione, il chiamante salta

os.makedirs("data/raw/candles", exist_ok=True); os.makedirs("data/raw/whales", exist_ok=True)
ck=json.load(open(CK)) if os.path.exists(CK) else {}
now=int(time.time())

# lista pool CACHATA (rinfresca ogni 24h)
pools=None
if os.path.exists(POOLS):
    pj=json.load(open(POOLS))
    if now-pj.get("ts",0) < 24*3600: pools=pj["pools"]
if pools is None:
    pools=[]
    for pg in range(1,10):
        d=get(f"{GT}/networks/robinhood/pools?page={pg}")
        if not d or not d.get("data"): break
        for p in d["data"]:
            a=p.get("attributes",{})
            pools.append({"addr":a.get("address"),"name":a.get("name"),"vol":float((a.get("volume_usd") or {}).get("h24") or 0)})
        time.sleep(PAUSE)
    pools=sorted([p for p in pools if p["addr"]], key=lambda x:-x["vol"])[:150]
    json.dump({"ts":now,"pools":pools}, open(POOLS,"w"))
print(f"pool in lista: {len(pools)}", flush=True)

# dedup dagli immutabili
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

# scegli i 25 pool piu' ARRETRATI (mai fatti o piu' vecchi)
todo=sorted(pools, key=lambda p: ck.get(p["addr"],0))[:BATCH]
cf=f"data/raw/candles/run_{now}.jsonl.gz"; wf=f"data/raw/whales/run_{now}.jsonl.gz"
fc=gzip.open(cf,"wt"); fw=gzip.open(wf,"wt"); nc=nw=0
for i,p in enumerate(todo):
    addr=p["addr"]
    for tf in ("day","hour"):
        d=get(f"{GT}/networks/robinhood/pools/{addr}/ohlcv/{tf}?aggregate=1&limit=1000")
        time.sleep(PAUSE)
        if not d: continue
        for x in d.get("data",{}).get("attributes",{}).get("ohlcv_list",[]):
            sid=f"{addr}_{int(x[0])}_{tf}"
            if sid in seen_c: continue
            seen_c.add(sid); nc+=1
            fc.write(json.dumps({"pool":addr,"tf":tf,"ts":int(x[0]),"o":x[1],"h":x[2],"l":x[3],"cl":x[4],"v":round(x[5])})+"\n")
    d=get(f"{GT}/networks/robinhood/pools/{addr}/trades"); time.sleep(PAUSE)
    tr=d.get("data",[]) if d else []
    buyv=sellv=0.0
    for t in tr:
        a=t.get("attributes",{}); usd=float(a.get("volume_in_usd") or 0)
        if a.get("kind")=="buy": buyv+=usd
        elif a.get("kind")=="sell": sellv+=usd
        tx=a.get("tx_hash")
        if a.get("kind")=="buy" and usd>=WHALE and tx and tx not in seen_w:
            seen_w.add(tx); nw+=1
            fw.write(json.dumps({"tx":tx,"ts":a.get("block_timestamp"),"pool":addr,"name":p["name"],"wallet":a.get("tx_from_address"),"usd":round(usd)})+"\n")
    if buyv+sellv>0:
        fw.write(json.dumps({"tx":f"press_{addr}_{now}","ts":now,"pool":addr,"kind":"pressure","buy":round(buyv),"sell":round(sellv),"ratio":round(buyv/(sellv or 1),2)})+"\n")
    ck[addr]=now
fc.close(); fw.close(); json.dump(ck,open(CK,"w"))
if nc==0: os.remove(cf)
if nw==0: os.remove(wf)
print(f"✅ batch {len(todo)} pool | +{nc} candele +{nw} whale | archivio: {len(seen_c):,} candele, {len(seen_w):,} whale/press", flush=True)
