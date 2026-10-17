#!/usr/bin/env python3
"""
validate_unbiased.py — TEST IMPARZIALE dell'edge (niente survivorship).
Invece di partire dai token che le whale TENGONO ora (vincitori), campiona TANTI token della chain
e misura cosa succede dopo OGNI grande spike di volume/acquisto — su vincenti E perdenti.
Stack gratis: GeckoTerminal (lista pool + OHLCV storico). Proxy di "entrata whale" = candela con
volume >> mediana e verde (forte acquisto). Onesto: include i token che poi sono crollati.
"""
import urllib.request, json, time, statistics as st
GT = "https://api.geckoterminal.com/api/v2"
def get(url):
    last=None
    for a in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}), timeout=30))
        except Exception as e: last=e; time.sleep(0.8*(a+1))
    raise last

# 1) prendi TANTI pool della chain (non solo i trending di oggi -> più pagine = più varietà, anche faded)
pools=[]
for pg in range(1,7):
    try:
        d=get(f"{GT}/networks/robinhood/pools?page={pg}")
        for p in d.get("data",[]):
            a=p.get("attributes",{})
            pools.append({"addr":a.get("address"), "name":a.get("name"), "vol":float(a.get("volume_usd",{}).get("h24") or 0)})
        time.sleep(2.1)  # rate-limit friendly
    except Exception as e:
        print("pool pg err", pg, str(e)[:60]); break
# dedup
seen=set(); pools=[p for p in pools if p["addr"] and not (p["addr"] in seen or seen.add(p["addr"]))]
print(f"pool campionati: {len(pools)}")

SPIKE=5.0        # volume candela > 5x mediana = grande acquisto
FWD=[6,24,72]    # ore forward
events=[]
for i,p in enumerate(pools):
    try:
        d=get(f"{GT}/networks/robinhood/pools/{p['addr']}/ohlcv/hour?aggregate=1&limit=1000")
        c=sorted(d.get("data",{}).get("attributes",{}).get("ohlcv_list",[]))  # [ts,o,h,l,c,v]
    except: continue
    if len(c)<80: continue
    vols=[x[5] for x in c if x[5]>0]
    if len(vols)<40: continue
    medv=st.median(vols)
    if medv<=0: continue
    idx={x[0]:k for k,x in enumerate(c)}
    for k in range(len(c)-max(FWD)-1):
        ts,o,hi,lo,cl,v = c[k]
        if v > SPIKE*medv and cl>o and cl>0:   # spike di volume + verde = forte acquisto
            ev={"tok":p["name"][:16], "entry":cl}
            ok=True
            for h in FWD:
                fk=k+h
                if fk<len(c) and c[fk][4]>0: ev[f"r{h}"]=c[fk][4]/cl-1
                else: ok=False
            # max nelle 72h
            window=[c[k+j][4] for j in range(1,73) if k+j<len(c) and c[k+j][4]>0]
            ev["rmax"]=max(window)/cl-1 if window else 0
            if ok: events.append(ev)
    time.sleep(2.1)
    if (i+1)%20==0: print(f"  ...{i+1} pool, {len(events)} eventi")

print("\n"+"="*64)
print(f"EVENTI 'grande acquisto' misurati (imparziale, tutti i token): {len(events)}")
if events:
    for h in FWD:
        rr=[e[f"r{h}"] for e in events if f"r{h}" in e]
        print(f"  +{h:>2}h: mediana {st.median(rr)*100:+6.1f}%  media {sum(rr)/len(rr)*100:+7.1f}%  positivi {sum(1 for x in rr if x>0)/len(rr)*100:3.0f}%  (n={len(rr)})")
    rm=[e["rmax"] for e in events]
    print(f"  picco max 72h: mediana {st.median(rm)*100:+.1f}%  media {sum(rm)/len(rm)*100:+.1f}%")
    print(f"\n  >>> Se entri a OGNI grande acquisto e prendi profitto al picco: media +{sum(rm)/len(rm)*100:.0f}%")
    print(f"  >>> Ma la MEDIANA (il caso tipico) a +24h dice la verità onesta: {st.median([e['r24'] for e in events if 'r24' in e])*100:+.1f}%")
    # salva
    json.dump(events, open("data/unbiased_events.json","w")) if __import__("os").path.isdir("data") else None
