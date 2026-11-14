#!/usr/bin/env python3
"""WATCHDOG — controlla che l'ACCUMULATOR giri. Se fermo da >2.5h -> allarme (workflow fallisce -> GitHub manda email al founder). Scrive data/results/health.json. Costo €0."""
import json, os, time, sys
NOW=int(time.time())
os.makedirs("data/results", exist_ok=True)
p = "data/state/paper_state.json" if os.path.exists("data/state/paper_state.json") else "data/paper_state.json"
try:
    d=json.load(open(p))
    last=d.get("last_run",0); age=(NOW-last)/60
    health={"ts":NOW,"last_run":last,"age_min":round(age),"n_open":len(d.get("open",[])),
            "n_closed":len(d.get("closed",[])),"runs":d.get("runs"),"status":"OK" if age<=150 else "STALE"}
    json.dump(health, open("data/results/health.json","w"))
    if age>150:
        print(f"🚨 ALLARME: accumulator fermo da {age:.0f} min (>2.5h)!"); sys.exit(1)
    print(f"✅ salute OK | accumulator {age:.0f} min fa | aperte {health['n_open']} | chiuse {health['n_closed']} | run {health['runs']}")
except Exception as e:
    print("🚨 watchdog: stato illeggibile:", str(e)); sys.exit(1)
