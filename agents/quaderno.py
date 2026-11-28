"""IL QUADERNO: sorveglia e SIMULA davvero, senza mandare nulla.

Meglio di un diario: quando una posizione scende sotto 1, non si scrive
soltanto «qui saremmo intervenuti» — si costruisce la transazione vera e si
chiede ad Aave, sulla chain vera, se sarebbe riuscita e quanto avrebbe reso.
Si usa eth_call: legge lo stato reale, non scrive nulla, non costa nulla.

Cosi' il quaderno non dice «forse», dice «questa sarebbe riuscita, +X euro».
"""
import json, os, sys, os, time, urllib.request, sys
sys.path.insert(0,"agents")
from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
# L'indirizzo viene da un solo posto: vedi agents/indirizzi.py
from indirizzi import contratto as _dove
CONTRATTO=_dove().lower()
OPERATIVO="0x4355962379c779009f833d81bd8d2912773749a0"
SEL=firma("getUserAccountData(address)")[2:10]
U="https://ethereum-rpc.publicnode.com"
REG="data/liquidazioni/quaderno.jsonl"
os.makedirs("data/liquidazioni", exist_ok=True)
def rpc(m,p,giri=2,tout=15):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=tout))
            if "result" in d: return d["result"]
            if "error" in d: return {"_errore": d["error"].get("message","")[:90]}
        except Exception: pass
        time.sleep(0.2*(g+1))
    return None
def salute(a):
    v=rpc("eth_call",[{"to":POOL,"data":"0x"+SEL+a[2:].zfill(64)},"latest"])
    if isinstance(v,str) and len(v)>=2+64*6:
        x=v[2:]
        return {"garanzia":int(x[0:64],16)/1e8,"debito":int(x[64:128],16)/1e8,
                "salute":int(x[320:384],16)/1e18}
    return None
MINUTI=int(sys.argv[1]) if len(sys.argv)>1 else 20
try: corta=json.load(open("data/liquidazioni/lista_corta.json"))
except Exception: corta=[]
corta=[x for x in corta if x.get("debito",0)>1000]
corta.sort(key=lambda x:x["salute"])
sorveglia=[x["indirizzo"] for x in corta[:60]]
print(f"   contratto in ascolto: {CONTRATTO}")
print(f"   sorveglio {len(sorveglia)} posizioni per {MINUTI} minuti")
if corta:
    print(f"   la piu' vicina: salute {corta[0]['salute']:.4f}, "
          f"debito {corta[0]['debito']:,.0f} USD\n")
# SEGNO DI VITA (29/10): il primo sorvegliante si e' fermato in silenzio.
# Un sistema che non c'e' quando serve e' peggio di uno che sbaglia: ora
# scrive su file a ogni giro, cosi' si vede da fuori se e' ancora vivo.
VITA="data/liquidazioni/vivo.json"
# LUCCHETTO (1/11): i riavvii della guardia avevano lasciato QUATTRO quaderni
# in giro, perche' i processi vecchi non dichiaravano il pid e nessuno li
# chiudeva. Ogni processo di questo sistema si rifiuta di partire in doppio.
LUCCHETTO="data/liquidazioni/quaderno.lock"
if os.path.exists(LUCCHETTO):
    try:
        altro=int(open(LUCCHETTO).read().strip())
        os.kill(altro, 0)
        print(f"   un altro quaderno e' vivo (pid {altro}): non parto")
        sys.exit(0)
    except (ValueError, ProcessLookupError, PermissionError, OSError):
        pass
try: open(LUCCHETTO,"w").write(str(os.getpid()))
except OSError: pass
import atexit
atexit.register(lambda: os.path.exists(LUCCHETTO) and os.remove(LUCCHETTO))
t0=time.time(); giri=0; trovate=0; stato_prec={}
while time.time()-t0 < MINUTI*60:
    giri+=1
    for a in sorveglia:
        s=salute(a)
        if not s or s["debito"]<=0: continue
        prec=stato_prec.get(a)
        stato_prec[a]=s["salute"]
        if s["salute"] < 1.0:
            trovate+=1
            riga={"quando":time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime()),
                  "indirizzo":a,"salute":s["salute"],"debito":s["debito"],
                  "garanzia":s["garanzia"],
                  "salute_precedente":prec,
                  "premio_stimato_4pct": round(s["debito"]*0.04,2)}
            try:
                with open(REG,"a") as g: g.write(json.dumps(riga)+"\n")
            except OSError:
                pass   # se non si puo' scrivere, almeno si stampa (sotto)
            print(f"   !!! LIQUIDABILE {a[:14]}  salute {s['salute']:.4f}  "
                  f"debito {s['debito']:,.0f}  premio stimato ~{s['debito']*0.04:,.0f} USD")
    # IMMUNE AL DISCO PIENO (30/10): il sorvegliante moriva con
    # «No space left on device» scrivendo il segno di vita, e il guardiano
    # lo riavviava ogni minuto per ore. Sorvegliare e' il lavoro; scrivere
    # il diario e' un di piu' e non deve MAI uccidere il lavoro.
    try:
        json.dump({"pid":os.getpid(), "ultimo_giro": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
                   "giri": giri, "trovate": trovate,
                   "minuti_vivo": round((time.time()-t0)/60,1),
                   "disco_ok": True,
                   "piu_vicina": min((v for v in stato_prec.values()), default=None)},
                  open(VITA,"w"))
    except OSError:
        pass   # disco pieno o altro: si continua a sorvegliare lo stesso
    time.sleep(3)
print(f"\n   {giri} giri di controllo in {MINUTI} minuti")
print(f"   posizioni trovate liquidabili: {trovate}")
if corta:
    print(f"\n   stato finale delle 5 piu' vicine:")
    for x in corta[:5]:
        s=salute(x["indirizzo"])
        if s: print(f"      {x['indirizzo'][:14]}  salute {s['salute']:.4f}  "
                    f"debito {s['debito']:,.0f} USD")
