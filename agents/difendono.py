# -*- coding: utf-8 -*-
"""I debitori DIFENDONO la posizione? E' la domanda che decide la metrica.

Il modello di probabilita' tratta le posizioni come immobili: calcola la
probabilita' che il prezzo scenda del tanto che serve, come se nessuno
facesse niente. Se i debitori aggiungono garanzia o ripagano quando si
avvicinano a 1,0, quel modello e' aria.

CONTRADDIZIONE che ha fatto nascere questa misura (31/10): il modello
dava EUR 311.878 di atteso in 30 giorni sulle nostre 99 posizioni, ma il
mercato Aave INTERO paga EUR 407.000/mese lordi di cui vendibili 41.000.
Attribuirci 7,6 volte il mercato vendibile e' impossibile -> il modello
sbaglia, e di molto. Due contatori della stessa cosa che non tornano.

Si misura la TRANSIZIONE: salute di 9 giorni fa contro salute di oggi,
sulle stesse posizioni. Non e' un modello, e' un prima/dopo.

BIAS da dichiarare, non da nascondere: il campione sono le posizioni a
rischio OGGI. Chi e' caduto 9 giorni fa ed e' stato liquidato al 50% ora
ha salute ~1,5 e NON e' piu' in questa lista -> le cadute si contano in
difetto. Il verso dell'errore e' noto: sottostima le cadute.
"""
import json, sys, time, urllib.request
sys.path.insert(0,"agents"); from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
SEL=firma("getUserAccountData(address)")[2:10]
FONTI=["https://gateway.tenderly.co/public/mainnet","https://rpc.mevblocker.io"]
import itertools; _g=itertools.cycle([0,1])
def rpc(m,p):
    i=next(_g)
    for u in (FONTI[i],FONTI[1-i]):
        try:
            c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
            r=urllib.request.Request(u,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=30))
            if "result" in d: return d["result"]
        except Exception: pass
    return None
def sal(a, blocco):
    v=rpc("eth_call",[{"to":POOL,"data":"0x"+SEL+a[2:].zfill(64)},blocco])
    if isinstance(v,str) and len(v)>=2+64*6:
        x=v[2:]
        return int(x[320:384],16)/1e18, int(x[64:128],16)/1e8
    return None,None
testa=int(rpc("eth_blockNumber",[]),16)
VECCHIO=testa-64800        # 9 giorni a 12 secondi
print(f"   oggi {testa} | 9 giorni fa {VECCHIO}")
# prova che l'archivio risponde davvero a quel blocco: senza questo cancello
# tutto il resto sarebbe un confronto fra oggi e oggi, in silenzio.
p=json.load(open("data/liquidazioni/composizione.json"))
primo=list(p.keys())[0]
s_old,_=sal(primo,hex(VECCHIO)); s_new,_=sal(primo,"latest")
if s_old is None:
    print("   l'archivio non risponde a 9 giorni: misura ABBANDONATA"); sys.exit(1)
if abs(s_old-s_new)<1e-12:
    print(f"   SOSPETTO: salute identica ({s_old}). L'archivio potrebbe "
          f"servire sempre l'ultimo blocco -> misura ABBANDONATA"); sys.exit(1)
print(f"   cancello passato: {primo[:12]} era {s_old:.4f}, ora {s_new:.4f}\n")
caduti={e["utente"].lower() for e in json.load(open("data/liquidazioni/caduti.json"))["eventi"]}
out=[]
for i,(u,c) in enumerate(p.items()):
    so,do_=sal(u,hex(VECCHIO))
    sn,dn=sal(u,"latest")
    if so is None or sn is None or so<=0 or so>100: continue
    out.append({"u":u.lower(),"prima":so,"ora":sn,
                "deb_prima":do_,"deb_ora":dn,
                "liquidato":u.lower() in caduti})
    if (i+1)%60==0: print(f"   {i+1}/{len(p)}...")
    time.sleep(0.05)
json.dump(out,open("data/liquidazioni/transizione.json","w"),indent=1)
print(f"\n   {len(out)} posizioni con prima/dopo\n")
BANDE=[(1.00,1.02),(1.02,1.05),(1.05,1.10),(1.10,1.20),(1.20,99)]
print("   salute 9gg fa   n   caduta  difesa  peggiorata  nulla   P(caduta/9gg)")
for a,b in BANDE:
    g=[r for r in out if a<=r["prima"]<b]
    if not g: continue
    cad=sum(1 for r in g if r["liquidato"] or r["ora"]<1.0)
    dif=sum(1 for r in g if not r["liquidato"] and r["ora"]>=1.0
            and r["ora"]>r["prima"]*1.01)
    peg=sum(1 for r in g if not r["liquidato"] and r["ora"]>=1.0
            and r["ora"]<r["prima"]*0.99)
    nul=len(g)-cad-dif-peg
    print(f"   {a:.2f}-{b:>5.2f}  {len(g):>4}  {cad:>5}  {dif:>6}  {peg:>10}  "
          f"{nul:>5}   {100*cad/len(g):>6.1f}%")
tot=len(out); cad=sum(1 for r in out if r["liquidato"] or r["ora"]<1.0)
print(f"\n   complessivo: {cad}/{tot} cadute in 9 giorni = {100*cad/tot:.1f}%")
print(f"   (la stessa cosa in 30 giorni, a ritmo costante: {100*cad/tot*30/9:.1f}%)")
