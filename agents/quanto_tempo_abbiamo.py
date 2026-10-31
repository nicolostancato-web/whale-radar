"""Quanto tempo passa fra l'avviso e il blocco? E' LA misura che decide.

Se dall'avviso su MEV-Share al momento in cui la transazione finisce in un
blocco passano due secondi, possiamo starci. Se ne passano due decimi, no.

Metodo: si ascolta il flusso, si segna l'ORA di ogni avviso, e poi si
guarda in quale blocco e' finita quella transazione e QUANDO quel blocco e'
stato prodotto. La differenza e' il tempo che avremmo per reagire.
"""
import json, time, urllib.request, threading, collections, statistics as st
U="https://ethereum-rpc.publicnode.com"
def rpc(m,p,giri=3):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=20))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.3*(g+1))
    return None
visti={}   # hash -> ora dell'avviso
MINUTI=3
print(f"   ascolto gli avvisi per {MINUTI} minuti, segnando l'ora di ciascuno...")
t0=time.time()
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
            h=d.get("hash")
            if h and h not in visti: visti[h]=time.time()
except Exception as e:
    print(f"   flusso interrotto: {str(e)[:50]}")
print(f"   {len(visti)} avvisi raccolti\n")
# LA CORREZIONE: cercavo subito, ma una transazione annunciata ha bisogno
# di tempo per finire in un blocco ED essere indicizzata. 0 su 40 non
# significava «non atterrano»: significava «ho guardato troppo presto».
print("   aspetto 90 secondi che atterrino e vengano indicizzate...")
time.sleep(90)
print("   ora cerco in quale blocco sono finite e quando...")
camp=list(visti.items())[:40]
ritardi=[]; nontrovate=0
for h,ora in camp:
    rc=rpc("eth_getTransactionReceipt",[h])
    if not rc: nontrovate+=1; continue
    bl=rpc("eth_getBlockByNumber",[rc["blockNumber"], False])
    if not bl: nontrovate+=1; continue
    t_blocco=int(bl["timestamp"],16)
    ritardi.append(t_blocco - ora)
    time.sleep(0.1)
print(f"   {len(ritardi)} trovate in un blocco, {nontrovate} no\n")
if ritardi:
    ritardi.sort()
    print(f"   TEMPO FRA AVVISO E BLOCCO (secondi):")
    print(f"      mediana {st.median(ritardi):.2f}")
    print(f"      il 25% piu' stretto  {ritardi[len(ritardi)//4]:.2f}")
    print(f"      il 25% piu' largo    {ritardi[3*len(ritardi)//4]:.2f}")
    print(f"      minimo {min(ritardi):.2f}   massimo {max(ritardi):.2f}")
    buoni=sum(1 for x in ritardi if x>=1.0)
    print(f"\n   avvisi con almeno 1 secondo di anticipo: "
          f"{buoni}/{len(ritardi)} ({buoni/len(ritardi)*100:.0f}%)")
    print(f"   -> {'CI STIAMO: c e tempo per reagire' if st.median(ritardi)>=1 else 'troppo stretto'}")
