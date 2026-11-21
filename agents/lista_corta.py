# -*- coding: utf-8 -*-
"""La lista corta: chi e' vicino alla soglia di caduta.

RISCRITTA l'1/11 per una ragione di scala. Prima leggeva la salute di TUTTI
i debitori, uno alla volta, a ogni giro: a 16.676 debitori ci metteva venti
minuti, e la raccolta li sta portando verso 60.000+. A quel punto la lista
corta non starebbe piu' dietro, e i debitori nuovi non arriverebbero MAI al
pescatore: il laghetto crescerebbe sulla carta e non in acqua.

Due cambiamenti:
 1. MEMORIA. Si ricorda l'ultima salute vista di ciascuno e quando. Le
    priorita' a ogni giro:
      a) chi non si e' mai visto      -- e' l'unica vera incognita
      b) chi era sotto 1,30           -- gli unici che possono cadere presto
      c) i piu' vecchi di controllo   -- a giro, per non fidarsi del passato
 2. LETTURE A MAZZI. Un'unica richiesta HTTP porta 50 letture.
    REGOLA (imparata a caro prezzo su Base, vedi reference_base_rpc_tronca):
    le risposte di un mazzo si abbinano per "id", MAI per posizione. Alcune
    fonti ne restituiscono meno di quante chieste, e abbinare per indice
    sposta i dati di una casella in silenzio.
"""
import json, os, sys, time, urllib.request
sys.path.insert(0,"agents")
from keccak import firma
# LA DEFINIZIONE STA QUI, NON A META' FILE (5/11).
# Era sotto il suo primo uso: il codice a livello di modulo gira dall'alto
# in basso, quindi l'agente moriva di NameError alla prima scrittura. Non
# e' un errore di sintassi, quindi il controllo "ogni agente compila" lo
# dichiarava sano -- 76 agenti tutti verdi -- ed e' la STESSA FAMIGLIA del
# threading dimenticato nella sentinella: un nome mancante si vede solo
# ESEGUENDO. Intanto la popolazione sorvegliata e' rimasta ferma 15 ore, e
# la nona e la decima liquidazione hanno colpito posizioni che non c'erano.
def _salva_atomico(dati, dove, indent=None):
    """Si scrive di fianco e poi si sostituisce in un colpo.

    DIFETTO TROVATO il 5/11: questi due file si scrivevano con un
    json.dump(open(...,"w")) diretto, e la lista corta la leggono OTTO
    agenti fra cui la SENTINELLA, quella che compone i pacchetti. La
    ricostruzione dura minuti: in quella finestra un lettore trovava il
    file a meta' e la sentinella non componeva NIENTE, in silenzio.
    L'ho scoperto perche' una verifica e' diventata rossa con un errore di
    lettura JSON proprio mentre la lista si stava riscrivendo -- cioe' per
    caso. Un file che qualcuno legge mentre lo scrivi va sostituito, non
    riempito.
    """
    tmp = dove + ".tmp"
    with open(tmp, "w") as f:
        json.dump(dati, f, indent=indent)
    os.replace(tmp, dove)

POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
SEL=firma("getUserAccountData(address)")[2:10]
# PROVATE l'1/11, mazzo per mazzo, prima di fidarsi:
#   publicnode  mazzo 25 -> 25/25 in 0,2s      mevblocker mazzo 25 -> 25/25
#   tenderly    mazzo 10 -> 429 Too Many Requests
# Il mio primo tentativo usava mazzi da 50 con tenderly nel ripiego: le
# richieste venivano rifiutate e si aspettava il timeout, 1,2 letture al
# secondo contro le 14 della versione seriale. Un'ottimizzazione PEGGIORE
# dell'originale, e non l'avrei saputo senza misurarla.
FONTI=["https://ethereum-rpc.publicnode.com","https://rpc.mevblocker.io"]
D="data/liquidazioni"
FUORI=f"{D}/lista_corta.json"; NOTE=f"{D}/salute_note.json"
MAZZO=25            # letture per richiesta: il massimo provato che regge
BILANCIO=20000      # a ~100 letture/s sono ~3 minuti: ci sta tutto
VECCHIO=12*3600     # dopo 12 ore una salute nota non e' piu' affidabile

