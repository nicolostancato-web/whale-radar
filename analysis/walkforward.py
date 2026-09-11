#!/usr/bin/env python3
"""
walkforward.py — LA PROVA VERA, ADESSO (niente attesa di 2 settimane).
Test out-of-sample DENTRO la storia: alleno su un periodo, testo su un altro. + robustezza:
sotto-periodi (quarti), sensibilita' ai parametri. Se l'edge e' reale regge; se e' overfit, crolla.
Sul dataset gia' raccolto (data/dataset.json). Strategia scale-out net fee+slippage, size $200.
"""
import json, statistics as st
D = json.load(open("data/dataset.json"))
FEE_RT=0.02; NOTIONAL=200; LADDER=[(0.30,0.25),(0.80,0.25),(1.80,0.25)]

def events(spike=5.0):
    ev=[]
    for p in D.values():
        c=p.get("ohlcv",[]);
        if len(c)<80: continue
        vols=[x[5] for x in c if x[5]>0]
        if len(vols)<40: continue
        medv=st.median(vols); liq=p.get("liq",0) or 0
        if medv<=0: continue
        for k in range(len(c)-4):
            ts,o,hi,lo,cl,v=c[k]
            if v>spike*medv and cl>o and cl>0:
                path=[c[k+j][4] for j in range(1,73) if k+j<len(c) and c[k+j][4]>0]
                if len(path)>=6: ev.append({"ts":ts,"entry":cl,"path":path,"liq":liq})
    return ev

def portfolio(ev):
    """rendimento medio per-trade della strategia scale-out, net costi (size $200)."""
    if not ev: return None
    rets=[]
    for e in ev:
        liq=max(e["liq"],1); sold=0; realized=0
        for thr,frac in LADDER:
            if any(px>=e["entry"]*(1+thr) for px in e["path"]):
                exit_imp=(NOTIONAL*frac)/(liq*0.7); realized+=frac*((1+thr)*(1-exit_imp)); sold+=frac
        rem=1-sold; exit_imp=(NOTIONAL*rem)/(liq*0.7); realized+=rem*((e["path"][-1]/e["entry"])*(1-exit_imp))
        rets.append(realized*(1-FEE_RT)*(1-NOTIONAL/liq)-1)
    return {"n":len(rets),"mean":sum(rets)/len(rets),"median":st.median(rets),"win":sum(1 for x in rets if x>0)/len(rets)}

ev=events()
ev.sort(key=lambda e:e["ts"])
print(f"eventi totali: {len(ev)}\n")

# ===== WALK-FORWARD: primi 60% (train) vs ultimi 40% (test out-of-sample) =====
cut=ev[int(len(ev)*0.6)]["ts"]
tr=[e for e in ev if e["ts"]<cut]; te=[e for e in ev if e["ts"]>=cut]
print("="*60); print("[A] WALK-FORWARD (train 60% -> test 40% out-of-sample)"); print("="*60)
for lab,s in [("TRAIN (in-sample)",portfolio(tr)),("TEST  (OUT-OF-SAMPLE)",portfolio(te))]:
    if s: print(f"  {lab}: n={s['n']:>4}  portafoglio {s['mean']*100:+6.1f}%  mediana {s['median']*100:+.1f}%  win {s['win']*100:.0f}%")
print("  >>> se il TEST out-of-sample resta positivo = edge REALE (non overfit)")

# ===== ROBUSTEZZA: 4 quarti temporali =====
print("\n"+"="*60); print("[B] STABILITA' nei 4 quarti del tempo (ognuno deve tenere)"); print("="*60)
qs=[ev[i*len(ev)//4:(i+1)*len(ev)//4] for i in range(4)]
for i,q in enumerate(qs):
    s=portfolio(q)
    if s: print(f"  Q{i+1}: n={s['n']:>3}  portafoglio {s['mean']*100:+6.1f}%  win {s['win']*100:.0f}%")
print("  >>> se un quarto e' molto negativo = fragile / dipende da un periodo fortunato")

# ===== SENSIBILITA' AI PARAMETRI (non deve funzionare solo a un valore magico) =====
print("\n"+"="*60); print("[C] SENSIBILITA' alla soglia di spike (robusto = tiene su piu' valori)"); print("="*60)
for sp in (3.0,4.0,5.0,6.0,8.0):
    s=portfolio(events(spike=sp))
    if s: print(f"  spike {sp}x: n={s['n']:>4}  portafoglio {s['mean']*100:+6.1f}%  win {s['win']*100:.0f}%")
print("  >>> se funziona solo a spike=5 ed esplode altrove = overfit sospetto")
