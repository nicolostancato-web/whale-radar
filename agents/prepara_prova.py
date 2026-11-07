# -*- coding: utf-8 -*-
"""Prepara i dati per la prova su UNA posizione vera, qualunque garanzia.

Nasce generalizzando prepara_prova_weth.py: scrivere una prova per asset
e' il modo di avere sei prove che si somigliano e nessuna aggiornata.
Un asset si arma SOLO dopo che questa prova e' passata su posizione vera.

Uso:  prepara_prova.py <indirizzo_utente>
Poi:  cd liquidatore && RPC_ARCHIVIO=<rpc> forge test --match-contract ProvaVera

Prezzi letti dall'oracolo ORA, non dal file: un prezzo di ore prima
sposterebbe la taglia e la prova direbbe un'altra cosa.
"""
import json, os, sys, time, urllib.request
sys.path.insert(0,"agents")
# una costante, un nome: il margine lo decide pescatore.py, non questo file
from pescatore import SCIVOLAMENTO_BP
from keccak import firma
from pescatore import (trova_posizione, AMMESSI, GUADAGNO_MINIMO_USD,
                       tetto_per, FRAZIONE_PREMIO_PRETESA)
U="https://ethereum-rpc.publicnode.com"
ORAC="0x54586be62e3c3580375ae3723c145253060ca0c2"
CONTR="0xE30b58692FB7a1a417d3e0F1F5585a8Bc4D51212"
SEL=firma("getAssetPrice(address)")[2:10]
def rpc(m,p):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    for g in range(3):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=20))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.3)
    return None
def prezzo(a):
    v=rpc("eth_call",[{"to":ORAC,"data":"0x"+SEL+a[2:].zfill(64)},"latest"])
    return int(v,16)/1e8 if v else None
if len(sys.argv)<2:
    print("   serve l'indirizzo della posizione"); sys.exit(1)
UTENTE=sys.argv[1]
comp=json.load(open("data/liquidazioni/composizione.json"))
chiavi=[k for k in comp if k.lower()==UTENTE.lower()]
if not chiavi: print(f"   {UTENTE} non e' nella composizione"); sys.exit(1)
c=comp[chiavi[0]]
gar=c["garanzia_principale"].lower(); deb=c["debito_principale"].lower()
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
TETTI=json.load(open("data/liquidazioni/tetti.json"))
if gar not in TETTI:
    print(f"   {gar[:10]} non ha un tetto misurato: prima misura_tetti.py"); sys.exit(1)
pg=prezzo(gar); pd=prezzo(deb)
if not pg or not pd: print("   oracolo muto"); sys.exit(1)
stesso = (gar == deb)
print(f"   posizione {UTENTE[:14]}  salute {c['salute']:.4f}")
print(f"   garanzia {gar[:10]} ${pg:,.4f}   debito {deb[:10]} ${pd:,.4f}")
print(f"   {'STESSO GETTONE: nessuna vendita' if stesso else 'serve vendere'}")
dus=c["debito_usd"]*0.5
# Lo STESSO tetto del pescatore e di prepara_vendite: il 4/11 qui c'era
# TETTI[gar], cioe' il tetto per GETTONE, mentre gli altri due file usano
# quello per COPPIA. La stessa costante in un terzo posto -- e la prova
# girava su una taglia che il sistema vero non userebbe.
_tet=tetto_per(gar, deb)
if dus*1.07>_tet: dus=_tet/1.07; print(f"   tagliato al tetto ${_tet:,}")
if dus*0.07 < GUADAGNO_MINIMO_USD:
    print(f"   premio ${dus*0.07:,.2f} sotto il minimo: non si prova"); sys.exit(1)
dd=PR[deb]["decimali"]; dg=PR[gar]["decimali"]
qd=int(dus/pd*10**dd)
print(f"   chiudo ${dus:,.0f} -> premio atteso ${dus*0.07:,.0f}")
os.makedirs("liquidatore/dati",exist_ok=True)
def scrivi(n,v): open(f"liquidatore/dati/p_{n}.txt","w").write(str(v))
if stesso:
    sede="0x0000000000000000000000000000000000000000"; dati="0x"; pos=0
    print("   piano a ZERO passi")
else:
    qg=int(dus*1.07*0.995/pg*10**dg)
    # SI USA LO STESSO PERCORSO DEL SISTEMA VERO. Qui c'erano chiamate
    # all'aggregatore scritte a parte, e il 4/11 notte e' diventato un
    # difetto serio: il pescatore aveva imparato a ripiegare su Uniswap
    # quando l'aggregatore blocca, ma la PROVA no -- quindi provava una
    # strada che il sistema non prende piu'. Una prova che non attraversa
    # il codice vero rassicura invece di verificare.
    from pescatore import preventivo as _prev
    sede, dati, pos, app = _prev(gar, deb, str(qg), dg, dd)
    if not sede:
        if "429" in str(dati) or "Too Many" in str(dati):
            print(f"   nessuna strada: {dati}"); sys.exit(3)
        print(f"   preventivo non ottenuto: {str(dati)[:120]}"); sys.exit(1)
    print(f"   vendo {qg/10**dg:,.4f} via {sede[:12]} | importo a offset {pos}")
for n,v in (("utente",UTENTE),("garanzia",gar),("debito",deb),
            ("qdebito",qd),("sede",sede),("dati",dati),("posizione",pos),
            ("approvare",app or "0x"+"0"*40),
            # IL GUADAGNO PRETESO, NELLA MONETA DEL DEBITO. Il 4/11 notte
            # lo passavo alla prova come numero grezzo fisso (8,17e17),
            # tarato su un debito a 18 decimali: su un debito in USDT (6
            # decimali) quel numero vale 817 miliardi di dollari e la prova
            # falliva sempre. Un importo senza la sua moneta -- la terza
            # volta che ci casco. Ora si calcola come in produzione.
            ("guadagno", int(max(GUADAGNO_MINIMO_USD,
                                 dus*0.07*FRAZIONE_PREMIO_PRETESA)/pd*10**dd)),
            ("stesso",1 if stesso else 0)):
    scrivi(n,v)
print("   dati scritti in liquidatore/dati/p_*.txt")
