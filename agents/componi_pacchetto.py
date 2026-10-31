"""Composizione e firma del pacchetto per Flashbots.

Il pacchetto dice: «dopo quella transazione annunciata, esegui la mia».
Si firma con una chiave di IDENTITA' — che non e' un portafoglio e non
contiene fondi: serve solo a farsi riconoscere dal relay e a costruirsi
una reputazione.

Qui si compone, si firma e si chiede al relay di SIMULARE. Non si manda
nulla che possa eseguire.
"""
import json, os, subprocess, time, urllib.request, sys
CHIAVE=".chiavi/identita"
FOUNDRY=os.path.expanduser("~/.foundry/bin")
def cast(*a):
    return subprocess.run([f"{FOUNDRY}/cast",*a], capture_output=True, text=True).stdout.strip()
if not os.path.exists(CHIAVE):
    print("manca la chiave di identita"); sys.exit(1)
k=open(CHIAVE).read().strip()
mio=cast("wallet","address","--private-key",k)
print(f"   identita: {mio}\n")
def firma_corpo(corpo:str):
    """Flashbots vuole: indirizzo:firma del TESTO dell'hash del corpo.

    Trappola (29/10): cast avverte che «i messaggi che cominciano per 0x
    vengono decodificati prima di essere firmati». Noi dobbiamo firmare i
    CARATTERI «0xabc...», non i byte che rappresentano. Quindi si passa il
    testo gia' convertito in esadecimale: cast lo ri-decodifica e firma
    esattamente i caratteri giusti.
    """
    h=cast("keccak",corpo)                     # "0xabc..."
    come_testo="0x"+h.encode().hex()           # esadecimale DEI CARATTERI
    s=cast("wallet","sign","--private-key",k,come_testo)
    return f"{mio}:{s}"
def chiedi(metodo, parametri, url="https://relay.flashbots.net"):
    corpo=json.dumps({"jsonrpc":"2.0","id":1,"method":metodo,"params":parametri})
    intest={"content-type":"application/json",
            "X-Flashbots-Signature":firma_corpo(corpo),
            "user-agent":"Mozilla/5.0"}
    try:
        r=urllib.request.Request(url, data=corpo.encode(), headers=intest)
        return json.load(urllib.request.urlopen(r, timeout=25))
    except urllib.error.HTTPError as e:
        try: return {"errore_http": e.code, "corpo": e.read().decode()[:200]}
        except Exception: return {"errore_http": e.code}
    except Exception as e:
        return {"errore": str(e)[:90]}
# blocco corrente
U="https://ethereum-rpc.publicnode.com"
c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
r=urllib.request.Request(U,data=c,headers={"content-type":"application/json","user-agent":"Mozilla/5.0"})
blocco=int(json.load(urllib.request.urlopen(r,timeout=20))["result"],16)
print(f"   blocco corrente {blocco}")
# 1) il relay ci riconosce? (richiesta innocua)
print("\n   1) il relay accetta la nostra firma?")
risp=chiedi("flashbots_getUserStats", [{"blockNumber": hex(blocco)}])
print(f"      {json.dumps(risp)[:200]}")
# 2) forma di un pacchetto che si attacca a un avviso
print("\n   2) forma del pacchetto (non inviato):")
pacchetto={"version":"v0.1",
  "inclusion":{"block":hex(blocco+1),"maxBlock":hex(blocco+3)},
  "body":[{"hash":"0x"+"11"*32},            # il riferimento dell'avviso
          {"tx":"0x"+"22"*100,"canRevert":False}],  # la nostra transazione
  "validity":{"refund":[],"refundConfig":[]}}
print("      " + json.dumps(pacchetto)[:230] + "...")
print("\n   (nessun invio: serviva sapere se il relay ci parla)")

# 3) il comando che useremmo davvero: la SIMULAZIONE di un pacchetto.
#    Se l'errore riguarda i parametri e non l'autorizzazione, siamo dentro.
print("\n   3) simulazione di un pacchetto (eth_callBundle):")
sim=chiedi("eth_callBundle", [{"txs":["0x02f8" + "00"*40],
                               "blockNumber":hex(blocco+1),
                               "stateBlockNumber":"latest"}])
print(f"      {json.dumps(sim)[:260]}")
if isinstance(sim,dict):
    c_=json.dumps(sim)
    if "signature" in c_.lower():
        print("      -> ancora un problema di firma")
    elif "whitelist" in c_.lower():
        print("      -> metodo non ammesso su questo indirizzo")
    else:
        print("      -> AUTENTICATI: l'errore riguarda i dati, non l'identita'")
