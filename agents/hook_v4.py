"""Chi puo' bloccarti l'uscita: i permessi degli hook dei pool Uniswap V4.

PERCHE' (24/09, dalla ricerca su GitHub delegata a Grok). Su V4 un pool puo' impedire di vendere
ANCHE avendo scambi veri da molti portafogli diversi: il blocco non sta negli swap, sta in un
contratto aggiuntivo (l'hook) i cui permessi sono scritti nei BIT BASSI del suo indirizzo.
`beforeSwap` puo' far fallire una sola direzione; `afterSwapReturnDelta` puo' trattenere l'output.

Il nostro controllo di vendibilita' vede solo chi non ha MAI venduto. Questa famiglia di trappole
gli sfugge — e sarebbe proprio dove si concentrano i guadagni finti.

L'indirizzo dell'hook sta nell'evento `Initialize` del PoolManager. Hook a zero = pool vaniglia,
nessun blocco possibile.
"""
import gzip
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keccak import keccak256                                   # noqa: E402

CHAIN = os.environ.get("CHAIN", "base")
RPC = {"base": "https://mainnet.base.org",
       "robinhood": "https://rpc.mainnet.chain.robinhood.com"}
# I PoolManager NON sono stati cercati fuori: stanno gia' nei nostri dati, nel campo `mgr` di
# ogni scambio V4. Confermati contando le occorrenze su 60 pool per chain.
POOLMANAGER = {"base": "0x498581ff718922c3f8e6a244956af099b2652b2b",
               "robinhood": "0x8366a39cc670b4001a1121b8f6a443a643e40951"}
T_INIT = "0x" + keccak256(
    b"Initialize(bytes32,address,address,uint24,int24,address,uint160,int24)").hex()

# i permessi, dai bit bassi dell'indirizzo dell'hook (Hooks.sol di Uniswap)
PERMESSI = [(1 << 13, "prima_init"), (1 << 12, "dopo_init"),
            (1 << 11, "prima_liquidita_su"), (1 << 10, "dopo_liquidita_su"),
            (1 << 9, "prima_liquidita_giu"), (1 << 8, "dopo_liquidita_giu"),
            (1 << 7, "PRIMA_SWAP"), (1 << 6, "DOPO_SWAP"),
            (1 << 5, "prima_dono"), (1 << 4, "dopo_dono"),
            (1 << 3, "prima_swap_delta"), (1 << 2, "DOPO_SWAP_TRATTIENE"),
            (1 << 1, "liquidita_su_delta"), (1 << 0, "liquidita_giu_delta")]
# quelli che possono impedirti di USCIRE o mangiarti il ricavato
PERICOLOSI = {"PRIMA_SWAP", "DOPO_SWAP", "DOPO_SWAP_TRATTIENE", "prima_swap_delta"}


# OGNI NODO HA IL SUO LIMITE DI FINESTRA (25/09, trovato dalla sentinella).
# base rifiuta eth_getLogs oltre una certa ampiezza con 413 «eth_getLogs is limited to...». Il
# codice lo leggeva come «il nodo e' giu'» e SALTAVA il pool per sempre: base ferma a 590 mentre
# robinhood arrivava a 36.000, e nessun errore da nessuna parte.
# In positivo: **se il nodo si lamenta dell'ampiezza, stringi la finestra** — non dedurre che il
# dato non esista. E si cammina all'indietro a passi costanti invece di allargare il salto.
PASSO = {"base": 400, "robinhood": 3000}


def logs(par, tentativi=3):
    b = json.dumps({"jsonrpc": "2.0", "method": "eth_getLogs",
                    "id": 1, "params": [par]}).encode()
    attesa = 2
    for k in range(tentativi):
        try:
            r = urllib.request.Request(RPC[CHAIN], data=b,
                                       headers={"Content-Type": "application/json",
                                                "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=40) as x:
                return json.load(x).get("result")
        except Exception:
            if k < tentativi - 1:
                time.sleep(attesa)
                attesa *= 2
    return None


def nascita_di(pool_id, blocco_primo):
    """Hook E COPPIA DI TOKEN, dallo stesso evento. Una chiamata, due informazioni.

    La coppia serve per la TRAPPOLA A DUE POOL (trovata su X il 24/09, caso OLEAF sulla nostra
    chain): un token ha due pool sulla stessa coppia, quella grossa con un hook che fa fallire le
    vendite, quella piccola senza. Gli scanner vendono nella piccola, funziona, e dichiarano il
    token sano — ma la liquidita' e' nella grossa, da cui non si esce.
    E' la trappola perfetta contro il nostro controllo: noi chiediamo «ci sono state vendite
    riuscite?» e la risposta e' si', solo nella pool sbagliata.
    Senza sapere QUALI token scambia ogni pool, quella famiglia e' invisibile.
    """
    pm = POOLMANAGER.get(CHAIN)
    if not pm:
        return None, None, None
    passo = PASSO.get(CHAIN, 3000)
    for giro in range(8):
        alto = blocco_primo + 2 - giro * passo
        if alto <= 1:
            break
        k = logs({"fromBlock": hex(max(1, alto - passo)), "toBlock": hex(alto),
                  "address": pm, "topics": [T_INIT, pool_id]})
        if k:
            ev = k[0]
            d = ev["data"][2:]
            parole = [d[i * 64:(i + 1) * 64] for i in range(len(d) // 64)]
            hook = "0x" + parole[2][-40:] if len(parole) > 2 else None
            # currency0 e currency1 sono indicizzati: stanno nei topic, non nei dati
            tp = ev.get("topics", [])
            c0 = "0x" + tp[2][-40:] if len(tp) > 2 else None
            c1 = "0x" + tp[3][-40:] if len(tp) > 3 else None
            return hook, c0, c1
        if k is None:
            return None, None, None
    return "non_trovato", None, None


def hook_di(pool_id, blocco_primo):
    """L'indirizzo dell'hook, cercato attorno al primo blocco in cui vediamo il pool."""
    pm = POOLMANAGER.get(CHAIN)
    if not pm:
        return None
    passo = PASSO.get(CHAIN, 3000)
    for giro in range(8):
        alto = blocco_primo + 2 - giro * passo
        if alto <= 1:
            break
        k = logs({"fromBlock": hex(max(1, alto - passo)), "toBlock": hex(alto),
                  "address": pm, "topics": [T_INIT, pool_id]})
        if k:
            d = k[0]["data"][2:]
            parole = [d[i * 64:(i + 1) * 64] for i in range(len(d) // 64)]
            if len(parole) > 2:
                return "0x" + parole[2][-40:]
        if k is None:
            return None                      # il nodo non ha risposto: NON e' «nessun hook»
    return "non_trovato"


def descrivi(hook):
    if hook in (None, "non_trovato"):
        return hook, []
    n = int(hook, 16)
    if n == 0:
        return "vaniglia", []
    attivi = [nome for bit, nome in PERMESSI if n & bit]
    return "con_hook", attivi
