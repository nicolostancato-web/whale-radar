"""LA CATENA COMPLETA: dall'indizio al pacchetto consegnato.

Unisce tutti i pezzi provati separatamente:
  orecchio (MEV-Share) -> testa (composizione) -> braccio (contratto)
  -> prenotazione (Flashbots)

Modalita' SILENZIOSA: arriva fino alla SIMULAZIONE e non consegna davvero.
Scrive tutto, cosi' si vede se avremmo prenotato per la posizione giusta e
in quanto tempo.

Il silenziatore e' una riga sola, e toglierlo sara' una decisione di Nicolo'.
"""
import json, os, subprocess, time, threading, urllib.request, sys, socket, collections
sys.path.insert(0,"agents")
from keccak import firma
SILENZIOSO = True
FOUNDRY=os.path.expanduser("~/.foundry/bin")
# L'INDIRIZZO VIENE DA UN SOLO POSTO (4/11 sera). Era scritto a mano in
# dieci file, il sorgente e' cresciuto e il contratto in catena non e' mai
# stato ridistribuito: la calldata chiamava un selettore che il bytecode
# distribuito non aveva, e ~12.000 pacchetti sono morti al primo byte con
# revert vuoto. Vedi agents/indirizzi.py.
from indirizzi import contratto as _dove
CONTRATTO=_dove()
U="https://ethereum-rpc.publicnode.com"
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
AU=firma("AnswerUpdated(int256,uint256,uint256)").lower()
SEL_SALUTE=firma("getUserAccountData(address)")[2:10]
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
ESCLUSI={"0xa1290d69c65a6fe4df752f95823fae25cb99e5a7"}   # rsETH: non si vende
REG="data/liquidazioni/catena.jsonl"
def cast(*a):
    return subprocess.run([f"{FOUNDRY}/cast",*a], capture_output=True, text=True).stdout.strip()
def rpc(m,p,giri=2,tout=10):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=tout))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.15*(g+1))
    return None
K=subprocess.run(["grep","-oE","Private key wallet 1 0x[a-fA-F0-9]{64}",
    os.path.expanduser("~/Documents/b2b-finder-credentials.txt")],
    capture_output=True, text=True).stdout.strip().split()[-1]
OPERATIVO=cast("wallet","address","--private-key",K)
KID=open(".chiavi/identita").read().strip()
IDENT=cast("wallet","address","--private-key",KID)
def flashbots(metodo, par):
    corpo=json.dumps({"jsonrpc":"2.0","id":1,"method":metodo,"params":par})
    h=cast("keccak",corpo)
    s=cast("wallet","sign","--private-key",KID,"0x"+h.encode().hex())
    req=urllib.request.Request("https://relay.flashbots.net", data=corpo.encode(),
        headers={"content-type":"application/json","user-agent":"Mozilla/5.0",
                 "X-Flashbots-Signature": f"{IDENT}:{s}"})
    try: return json.load(urllib.request.urlopen(req, timeout=20))
    except urllib.error.HTTPError as e: return {"http":e.code,"corpo":e.read().decode()[:200]}
    except Exception as e: return {"errore":str(e)[:100]}
def vendita(src,dst,q,sd,dd):
    try:
        r=urllib.request.Request(
            f"https://api.paraswap.io/prices?srcToken={src}&destToken={dst}"
            f"&amount={q}&srcDecimals={sd}&destDecimals={dd}&side=SELL&network=1",
            headers={"user-agent":"Mozilla/5.0","accept":"application/json"})
        pr=json.load(urllib.request.urlopen(r,timeout=12))["priceRoute"]
        rq=urllib.request.Request(
            "https://api.paraswap.io/transactions/1?ignoreChecks=true&ignoreGasEstimate=true",
            data=json.dumps({"srcToken":src,"destToken":dst,"srcAmount":str(q),
                "priceRoute":pr,"userAddress":CONTRATTO,"slippage":100}).encode(),
            headers={"content-type":"application/json","user-agent":"Mozilla/5.0"})
        tx=json.load(urllib.request.urlopen(rq,timeout=12))
        return tx.get("to"), tx.get("data")
    except Exception as e: return None, str(e)[:60]
def salute(a):
    v=rpc("eth_call",[{"to":POOL,"data":"0x"+SEL_SALUTE+a[2:].zfill(64)},"latest"])
    if isinstance(v,str) and len(v)>=2+64*6: return int(v[2:][320:384],16)/1e18
    return None
stato={"blocco":0,"ora":0.0,"nonce":0}
stop=False
def testa_chain():
    while not stop:
        b=rpc("eth_blockNumber",[])
        if b:
            n=int(b,16)
            if n>stato["blocco"]:
                stato["blocco"]=n; stato["ora"]=time.time()
                nn=rpc("eth_getTransactionCount",[OPERATIVO,"pending"])
                if nn: stato["nonce"]=int(nn,16)
        time.sleep(0.6)
