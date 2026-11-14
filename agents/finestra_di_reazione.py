"""Quanto tempo abbiamo per reagire a un avviso?

Gli hash di MEV-Share non sono transazioni pubbliche (sono riferimenti
interni: si costruisce il pacchetto scrivendo «dopo quel riferimento»).
Quindi il tempo si misura cosi': quando arriva un avviso, quanto manca
alla chiusura del blocco in corso?

Su Ethereum i blocchi arrivano ogni 12 secondi a orario fisso. Se l'avviso
arriva a meta' slot abbiamo 6 secondi; se arriva sul filo, zero.
Un thread segue la testa della chain, l'altro ascolta gli avvisi.
"""
import json, time, urllib.request, threading, statistics as st
U="https://ethereum-rpc.publicnode.com"
stato={"blocco":0,"ora":0.0}
stop=False
def segui_testa():
    while not stop:
        try:
            c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            b=int(json.load(urllib.request.urlopen(r,timeout=8))["result"],16)
            if b>stato["blocco"]:
                stato["blocco"]=b; stato["ora"]=time.time()
        except Exception: pass
        time.sleep(0.4)
t=threading.Thread(target=segui_testa, daemon=True); t.start()
time.sleep(14)   # aspetta di vedere almeno un cambio di blocco
print(f"   testa della chain agganciata al blocco {stato['blocco']}\n")
MINUTI=4
finestre=[]
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
            ora=time.time()
            if stato["ora"]==0: continue
            da_inizio = ora - stato["ora"]       # da quando e' uscito l'ultimo blocco
            resta = 12.0 - da_inizio             # quanto manca al prossimo
            if -1 < resta < 13: finestre.append(resta)
except Exception as e:
    print(f"   flusso interrotto: {str(e)[:50]}")
stop=True
print(f"   {len(finestre)} avvisi misurati in {MINUTI} minuti\n")
if finestre:
    finestre.sort()
    print(f"   TEMPO CHE RESTA PRIMA DEL PROSSIMO BLOCCO (secondi):")
    print(f"      mediana {st.median(finestre):.2f}")
    print(f"      il quarto piu' stretto {finestre[len(finestre)//4]:.2f}")
    print(f"      il quarto piu' largo   {finestre[3*len(finestre)//4]:.2f}")
    for soglia in (0.5, 1.0, 2.0, 4.0):
        n=sum(1 for x in finestre if x>=soglia)
        print(f"      avvisi con almeno {soglia:.1f}s: {n}/{len(finestre)} "
              f"({n/len(finestre)*100:.0f}%)")
