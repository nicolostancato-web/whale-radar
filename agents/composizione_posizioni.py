# -*- coding: utf-8 -*-
"""Per ogni posizione sorvegliata: QUALE garanzia e QUALE debito.

Senza questo, anche vedendo una caduta non saprei cosa liquidare: servono
l'asset del debito da ripagare e quello della garanzia da incassare.
Si calcola PRIMA, con calma; al momento della caduta la risposta e' pronta.

--- STORIA DEI DIFETTI, scritta qui perche' non si rifacciano ---

31/10, difetto 1: si prendevano i primi 25 della lista corta e si
  SOVRASCRIVEVA il file. Per sempre gli stessi 25: allargare il laghetto
  non serviva a nulla, il frutto veniva buttato a ogni giro.
  Ora si ACCUMULA e si danno le non-ancora-composte, dalla piu' malata.

31/10, difetto 2: si interrogavano TUTTI i 67 asset del protocollo per
  ogni persona (67 chiamate a testa, 25 persone ogni 70 minuti = 17 ore
  per i 363 candidati che restavano). Ma Aave sa gia' dire quali asset usa
  un utente: getUserConfiguration torna un uint256 con 2 bit per riserva,
    bit 2i   = prende in prestito la riserva i
    bit 2i+1 = usa la riserva i come garanzia
  e l'indice i e' la posizione in Pool.getReservesList().
  VERIFICATO prima di usarlo, su 4 posizioni di cui sapevo gia' la
  risposta col metodo lento: 4/4 riprodotte. Da 67 chiamate a ~4.
"""
from scrittura import atomico
import json, os, sys, time, urllib.request
sys.path.insert(0,"agents")
from keccak import firma
U="https://ethereum-rpc.publicnode.com"
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
PDP="0x41393e5e337606dc3821075af65aee84d7688cbd"
S_LISTA=firma("getReservesList()")[2:10]
S_CONF =firma("getUserConfiguration(address)")[2:10]
S_DATI =firma("getUserReserveData(address,address)")[2:10]
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))

def rpc(dati, to, giri=3):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call",
      "params":[{"to":to,"data":dati},"latest"]}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            v=json.load(urllib.request.urlopen(r,timeout=20))
            if "result" in v: return v["result"]
        except Exception: pass
        time.sleep(0.3*(g+1))
    return None

# l'ordine delle riserve NON e' quello del ProtocolDataProvider: l'indice
# dei bit e' la posizione in Pool.getReservesList(). Prenderlo dall'altra
# fonte sposterebbe tutti gli asset di una casella, in silenzio.
v=rpc("0x"+S_LISTA, POOL)
if not v or len(v)<200:
    print("   non riesco a leggere la lista delle riserve"); sys.exit(1)
x=v[2:]; n=int(x[64:128],16)
riserve=["0x"+x[128+i*64+24:128+(i+1)*64].lower() for i in range(n)]
print(f"   {n} riserve nella lista del Pool")

FUORI="data/liquidazioni/composizione.json"
try: out=json.load(open(FUORI))
except Exception: out={}
gia=set(k.lower() for k in out)
try: corta=json.load(open("data/liquidazioni/lista_corta.json"))
except Exception: corta=[]
# IL LIMITE LO DECIDE UN NUMERO SOLO (6/11). Qui era scritto > 1000, cioe'
# un TERZO valore dopo BANDA e MINIMO_DEBITO -- e proprio questo file ha in
# cima la lezione che un limite su chi guardiamo non puo' stare in due posti.
# COSTO MISURATO: 266 posizioni con debito fra 150 e 1.000 dollari NON SONO
# MAI STATE COMPOSTE, 38 delle quali a meno del 2% dalla soglia. Erano dentro
# il vecchio MINIMO_DEBITO di 150 e avrebbero dovuto essere in gioco da
# sempre: il limite vero era 1.000, scritto dove nessuno lo guardava.
# La composizione e' il collo fra «trovata» e «sorvegliata»: una posizione
# non composta non riceve un ordine, quindi per il pescatore non esiste.
from banda import MINIMO_DEBITO as _MIN_DEB
tutte=[c for c in corta if c.get("debito",0) >= _MIN_DEB]
tutte.sort(key=lambda c: c["salute"])
nuove=[c for c in tutte if c["indirizzo"].lower() not in gia]
PER_GIRO=250     # ~4 chiamate a testa: 1.000 chiamate in ~60s, regge
# UNA COMPOSIZIONE COMPOSTA UNA VOLTA NON E' GIUSTA PER SEMPRE (7/11).
# Questo file componeva SOLO le posizioni mai viste (`not in gia`), quindi
# una composizione vecchia non si rinnovava nemmeno da sola -- e i gettoni
# del debito cambiano, perche' un utente rimborsa in uno e prende in
# prestito un altro.
# Costo misurato: 29 ordini portavano «il debito registrato non esiste
# piu'», e sarebbero rimasti sbagliati PER SEMPRE. Uno di quelli vale 4,5
# MILIONI di debito, cioe' ~135.000 \$ di premio: non era un confine del
# mercato, era una riga che non si rileggeva.
# Ora chi scopre l'errore (prepara_vendite) scrive in una coda, e questa
# coda passa DAVANTI alle nuove: una composizione sbagliata fa perdere una
# presa, una composizione mancante fa solo aspettare.
_CODA = "data/liquidazioni/da_ricomporre.json"
try:
    _da_rifare_comp = json.load(open(_CODA))
