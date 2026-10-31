"""LA PROVA DEI PROFESSIONISTI: Flashbots accetta e simula il nostro pacchetto?

Se si', vuol dire che quel pacchetto SAREBBE ENTRATO nel blocco: e' la
definizione tecnica di «stare nel primo blocco».

Catena: compone la chiamata -> firma la transazione -> la manda a Flashbots
per SIMULAZIONE (eth_callBundle). Nessuna esecuzione vera: la simulazione
legge lo stato reale e dice cosa succederebbe.
"""
import json, os, subprocess, time, urllib.request, sys
sys.path.insert(0,"agents")
from keccak import firma
FOUNDRY=os.path.expanduser("~/.foundry/bin")
CONTRATTO="0xE30b58692FB7a1a417d3e0F1F5585a8Bc4D51212"
U="https://ethereum-rpc.publicnode.com"
CHIAVE_ID=".chiavi/identita"
def cast(*a):
    return subprocess.run([f"{FOUNDRY}/cast",*a], capture_output=True, text=True)
def rpc(m,p):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    r=urllib.request.Request(U,data=c,headers={
      "content-type":"application/json","user-agent":"Mozilla/5.0"})
    return json.load(urllib.request.urlopen(r,timeout=20)).get("result")
# 1) una transazione firmata, verso il nostro contratto
K=subprocess.run(["grep","-oE","Private key wallet 1 0x[a-fA-F0-9]{64}",
                  os.path.expanduser("~/Documents/b2b-finder-credentials.txt")],
                 capture_output=True, text=True).stdout.strip().split()[-1]
mio=cast("wallet","address","--private-key",K).stdout.strip()
nonce=int(rpc("eth_getTransactionCount",[mio,"pending"]),16)
bl=int(rpc("eth_blockNumber",[]),16)
print(f"   operativo {mio}  nonce {nonce}  blocco {bl}")
# chiamata innocua al contratto: legge la cassa. Serve a provare la CATENA,
# non a liquidare: la posizione non e' ancora caduta.
dati="0x"+firma("cassa()")[2:10]
# lo strumento cercava un nodo sul computer locale: va detto quale usare
r=cast("mktx", CONTRATTO, dati, "--private-key", K, "--nonce", str(nonce),
       "--gas-limit","100000", "--gas-price","2000000000",
       "--chain","1", "--rpc-url", U)
grezza=r.stdout.strip()
if not grezza.startswith("0x"):
    print(f"   firma fallita: {r.stderr[:200]}"); sys.exit(1)
print(f"   transazione firmata: {len(grezza)} caratteri")
# 2) Flashbots: simulazione del pacchetto
k=open(CHIAVE_ID).read().strip()
ident=cast("wallet","address","--private-key",k).stdout.strip()
def chiedi(metodo, par):
    corpo=json.dumps({"jsonrpc":"2.0","id":1,"method":metodo,"params":par})
    h=cast("keccak",corpo).stdout.strip()
    s=cast("wallet","sign","--private-key",k,"0x"+h.encode().hex()).stdout.strip()
    req=urllib.request.Request("https://relay.flashbots.net", data=corpo.encode(),
        headers={"content-type":"application/json","user-agent":"Mozilla/5.0",
                 "X-Flashbots-Signature": f"{ident}:{s}"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        return {"http": e.code, "corpo": e.read().decode()[:300]}
    except Exception as e:
        return {"errore": str(e)[:120]}
print(f"\n   chiedo a Flashbots di simulare il pacchetto per il blocco {bl+1}...")
risp=chiedi("eth_callBundle", [{"txs":[grezza], "blockNumber":hex(bl+1),
                                "stateBlockNumber":"latest"}])
print(f"   risposta: {json.dumps(risp)[:400]}")
c=json.dumps(risp)
if "results" in c:
    print(f"\n   >>> FLASHBOTS HA SIMULATO IL NOSTRO PACCHETTO <<<")
    print(f"   Tecnicamente possiamo stare nel loro stesso blocco.")
elif "signature" in c.lower():
    print(f"\n   problema di firma")
else:
    print(f"\n   non simulato: vedi risposta sopra")
