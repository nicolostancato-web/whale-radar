"""Accumulatore delle liquidazioni su piu' protocolli di prestito.

Tre scelte di progetto, ognuna da una lezione gia' pagata:
  - RIPRENDE da dove si era fermato (non guarda sempre le ultime ore):
    cosi' la copertura si accumula senza buchi e il tasso e' reale;
  - REGISTRA i blocchi davvero letti e quelli falliti: gli zeri silenziosi
    hanno gia' fatto sembrare morto Kleros e sbagliato di 5x il conto;
  - PIU' PROTOCOLLI: Aave da solo e' un pavimento del mestiere, non la sua
    dimensione.

Ogni esecuzione scrive una riga in data/liquidazioni/giro.jsonl.
"""
import json, os, time, urllib.request, sys, collections
sys.path.insert(0,"agents")
from keccak import firma
# FIRME — stato della verifica al 28/10/2026:
#   aave_v3   VERIFICATA: ha sparato eventi veri con questa firma
#   spark     verificata per costruzione: clone di Aave v3, stessa firma
#   morpho    VERIFICATA: 0xa4946ede... confermata come Liquidate di Morpho
#             Blue (morpho-org/morpho-blue, EventsLib.sol)
#   compound3 NON verificata: se resta muta dopo giorni di copertura mentre
#             le altre sparano, sospettare la firma prima della realta'
PROT={
 "aave_v3":   ("0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
               firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")),
 "spark":     ("0xc13e21b648a5ee794902342038ff3adab66be987",
               firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")),
 "morpho":    ("0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb",
               firma("Liquidate(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)")),
 "compound3": ("0xc3d688b66703497daa19211eedff47f25384cdc3",
               firma("AbsorbCollateral(address,address,address,uint256,uint256)")),
}
RPC=["https://eth.llamarpc.com","https://ethereum-rpc.publicnode.com",
     "https://rpc.ankr.com/eth","https://cloudflare-eth.com"]
def chiama(m,p=None,giri=6):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p or []}).encode()
    for g in range(giri):
        for u in RPC:
            try:
                r=urllib.request.Request(u,data=c,headers={
                  "content-type":"application/json","user-agent":"Mozilla/5.0"})
                d=json.load(urllib.request.urlopen(r,timeout=30))
                if "result" in d and d["result"] is not None: return d["result"]
            except Exception: pass
        time.sleep(0.4*(g+1))
    return None
D="data/liquidazioni"; os.makedirs(D, exist_ok=True)
F=f"{D}/giro.jsonl"; S=f"{D}/stato.json"
ult=int(chiama("eth_blockNumber"),16)
stato=json.load(open(S)) if os.path.exists(S) else {}
da = stato.get("ultimo_letto", ult-1800)      # prima volta: ultime ~6 ore
if da >= ult:
    print("   nessun blocco nuovo"); sys.exit(0)
fino = min(ult, da + 1800)                    # un pezzo per giro, senza strafare
print(f"   blocchi {da+1}..{fino}  ({fino-da} blocchi, ~{(fino-da)*12/3600:.1f} ore)")
tot=collections.Counter(); letti=0; falliti=0
eventi=[]
b=da+1
while b<=fino:
    f=min(b+199, fino)
    ok_finestra=True
    for nome,(ind,sig) in PROT.items():
        r=chiama("eth_getLogs",[{"fromBlock":hex(b),"toBlock":hex(f),
                                 "address":ind,"topics":[sig]}])
        if r is None: ok_finestra=False; continue
        for x in r:
            # 28/10: salvavo solo protocollo/blocco/transazione. Senza la
            # moneta della garanzia non si puo' risalire all'oracolo giusto,
            # e gli unici eventi abbastanza recenti per avere i log erano
            # proprio questi. Si salva tutto cio' che l'evento porta.
            eventi.append({"prot":nome,"blocco":int(x["blockNumber"],16),
                           "tx":x["transactionHash"],
                           "gar":("0x"+x["topics"][1][-40:]) if len(x.get("topics",[]))>1 else None,
                           "deb":("0x"+x["topics"][2][-40:]) if len(x.get("topics",[]))>2 else None,
                           "utente":("0x"+x["topics"][3][-40:]) if len(x.get("topics",[]))>3 else None,
                           "dati":x.get("data")})
            tot[nome]+=1
    if ok_finestra: letti += f-b+1
    else: falliti += f-b+1
    b=f+1; time.sleep(0.1)
# LEZIONE 28/10 (quarta volta oggi la stessa famiglia): una transazione puo'
# liquidare PIU' posizioni ed emettere piu' eventi. Otto eventi Spark erano
# UNA transazione: contarli come otto gonfiava il tasso da 11 a 30 al giorno.
# L'unita' di «quante occasioni ci sono» e' la TRANSAZIONE, non l'evento.
tx_distinte={e["tx"] for e in eventi}
riga={"da":da+1,"a":fino,"blocchi_letti":letti,"blocchi_falliti":falliti,
      "eventi":dict(tot),"n":len(eventi),"occasioni":len(tx_distinte),
      "quando":time.strftime("%Y-%m-%d %H:%M", time.gmtime())}
with open(F,"a") as g: g.write(json.dumps(riga)+"\n")
json.dump({"ultimo_letto":fino}, open(S,"w"))
with open(f"{D}/eventi.jsonl","a") as g:
    for e in eventi: g.write(json.dumps(e)+"\n")
print(f"   letti {letti}, falliti {falliti} "
      f"({falliti/(letti+falliti)*100:.0f}%) | eventi {len(eventi)} {dict(tot)}\n")
righe=[json.loads(x) for x in open(F)]
L=sum(r["blocchi_letti"] for r in righe)
N=sum(r["n"] for r in righe)
# le occasioni si contano sulle transazioni distinte di TUTTO l'archivio,
# non sommando i giri (una tx potrebbe comparire in due giri)
import json as _j, os as _o
_e=[_j.loads(x) for x in open(f"{D}/eventi.jsonl")] if _o.path.exists(f"{D}/eventi.jsonl") else []
OCC=len({x["tx"] for x in _e})
agg=collections.Counter()
for r in righe: agg.update(r["eventi"])
g=L*12/86400
print(f"   ACCUMULATO: {L:,} blocchi ({g:.2f} giorni)")
print(f"   {N} eventi ma {OCC} OCCASIONI (transazioni distinte)")
if g>0:
    print(f"   tasso: {OCC/g:.1f} occasioni al giorno"
          f"   (contando gli eventi sarebbe {N/g:.1f}: sbagliato)")
print(f"   per protocollo: {dict(agg)}")
giorni=L*12/86400
if giorni < 3:
    print(f"   -> servono almeno 3 giorni di copertura prima di citare un tasso")
# CONTROLLO RIMANDATO (28/10): su finestre corte non si distingue «raro» da
# «firma sbagliata». Tutti e 4 i contratti sono vivi e attivi; solo Aave ha
# sparato. Se dopo 3+ giorni di copertura un protocollo e' ancora a zero
# mentre gli altri no, allora e' la mia configurazione, non la realta'.
if giorni >= 3:
    muti=[k for k in PROT if agg.get(k,0)==0]
    if muti and sum(agg.values())>0:
        print(f"\n   ATTENZIONE: dopo {giorni:.1f} giorni di copertura questi")
        print(f"   protocolli non hanno MAI sparato: {muti}")
        print(f"   I contratti sono vivi: quindi e' probabile che sia sbagliata")
        print(f"   la FIRMA dell'evento, non che manchino le liquidazioni.")
        print(f"   Verificare l'ABI prima di concludere che Aave e' tutto.")
