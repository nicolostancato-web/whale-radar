"""I vincitori «occasionali» sono professionisti con contratti usa-e-getta?

Se dietro venti contratti diversi ci sono tre creatori, sono lo stesso
attore che ne brucia uno per volta — e la fetta scoperta non esiste.
Se i creatori sono tutti diversi, sono attori diversi davvero.

Blockscout espone il creatore di ogni contratto, gratis. Si va PIANO:
poche richieste, pausa fra una e l'altra, stop al primo rifiuto.
"""
import json, time, urllib.request, collections, os
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
EUR=1/1.08
def valore(a,q):
    v=PR.get(a)
    return None if not v else q/10**v["decimali"]*v["prezzo_usd"]*EUR
ev=[json.loads(x) for x in open("data/liquidazioni/storia_v2.jsonl")]
occ=collections.defaultdict(lambda:{"prem":0.0,"liq":None,"ign":0})
for e in ev:
    d=e["dati"][2:]
    if len(d)<64*3: continue
    o=occ[e["tx"]]; o["liq"]="0x"+d[64*2+24:64*3]
    vg=valore(e["gar"], int(d[64:128],16)); vd=valore(e["deb"], int(d[0:64],16))
    if vg is None or vd is None: o["ign"]+=1
    else: o["prem"]+=vg-vd
c=collections.Counter(o["liq"] for o in occ.values() if o["liq"])
una=[o for o in occ.values() if o["ign"]==0 and o["prem"]>=500 and c[o["liq"]]==1]
una.sort(key=lambda x:-x["prem"])
print(f"   {len(una)} occasioni sopra 500 EUR vinte da indirizzi che compaiono UNA volta\n")
FUORI="data/liquidazioni/creatori.json"
noti=json.load(open(FUORI)) if os.path.exists(FUORI) else {}
def creatore(a):
    if a in noti: return noti[a]
    u=f"https://eth.blockscout.com/api/v2/addresses/{a}"
    try:
        r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0","accept":"application/json"})
        d=json.load(urllib.request.urlopen(r, timeout=40))
    except Exception as e:
        return {"errore": str(e)[:40]}
    cr=(d.get("creator_address_hash") or "").lower()
    noti[a]={"creatore":cr,"nome":d.get("name"),
             "verificato":bool(d.get("is_verified")),
             "tx":d.get("transactions_count")}
    json.dump(noti, open(FUORI,"w"))
    return noti[a]
fatti=0
for o in una[:8]:
    if fatti>=8: break
    info=creatore(o["liq"])
    if info.get("errore"):
        print(f"   {o['liq'][:14]}  rifiuto: {info['errore']} — mi fermo")
        break
    print(f"   premio {o['prem']:>10,.0f}€  contratto {o['liq'][:14]}..")
    print(f"      creato da {str(info.get('creatore'))[:20]}..  "
          f"nome {info.get('nome') or '-'}  "
          f"transazioni {info.get('tx')}")
    fatti+=1
    time.sleep(4)
if noti:
    cr=collections.Counter(v.get("creatore") for v in noti.values() if v.get("creatore"))
    print(f"\n   {len(noti)} contratti esaminati, {len(cr)} creatori distinti")
    for a,n in cr.most_common(5):
        print(f"      {a[:24]}..  ha creato {n}")
    if len(cr)>0:
        p=cr.most_common(1)[0][1]/sum(cr.values())*100
        print(f"\n   -> {'STESSO ATTORE dietro piu contratti: fetta sospetta' if p>50 else 'creatori diversi: attori diversi davvero'}")
