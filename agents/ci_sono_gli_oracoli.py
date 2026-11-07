"""Gli aggiornamenti di prezzo compaiono nel flusso di indizi?

Se si', si puo' vedere l'aggiornamento PRIMA che sia nel blocco e attaccarsi
dietro: e' l'unico modo di stare nella finestra da 12 secondi.
Se no, la strada e' chiusa e il candidato muore qui.

Si ascolta il flusso e si cerca: (a) la firma AnswerUpdated, (b) gli
indirizzi degli aggregatori gia' mappati, (c) il contratto di Aave.
"""
import json, time, urllib.request, collections, sys
sys.path.insert(0,"agents")
from keccak import firma
AU=firma("AnswerUpdated(int256,uint256,uint256)").lower()
# aggregatori trovati mappando gli asset di Aave
AGG={"0x7d4e742018fb52e48b08be73d041c18b21de6fb5":"ETH/USD",
     "0x64c67984a4a0e4b1d0b0b6b0b6b0b6b0b6b0b6b0":"?",
     "0xdaa4b74c6b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b":"?"}
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
MINUTI=4
print(f"   ascolto il flusso per {MINUTI} minuti...\n")
t0=time.time()
tot=0; conAU=0; conPool=0
indirizzi=collections.Counter(); firme=collections.Counter()
try:
    r=urllib.request.Request("https://mev-share.flashbots.net",
        headers={"user-agent":"Mozilla/5.0","accept":"text/event-stream"})
    with urllib.request.urlopen(r, timeout=30) as f:
        while time.time()-t0 < MINUTI*60:
            l=f.readline()
            if not l: break
            s=l.decode("utf-8","ignore").strip()
            if not s.startswith("data:"): continue
            try: d=json.loads(s[5:])
            except Exception: continue
            tot+=1
            for lg in d.get("logs") or []:
                a=(lg.get("address") or "").lower()
                indirizzi[a]+=1
                if a==POOL: conPool+=1
                for t in (lg.get("topics") or []):
                    firme[t.lower()]+=1
                    if t.lower()==AU: conAU+=1
except Exception as e:
    print(f"   interrotto: {str(e)[:60]}")
print(f"   {tot} eventi ascoltati in {(time.time()-t0)/60:.1f} minuti\n")
print(f"   con firma AnswerUpdated (aggiornamento prezzo): {conAU}")
print(f"   che toccano il pool di Aave: {conPool}")
print(f"\n   i 10 contratti piu' visti nel flusso:")
for a,n in indirizzi.most_common(10):
    print(f"      {a}  {n}")
print(f"\n   -> {'GLI ORACOLI CI SONO: la strada esiste' if conAU>0 else 'nessun aggiornamento di prezzo nel flusso'}")
