# -*- coding: utf-8 -*-
"""I prezzi di TUTTI gli asset di Aave, letti dal suo oracolo. Mai assunti.

RISCRITTO il 2/11 perche' la versione precedente dipendeva da un file di
storia (storia_v2.jsonl) per sapere quali asset prezzare -- e quel file era
stato evitto dalla cartella temporanea. Risultato: il generatore non girava,
e `prezzi_oracolo.json` -- che legge QUASI TUTTO il sistema, compreso
pescatore.py all'import -- era sparito. Il pescatore e la sentinella erano
vivi solo perche' non si erano riavviati: al primo riavvio morivano entrambi,
e la guardia li avrebbe rialzati in ciclo senza mai riuscirci.

Ora la lista degli asset la chiede al PROTOCOLLO (Pool.getReservesList), che
non si puo' perdere. Nessuna dipendenza da file locali.
"""
import json, time, os, sys, time, urllib.request
sys.path.insert(0,"agents")
from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
ORAC="0x54586be62e3c3580375ae3723c145253060ca0c2"
FONTI=["https://ethereum-rpc.publicnode.com",
       "https://gateway.tenderly.co/public/mainnet",
       "https://rpc.mevblocker.io"]
S_LISTA=firma("getReservesList()")[2:10]
S_PREZZO=firma("getAssetPrice(address)")[2:10]
S_DEC=firma("decimals()")[2:10]
D="data/liquidazioni"; os.makedirs(D, exist_ok=True)
FUORI=f"{D}/prezzi_oracolo.json"
def call(to, dati):
    for u in FONTI:
        try:
            c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call",
                "params":[{"to":to,"data":dati},"latest"]}).encode()
            r=urllib.request.Request(u,data=c,headers={
                "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=25))
            if d.get("result") and d["result"]!="0x": return d["result"]
        except Exception: pass
    return None
v=call(POOL,"0x"+S_LISTA)
if not v or len(v)<200:
    print("   non riesco a leggere la lista delle riserve: NON sovrascrivo"); sys.exit(1)
x=v[2:]; n=int(x[64:128],16)
riserve=["0x"+x[128+i*64+24:128+(i+1)*64].lower() for i in range(n)]
print(f"   {n} riserve nel protocollo")
out={}
for a in riserve:
    p=call(ORAC,"0x"+S_PREZZO+a[2:].zfill(64))
    d=call(a,"0x"+S_DEC)
    if not p or not d: continue
    prezzo=int(p,16)/1e8
    dec=int(d,16)
    if prezzo<=0 or not (0<dec<=36): continue
    out[a]={"prezzo_usd":prezzo,"decimali":dec}
    time.sleep(0.05)
# CANCELLO: non si sovrascrive un file buono con uno mezzo vuoto. Se la
# lettura e' andata male a meta', meglio tenere quello di prima.
if len(out) < max(10, n//2):
    print(f"   solo {len(out)} prezzi su {n}: NON sovrascrivo, troppo pochi"); sys.exit(1)
vecchio=0
if os.path.exists(FUORI):
    try: vecchio=len(json.load(open(FUORI)))
    except Exception: pass
if vecchio and len(out) < vecchio*0.8:
    print(f"   {len(out)} prezzi contro {vecchio} di prima: NON sovrascrivo"); sys.exit(1)
# IL TERZO CONTROLLO, sui VALORI (4/11). I due sopra guardano QUANTI prezzi
# ci sono, nessuno guardava quanto VALGONO: un singolo prezzo corrotto
# passava, e da li' ogni quantita' da vendere nasce sbagliata -- in
# silenzio, perche' nient'altro se ne accorgerebbe.
#
# E NON BLOCCA, SEGNALA. La prima stesura rifiutava di sovrascrivere, e
# aveva due difetti che ho visto prima di lasciarla: (1) rifiutando lascia
# in casa il file vecchio, quindi se quello era gia' corrotto il blocco
# impedisce la guarigione invece di aiutarla; (2) in un crollo vero i
# prezzi SALTANO per davvero, e la guardia avrebbe bloccato proprio i
# prezzi che servono nel momento in cui servono. Il problema era il
# silenzio, non la scrittura: quindi si scrive e si grida.
# Chi legge il grido: il C-check, a ogni giro.
SALTO_SOSPETTO = 0.25
prima = {}
try: prima = json.load(open(FUORI))
except Exception: pass
saltati = []
for a, d in out.items():
    pv = (prima.get(a) or {}).get("prezzo_usd")
    pn = d.get("prezzo_usd")
    if not pv or not pn: continue
    if abs(pn - pv) / pv > SALTO_SOSPETTO:
        saltati.append({"gettone": a, "prima": pv, "dopo": pn,
                        "variazione": round(100*(pn-pv)/pv, 2)})
if saltati:
    quanti = len(saltati); su = len(prima) or 1
    insieme = quanti >= max(2, su*0.25)
    print(f"   !!! {quanti} prezzi su {su} saltano oltre il {SALTO_SOSPETTO:.0%} "
          f"-- {'sembra il mercato che si muove' if insieme else 'POCHI: sembra una lettura sbagliata'}")
    for x in saltati[:5]:
        print(f"     {x['gettone'][:12]}  {x['prima']:,.4f} -> {x['dopo']:,.4f}  "
              f"({x['variazione']:+.1f}%)")
json.dump({"quando": time.time(), "saltati": saltati,
           "soglia": SALTO_SOSPETTO, "su_quanti": len(prima)},
          open("data/liquidazioni/prezzi_sospetti.json", "w"), indent=1)
json.dump(out, open(FUORI,"w"), indent=1)
W="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
print(f"   {len(out)} prezzi scritti (prima erano {vecchio})")
if W in out: print(f"   controllo: WETH ${out[W]['prezzo_usd']:,.2f}")