except Exception:
    _da_rifare_comp = {}
_indice = {c["indirizzo"].lower(): c for c in tutte}
_rifare = [_indice[a] for a in _da_rifare_comp if a in _indice]
if _rifare:
    print(f"   {len(_rifare)} composizioni da RIFARE (il debito registrato "
          f"non esisteva): passano davanti")
corta=(_rifare + nuove)[:PER_GIRO]
print(f"   lista corta {len(tutte)} con debito | composte {len(out)}"
      f" | mancano {len(nuove)} | ne faccio {len(corta)}\n")
if not corta:
    print("   tutte composte: niente da fare"); sys.exit(0)

def importo(u, a):
    """Garanzia e debito in USD per un singolo asset, o None."""
    d=rpc("0x"+S_DATI+a[2:].zfill(64)+u[2:].zfill(64), PDP)
    if not d or len(d)<2+64*3: return None
    y=d[2:]; p=PR.get(a)
    if not p: return None
    return (int(y[0:64],16)/10**p["decimali"]*p["prezzo_usd"],       # aToken
            int(y[128:192],16)/10**p["decimali"]*p["prezzo_usd"])    # debito var

fatte=0; salti=0
for c in corta:
    u=c["indirizzo"]
    d=rpc("0x"+S_CONF+u[2:].zfill(64), POOL)
    if not d: salti+=1; continue
    bm=int(d,16)
    i_gar=[i for i in range(n) if bm>>(2*i+1) & 1]
    i_deb=[i for i in range(n) if bm>>(2*i)   & 1]
    if not i_gar or not i_deb: salti+=1; continue
    gar=[]; deb=[]
    for i in set(i_gar)|set(i_deb):
        a=riserve[i]
        r=importo(u,a)
        if not r: continue
        if i in i_gar and r[0]>0: gar.append((a,r[0]))
        if i in i_deb and r[1]>0: deb.append((a,r[1]))
        time.sleep(0.03)
    if not gar or not deb: salti+=1; continue
    gar.sort(key=lambda z:-z[1]); deb.sort(key=lambda z:-z[1])
    out[u]={"garanzia_principale":gar[0][0],"garanzia_usd":round(gar[0][1],2),
            "debito_principale":deb[0][0],"debito_usd":round(deb[0][1],2),
            "salute":c["salute"]}
    fatte+=1
    if fatte<=8 or fatte%25==0:
        print(f"   {u[:14]} salute {c['salute']:.4f}  "
              f"gar {gar[0][0][:10]}.. ${gar[0][1]:,.0f}  "
              f"deb {deb[0][0][:10]}.. ${deb[0][1]:,.0f}")
    if fatte%25==0:
        atomico(out, FUORI, indent=1)   # salva lungo la strada:
        # un'interruzione non deve buttare mezz'ora di lavoro
atomico(out, FUORI, indent=1)
# LA CODA SI SVUOTA, ALTRIMENTI E' UNA PERDITA (difetto mio del 7/11,
# trovato un giro dopo averlo introdotto). Avevo fatto leggere la coda di
# ricomposizione senza RIMUOVERE le voci fatte: le stesse nove posizioni
# sarebbero state rifatte a ogni giro per sempre, prendendo il posto delle
# nuove e trasformando una riparazione in un blocco.
# Si toglie solo quello che si e' DAVVERO ricomposto in questo giro.
if _da_rifare_comp:
    _fatti = {c["indirizzo"].lower() for c in corta if c["indirizzo"] in out}
    _restano = {a: v for a, v in _da_rifare_comp.items() if a not in _fatti}
    if len(_restano) != len(_da_rifare_comp):
        try:
            _t = _CODA + ".tmp"
            json.dump(_restano, open(_t, "w"), indent=1)
            os.replace(_t, _CODA)
            print(f"   coda di ricomposizione: {len(_da_rifare_comp)} -> "
                  f"{len(_restano)}")
        except Exception as _e:
            print(f"   non ho potuto svuotare la coda: {str(_e)[:50]}")
print(f"\n   composte {fatte} questo giro ({salti} saltate: senza garanzia"
      f" o senza debito) | archivio: {len(out)}")