def mazzo(indirizzi):
    """Legge la salute di piu' indirizzi in una richiesta. Abbina per ID."""
    corpo=[{"jsonrpc":"2.0","id":i,"method":"eth_call",
            "params":[{"to":POOL,"data":"0x"+SEL+a[2:].zfill(64)},"latest"]}
           for i,a in enumerate(indirizzi)]
    for u in FONTI:
        try:
            r=urllib.request.Request(u,data=json.dumps(corpo).encode(),
              headers={"content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=60))
            if not isinstance(d,list): continue
            out={}
            for e in d:
                i=e.get("id")
                if not isinstance(i,int) or i>=len(indirizzi): continue
                v=e.get("result")
                if not v or len(v)<2+64*6: continue
                x=v[2:]
                out[indirizzi[i]]={           # <- abbinato per ID, non per posizione
                  "garanzia":int(x[0:64],16)/1e8,"debito":int(x[64:128],16)/1e8,
                  "soglia":int(x[192:256],16)/100,"salute":int(x[320:384],16)/1e18}
            if out: return out
        except Exception: pass
    return {}

deb=json.load(open(f"{D}/debitori.json"))
note=json.load(open(NOTE)) if os.path.exists(NOTE) else {}
ora=time.time()
mai=[a for a in deb if a not in note]
noti=[a for a in deb if a in note]
rischio=sorted([a for a in noti if note[a]["salute"]<1.30],
               key=lambda a: note[a]["salute"])
altri=sorted([a for a in noti if note[a]["salute"]>=1.30],
             key=lambda a: note[a]["quando"])
coda=(mai + rischio + altri)[:BILANCIO]
print(f"   {len(deb)} debitori | mai visti {len(mai)} | a rischio {len(rischio)} "
      f"| altri {len(altri)}")
print(f"   questo giro ne leggo {len(coda)} a mazzi di {MAZZO}")
t0=time.time(); letti=0
for i in range(0, len(coda), MAZZO):
    r=mazzo(coda[i:i+MAZZO])
    for a,v in r.items():
        note[a]={"salute":v["salute"],"debito":v["debito"],
                 "garanzia":v["garanzia"],"soglia":v["soglia"],"quando":ora}
    letti+=len(r)
    if (i//MAZZO) % 40 == 0: _salva_atomico(note, NOTE)
    time.sleep(0.05)   # non si brucia la fonte
_salva_atomico(note, NOTE)
dt=max(0.001, time.time()-t0)
print(f"   {letti} letti in {dt:.0f}s ({letti/dt:.0f}/s) — la versione seriale "
      f"faceva 14/s")
# la lista corta si compone da TUTTA la memoria, non solo da questo giro
corta=[]
# SOGLIA MINIMA DI DEBITO, non arbitraria: il premio e' il 7% di metà del
# debito, cioe' il 3,5% del debito. Il guadagno minimo del pescatore e' $5,
# quindi sotto $143 di debito la posizione NON PUO' pagarci, qualunque cosa
# faccia il prezzo. Prima entravano in lista decine di posizioni con debito
# sotto il dollaro e salute 0,7: occupavano posti e sembravano urgentissime.
from banda import BANDA, MINIMO_DEBITO


for a,v in note.items():
    # LA BANDA VIENE DA UN SOLO POSTO (vedi agents/banda.py): qui c'era
    # 1,15 mentre il pianificatore usava 1,25, e le 353 posizioni fra i due
    # numeri -- 7,38 milioni di premio lordo -- non entravano MAI in
    # sorveglianza. Due pezzi che devono essere d'accordo leggono lo stesso
    # numero.
    if v.get("debito",0)<MINIMO_DEBITO or v["salute"]>=BANDA: continue
    corta.append({"indirizzo":a,"salute":v["salute"],"debito":v["debito"],
      "garanzia":v["garanzia"],"soglia":v["soglia"],
      "caduta_necessaria":(1-1/v["salute"])*100 if v["salute"]>0 else 0,
      "vecchia_di_ore":round((ora-v["quando"])/3600,1)})
corta.sort(key=lambda x:x["salute"])
_salva_atomico(corta, FUORI, indent=1)
vecchie=[r for r in corta if r["vecchia_di_ore"]>12]
print(f"\n   LISTA CORTA: {len(corta)} sotto {BANDA} "
      f"({len(vecchie)} con una lettura piu' vecchia di 12 ore)")
vic=[r for r in corta if r["caduta_necessaria"]<2]
print(f"   a meno del 2% dalla caduta: {len(vic)}, "
      f"{sum(r['debito'] for r in vic):,.0f} USD di debito")
for r in corta[:10]:
    print(f"   {r['indirizzo'][:14]}  salute {r['salute']:.4f}  "
          f"debito ${r['debito']:>12,.0f}  calo {r['caduta_necessaria']:>6.2f}%")
