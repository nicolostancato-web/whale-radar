#!/usr/bin/env python3
"""
analyze.py — I 5 TEST RIGOROSI sul dataset raccolto (tutto offline, veloce, ripetibile).
1) campione grande  2) persistenza (2 meta temporali)  3) slippage reale  4) filtro whale-vera
5) simulazione della strategia di Nicolo (entri, tieni, scale-out) net dei costi.
"""
import json, statistics as st, os
D = json.load(open("data/dataset.json"))
print(f"pool nel dataset: {len(D)} | candele totali: {sum(len(v.get('ohlcv',[])) for v in D.values()):,}\n")

SPIKE = 5.0          # volume candela > 5x mediana
WHALE_USD = 15000    # volume assoluto della candela-spike >= $15k -> proxy "whale vera compra forte"
FEE_RT = 0.02        # fee DEX round-trip ~2% (1% x2, tipico su questi pool memecoin)

def detect_events(min_abs_vol=0):
    ev = []
    for addr, p in D.items():
        c = p.get("ohlcv", [])
        if len(c) < 80: continue
        vols = [x[5] for x in c if x[5] > 0]
        if len(vols) < 40: continue
        medv = st.median(vols)
        if medv <= 0: continue
        liq = p.get("liq", 0) or 0
        for k in range(len(c) - 4):
            ts,o,hi,lo,cl,v = c[k]
            if v > SPIKE*medv and cl > o and cl > 0 and v >= min_abs_vol:
                path = [c[k+j][4] for j in range(1, 73) if k+j < len(c) and c[k+j][4] > 0]
                if len(path) < 6: continue
                ev.append({"ts": ts, "entry": cl, "path": path, "liq": liq, "spikevol": v})
    return ev

def fwd_stats(ev, label):
    def at(h): return [e["path"][h-1]/e["entry"]-1 for e in ev if len(e["path"])>=h]
    print(f"--- {label} (n={len(ev)}) ---")
    for h in (6,24,72):
        r = at(h)
        if not r: continue
        print(f"  +{h:>2}h: mediana {st.median(r)*100:+6.1f}%  media {sum(r)/len(r)*100:+7.1f}%  positivi {sum(1 for x in r if x>0)/len(r)*100:3.0f}%  (n={len(r)})")
    rmax = [max(e["path"])/e["entry"]-1 for e in ev]
    print(f"  picco72h: mediana {st.median(rmax)*100:+.1f}%  media {sum(rmax)/len(rmax)*100:+.1f}%")

# ===== 1) CAMPIONE GRANDE =====
ev_all = detect_events()
print("="*66); print("[1] CAMPIONE GRANDE — segnale 'spike volume' (proxy generico)"); print("="*66)
fwd_stats(ev_all, "tutti gli spike")

# ===== 4) FILTRO WHALE VERA (volume assoluto alto) =====
ev_whale = detect_events(min_abs_vol=WHALE_USD)
print("\n"+"="*66); print(f"[4] FILTRO WHALE VERA — spike con volume >= ${WHALE_USD:,} (compra forte)"); print("="*66)
fwd_stats(ev_whale, "solo whale forti")

# ===== 2) PERSISTENZA (2 meta temporali) sul set whale =====
print("\n"+"="*66); print("[2] PERSISTENZA — regge in entrambe le meta' del tempo?"); print("="*66)
if ev_whale:
    tmed = st.median([e["ts"] for e in ev_whale])
    fwd_stats([e for e in ev_whale if e["ts"] < tmed], "1a meta")
    fwd_stats([e for e in ev_whale if e["ts"] >= tmed], "2a meta")

# ===== 3) SLIPPAGE + 5) STRATEGIA SCALE-OUT (net costi) =====
def simulate(ev, pos_usd, label):
    """Strategia Nicolo: entri pos_usd, scale-out 25% a +30/+80/+180%, resto a fine 72h. Net fee+impact."""
    LADDER = [(0.30,0.25),(0.80,0.25),(1.80,0.25)]  # (soglia_ret, frazione)
    rets=[]
    for e in ev:
        liq=max(e["liq"],1)
        entry_imp = pos_usd/liq
        # esci: per ogni tranche, prezzo target; impatto uscita su liq (tranche piccola)
        remaining=1.0; realized=0.0
        peak_path=e["path"]
        hit={}
        for thr,frac in LADDER:
            # trova se il path tocca la soglia
            target=e["entry"]*(1+thr)
            if any(px>=target for px in peak_path):
                exit_imp=(pos_usd*frac)/(liq*0.7)
                realized += frac*( (1+thr)*(1-exit_imp) )
                remaining-=frac
        # il resto venduto a fine finestra (ultimo prezzo)
        end_ret=peak_path[-1]/e["entry"]
        exit_imp=(pos_usd*remaining)/(liq*0.7)
        realized += remaining*( end_ret*(1-exit_imp) )
        # applica fee entrata+uscita e impatto entrata
        net = realized*(1-FEE_RT)*(1-entry_imp) - 1
        rets.append(net)
    med=st.median(rets); mean=sum(rets)/len(rets); pos=sum(1 for x in rets if x>0)/len(rets)
    print(f"  {label}: pos ${pos_usd} -> per-trade mediana {med*100:+.1f}%  media {mean*100:+.1f}%  win {pos*100:.0f}%  | PORTAFOGLIO (media di {len(rets)} bet) = {mean*100:+.1f}%")
    return mean

print("\n"+"="*66); print("[3+5] SLIPPAGE REALE + STRATEGIA SCALE-OUT (entri/tieni/prendi profitto)"); print("="*66)
print("Su tutti gli spike:")
for size in (200, 1000, 5000): simulate(ev_all, size, "tutti")
print("Solo whale forti:")
for size in (200, 1000, 5000): simulate(ev_whale, size, "whale")
print("\nNOTA: 'PORTAFOGLIO' = se entri quella size su OGNI segnale e fai scale-out. Net di fee 2% + slippage.")
