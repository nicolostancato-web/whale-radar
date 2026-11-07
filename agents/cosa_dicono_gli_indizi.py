"""Cosa rivelano davvero gli indizi su un aggiornamento di prezzo?

Chi manda una transazione privata sceglie quanto mostrare. Se l'indizio
include il NUOVO PREZZO, si puo' calcolare in anticipo quali posizioni
cadono. Se lo nasconde, si puo' comunque tentare alla cieca: nei pacchetti
Flashbots una transazione che si annulla NON viene inclusa e non costa
nulla, e il nostro contratto si annulla gia' da solo se non c'e' guadagno.
"""
import json, time, urllib.request, sys
sys.path.insert(0,"agents")
from keccak import firma
AU=firma("AnswerUpdated(int256,uint256,uint256)").lower()
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
print("   cerco indizi di aggiornamento prezzo o di Aave (3 minuti)...\n")
t0=time.time(); trovati=0
try:
    r=urllib.request.Request("https://mev-share.flashbots.net",
        headers={"user-agent":"Mozilla/5.0","accept":"text/event-stream"})
    with urllib.request.urlopen(r, timeout=30) as f:
        while time.time()-t0 < 180 and trovati < 4:
            l=f.readline()
            if not l: break
            s=l.decode("utf-8","ignore").strip()
            if not s.startswith("data:"): continue
            try: d=json.loads(s[5:])
            except Exception: continue
            rilev=False
            for lg in d.get("logs") or []:
                if (lg.get("address") or "").lower()==POOL: rilev=True
                for t in (lg.get("topics") or []):
                    if t.lower()==AU: rilev=True
            if not rilev: continue
            trovati+=1
            print(f"   --- indizio {trovati}")
            print(f"       chiavi presenti: {sorted(d.keys())}")
            for k in ("hash","txs","mevGasPrice","gasUsed"):
                if k in d: print(f"       {k}: {str(d[k])[:90]}")
            for lg in (d.get("logs") or [])[:2]:
                print(f"       log su {lg.get('address')}")
                print(f"          firme: {[t[:14]+'..' for t in (lg.get('topics') or [])]}")
                dd=lg.get("data")
                print(f"          dati: {'PRESENTI ('+str(len(dd))+' car)' if dd and dd!='0x' else 'NASCOSTI'}")
except Exception as e:
    print(f"   interrotto: {str(e)[:60]}")
print(f"\n   trovati {trovati} indizi rilevanti")