threading.Thread(target=testa_chain, daemon=True).start()
time.sleep(8)
comp=json.load(open("data/liquidazioni/composizione.json"))
comp={k:v for k,v in comp.items() if v["garanzia_principale"] not in ESCLUSI}
vicini=sorted(comp.items(), key=lambda x:x[1]["salute"])[:6]
print(f"   operativo {OPERATIVO}  |  identita' {IDENT}")
print(f"   blocco {stato['blocco']}  |  {len(comp)} posizioni, sorveglio le {len(vicini)} piu' vicine")
print(f"   modalita': {'SILENZIOSA — simula, non consegna' if SILENZIOSO else 'ARMATA'}\n")
MINUTI=int(sys.argv[1]) if len(sys.argv)>1 else 40
t0=time.time(); avvisi=0; prezzi=0; prenotazioni=0; accettati=0; tempi=[]
while time.time()-t0 < MINUTI*60:
    try:
        r=urllib.request.Request("https://mev-share.flashbots.net",
            headers={"user-agent":"Mozilla/5.0","accept":"text/event-stream"})
        f=urllib.request.urlopen(r, timeout=25)
        f.fp.raw._sock.settimeout(20)
        while time.time()-t0 < MINUTI*60:
            try: l=f.readline()
            except (socket.timeout, TimeoutError): break
            if not l: break
            s=l.decode("utf-8","ignore").strip()
            if not s.startswith("data:"): continue
            try: d=json.loads(s[5:])
            except Exception: continue
            avvisi+=1
            if not any(t.lower()==AU for lg in (d.get("logs") or [])
                       for t in (lg.get("topics") or [])): continue
            prezzi+=1
            # un prezzo sta per cambiare: si prenota sulle piu' vicine
            tp=time.time()
            indizio=d.get("hash")
            u, c = vicini[0]
            hf=salute(u)
            gar=c["garanzia_principale"]; deb=c["debito_principale"]
            pg=PR.get(gar); pd=PR.get(deb)
            if not pg or not pd: continue
            dus=c["debito_usd"]*0.5
            qg=int(dus*1.07/pg["prezzo_usd"]*10**pg["decimali"])
            sede, dati = vendita(gar, deb, qg, pg["decimali"], pd["decimali"])
            if not sede: continue
            qd=int(dus/pd["prezzo_usd"]*10**pd["decimali"])
            chiamata=cast("calldata",
              "esegui(address,uint256,(address,address,(address,address,bytes,uint256)[],uint256))",
              deb, str(qd), f"({gar},{u},[({gar},{sede},{dati},0)],1)")
            if not chiamata.startswith("0x"): continue
            grezza=subprocess.run([f"{FOUNDRY}/cast","mktx",CONTRATTO,chiamata,
              "--private-key",K,"--nonce",str(stato["nonce"]),"--gas-limit","1200000",
              "--gas-price","3000000000","--chain","1","--rpc-url",U],
              capture_output=True, text=True).stdout.strip()
            if not grezza.startswith("0x"): continue
            prenotazioni+=1
            dt=time.time()-tp
            tempi.append(dt)
            risp=flashbots("eth_callBundle", [{"txs":[grezza],
                "blockNumber":hex(stato["blocco"]+1),"stateBlockNumber":"latest"}])
            ok = "results" in json.dumps(risp)
            if ok: accettati+=1
            riga={"quando":time.strftime("%H:%M:%S",time.gmtime()),
                  "indizio":indizio,"blocco":stato["blocco"]+1,
                  "posizione":u,"salute":hf,
                  "secondi_composizione":round(dt,2),
                  "flashbots_accetta":ok,
                  "consegnato": not SILENZIOSO}
            try:
                with open(REG,"a") as g: g.write(json.dumps(riga)+"\n")
            except OSError: pass
            print(f"   prezzo -> prenotato in {dt:.2f}s  "
                  f"salute {hf:.4f}  Flashbots: {'ACCETTA' if ok else 'no'}")
        try: f.close()
        except Exception: pass
    except Exception as e:
        print(f"   connessione: {str(e)[:40]}"); time.sleep(2)
stop=True
print(f"\n   === {MINUTI} minuti ===")
print(f"   avvisi ricevuti:     {avvisi}")
print(f"   aggiornamenti prezzo: {prezzi}")
print(f"   prenotazioni composte: {prenotazioni}")
print(f"   accettate da Flashbots: {accettati}/{prenotazioni}")
if tempi:
    import statistics as st
    print(f"   tempo di composizione: mediana {st.median(tempi):.2f}s  "
          f"max {max(tempi):.2f}s")
