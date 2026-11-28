"""L'ascoltatore: prova a vuoto del liquidatore.

Mette insieme i tre pezzi e NON manda niente. Scrive solo cosa avrebbe
fatto, cosi' alla fine c'e' un registro che dice se saremmo arrivati in
tempo e quante occasioni vere avremmo intercettato.

  - un filo tiene aggiornata la lista corta (ogni 5 minuti)
  - un filo segue la testa della chain
  - il principale ascolta gli avvisi e, quando ne vede uno di
    aggiornamento prezzo, segna l'istante e le posizioni piu' vicine
  - dopo qualche blocco ricontrolla: quelle posizioni sono davvero cadute?
    e qualcuno le ha liquidate?

Nessuna chiave, nessun soldo, nessuna transazione.
"""
import json, os, time, threading, urllib.request, sys, collections
sys.path.insert(0,"agents")
from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
SEL=firma("getUserAccountData(address)")[2:10]
AU=firma("AnswerUpdated(int256,uint256,uint256)").lower()
U="https://ethereum-rpc.publicnode.com"
REG="data/liquidazioni/prova_a_vuoto.jsonl"
os.makedirs("data/liquidazioni", exist_ok=True)
stato={"blocco":0,"ora":0.0,"corta":[],"aggiornata":0}
stop=False
def rpc(m,p,giri=2,tout=12):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=tout))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.2*(g+1))
    return None
def salute(a):
    v=rpc("eth_call",[{"to":POOL,"data":"0x"+SEL+a[2:].zfill(64)},"latest"])
    if v and len(v)>=2+64*6:
        x=v[2:]
        return int(x[64:128],16)/1e8, int(x[320:384],16)/1e18
    return None
def segui_testa():
    while not stop:
        b=rpc("eth_blockNumber",[])
        if b:
            n=int(b,16)
            if n>stato["blocco"]: stato["blocco"]=n; stato["ora"]=time.time()
        time.sleep(0.5)
def tieni_lista():
    while not stop:
        try:
            c=json.load(open("data/liquidazioni/lista_corta.json"))
            c.sort(key=lambda x:x["salute"])
            stato["corta"]=[x for x in c if x["debito"]>1000][:40]
            stato["aggiornata"]=time.time()
        except Exception: pass
        time.sleep(300)
threading.Thread(target=segui_testa, daemon=True).start()
threading.Thread(target=tieni_lista, daemon=True).start()
time.sleep(10)
print(f"   testa al blocco {stato['blocco']} | lista corta: {len(stato['corta'])} posizioni")
MINUTI=int(sys.argv[1]) if len(sys.argv)>1 else 12
print(f"   prova a vuoto per {MINUTI} minuti. Non viene mandato nulla.\n")
t0=time.time(); avvisi=0; rilevanti=0; segnati=[]
ultimo_evento=time.time(); riconnessioni=0; permin=collections.Counter()
# UN ASCOLTATORE CHE SI FERMA IN SILENZIO E' PEGGIO DI NESSUNO (29/10):
# la prima versione ha raccolto 111 avvisi in 10 minuti invece di ~4.000,
# perche' il flusso si era bloccato e readline aspettava senza dirlo.
# Ora: se passano 20 secondi senza eventi, si riconnette.
while time.time()-t0 < MINUTI*60:
    try:
        r=urllib.request.Request("https://mev-share.flashbots.net",
            headers={"user-agent":"Mozilla/5.0","accept":"text/event-stream"})
        f=urllib.request.urlopen(r, timeout=25)
        import socket
        f.fp.raw._sock.settimeout(20)      # readline non resta appeso
        while time.time()-t0 < MINUTI*60:
            try:
                l=f.readline()
            except (socket.timeout, TimeoutError):
                print(f"   flusso fermo da 20s, riconnetto"); break
            if not l:
                print("   flusso chiuso, riconnetto"); break
            s_=l.decode("utf-8","ignore").strip()
            if not s_.startswith("data:"): continue
            try: d=json.loads(s_[5:])
            except Exception: continue
            avvisi+=1; ultimo_evento=time.time()
            permin[int((time.time()-t0)//60)]+=1
            prezzo=any(t.lower()==AU for lg in (d.get("logs") or [])
                       for t in (lg.get("topics") or []))
            if not prezzo: continue
            rilevanti+=1
            ora=time.time()
            resta=12.0-(ora-stato["ora"]) if stato["ora"] else None
            cand=[x["indirizzo"] for x in stato["corta"][:5]]
            segnati.append({"ora":ora,"blocco":stato["blocco"],
                            "secondi_disponibili":round(resta,2) if resta else None,
                            "candidati":cand})
            print(f"   avviso PREZZO al blocco {stato['blocco']}  "
                  f"tempo disponibile {resta:.1f}s")
        try: f.close()
        except Exception: pass
        riconnessioni+=1
    except Exception as e:
        print(f"   errore di connessione: {str(e)[:40]}, riprovo")
        time.sleep(2)
print(f"\n   avvisi per minuto: {[permin[i] for i in range(min(MINUTI,int((time.time()-t0)//60)+1))]}")
print(f"   riconnessioni: {riconnessioni}")
stop=True
print(f"\n   {avvisi} avvisi totali, {rilevanti} di aggiornamento prezzo")
# verifica: le posizioni segnate sono poi cadute?
print(f"\n   controllo se i candidati sono caduti davvero...")
cadute=0; controllate=0
visti=set()
for s_ in segnati:
    for a in s_["candidati"]:
        if a in visti: continue
        visti.add(a)
        r=salute(a)
        if not r: continue
        controllate+=1
        if r[1] < 1.0:
            cadute+=1
            print(f"      {a[:14]} CADUTA (salute {r[1]:.4f}, debito {r[0]:,.0f})")
with open(REG,"a") as g:
    g.write(json.dumps({"quando":time.strftime("%Y-%m-%d %H:%M",time.gmtime()),
        "minuti":MINUTI,"avvisi":avvisi,"avvisi_prezzo":rilevanti,
        "candidati_controllati":controllate,"caduti":cadute})+"\n")
print(f"   {cadute} cadute su {controllate} controllate")
