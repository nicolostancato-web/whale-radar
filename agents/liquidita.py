"""Chi toglie e chi mette la liquidita': la porta da cui il denaro esce senza passare dagli scambi.

PERCHE'. Misurando i flussi degli swap risulta che chi entra nei primi blocchi ci rimette e chi
entra dopo e' in pareggio. Ma quel conto vede SOLO i soldi che passano dagli swap: **chi toglie la
liquidita' non fa uno swap**. Serve anche per sapere CHI ha lanciato il token — chi mette la
liquidita' la prima volta.

Su Uniswap V4 l'evento e' `ModifyLiquidity` sul PoolManager. Firma verificata su pool veri:
ModifyLiquidity(bytes32,address,int24,int24,int256,bytes32) — quattro parole nei dati, poolId e
mittente nei topic.

DUE DOMANDE DIVERSE, da tenere separate:
  - ritiro PRIMA della nostra decisione -> potrebbe essere un filtro utilizzabile
  - ritiro DOPO -> spiega il meccanismo, ma non si puo' usare per decidere

SCRITTO DUE VOLTE (25/09): la prima versione viveva solo sul Mac e si e' persa con una pulizia del
disco. **Pubblica subito quello che scrivi**, anche se sembra provvisorio.
"""
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keccak import keccak256                                   # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
RPC = {"base": "https://mainnet.base.org",
       "robinhood": "https://rpc.mainnet.chain.robinhood.com"}
POOLMANAGER = {"base": "0x498581ff718922c3f8e6a244956af099b2652b2b",
               "robinhood": "0x8366a39cc670b4001a1121b8f6a443a643e40951"}
T_MOD = "0x" + keccak256(
    b"ModifyLiquidity(bytes32,address,int24,int24,int256,bytes32)").hex()


def _con_segno(parola):
    """Un intero a 256 bit CON SEGNO. Senza questo, un ritiro sembra un deposito enorme."""
    v = int(parola, 16)
    return v - (1 << 256) if v >= (1 << 255) else v


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


def movimenti(pool_id, da_blocco, a_blocco, passo=15000):
    """Tutti i movimenti di liquidita' del pool.

    Torna None se il nodo non risponde: «non ho potuto guardare» NON e' «non e' successo niente».
    """
    pm = POOLMANAGER.get(CHAIN)
    if not pm:
        return None
    fuori = []
    cur = da_blocco
    while cur <= a_blocco:
        fine = min(a_blocco, cur + passo)
        k = logs({"fromBlock": hex(cur), "toBlock": hex(fine),
                  "address": pm, "topics": [T_MOD, pool_id]})
        if k is None:
            return None
        for ev in k:
            d = ev["data"][2:]
            parole = [d[i * 64:(i + 1) * 64] for i in range(len(d) // 64)]
            if len(parole) < 3:
                continue
            fuori.append({"blocco": int(ev["blockNumber"], 16),
                          "chi": "0x" + ev["topics"][2][-40:] if len(ev["topics"]) > 2 else None,
                          "delta": _con_segno(parole[2])})
        cur = fine + 1
    return fuori
