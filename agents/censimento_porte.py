#!/usr/bin/env python3
"""QUALI PORTE CONSEGNANO TRANSAZIONI CHE SI POSSONO LEGGERE?

Il 7/11 ho scoperto che drpc, una delle porte che contavamo come buone,
IGNORA la richiesta di transazioni intere e manda solo gli hash -- senza dare
errore, senza avvisare. Per leggere il selettore da un hash servirebbe una
seconda richiesta di rete, cioe' il tempo che nella gara non abbiamo.
Risultato: su 177 campanelle publicnode e' stata prima 177 volte e drpc zero,
e noi credevamo di avere due occhi sulla gara mentre ne avevamo uno.

E' la TERZA volta che il censimento delle porte mi inganna, sempre per lo
stesso motivo: ho misurato lo stadio sbagliato. Prima «si apre la
connessione» (e tenderly si apriva restando muta), poi «consegna messaggi»
(e drpc ne consegna venticinquemila, tutti inutili). Lo stadio giusto, il
solo che conta, e':

    consegna un DIZIONARIO che contiene il campo `input`?

Perche' e' da quel campo che si legge il selettore dell'oracolo senza
chiedere niente a nessuno. Tutto il resto e' traffico.

Non si giudica una porta da come risponde al saluto. Si guarda cosa mette
nel piatto.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from occhio_ws import Ws

CANDIDATE = [
    "wss://ethereum-rpc.publicnode.com",
    "wss://eth.drpc.org",
    "wss://mainnet.gateway.tenderly.co",
    "wss://ethereum.callstaticrpc.com",
    "wss://eth.llamarpc.com",
    "wss://rpc.ankr.com/eth/ws",
    "wss://eth-mainnet.public.blastapi.io",
    "wss://ethereum.blockpi.network/v1/ws/public",
    "wss://eth.merkle.io/ws",
    "wss://mainnet.era.zksync.io/ws",
    "wss://rpc.payload.de",
    "wss://eth.rpc.blxrbdn.com/ws",
    "wss://api.securerpc.com/v1",
    "wss://rpc.flashbots.net/ws",
    "wss://virginia.rpc.blxrbdn.com/ws",
    "wss://eth.public-rpc.com",
]
ATTESA = 12.0


def prova(url):
    """-> (esito, dettaglio). L'esito buono e' 'INTERE'."""
    w = None
    try:
        w = Ws(url)
        w.manda(json.dumps({"jsonrpc": "2.0", "id": 1,
                            "method": "eth_subscribe",
                            "params": ["newPendingTransactions", True]}))
        sub = None
        t0 = time.time()
        while time.time() - t0 < ATTESA:
            m = w.ricevi()
            if not m:
                continue
            r = json.loads(m)
            if r.get("id") == 1:
                if r.get("error"):
                    return "RIFIUTA", str(r["error"])[:70]
                sub = r.get("result")
                continue
            res = (r.get("params") or {}).get("result")
            if res is None:
                continue
            if isinstance(res, dict):
                if "input" in res:
                    return "INTERE", f"{len(res)} campi, input presente"
                return "DIZIONARIO SENZA INPUT", f"campi: {sorted(res)[:6]}"
            return "SOLO HASH", "ignora la richiesta di transazioni intere"
        return ("MUTA", f"sottoscritta ma niente in {ATTESA:.0f}s") if sub \
            else ("NESSUNA RISPOSTA", f"niente in {ATTESA:.0f}s")
    except Exception as e:
        return "ERRORE", f"{type(e).__name__}: {str(e)[:60]}"
    finally:
        if w:
            try:
                w.chiudi()
            except Exception:
                pass


def main():
    fuori = []
    print("   lo stadio che conta: consegna un dizionario col campo input?\n")
    for u in CANDIDATE:
        esito, det = prova(u)
        fuori.append({"porta": u, "esito": esito, "dettaglio": det})
        print("   %-9s %-44s %s" % (esito if esito == "INTERE" else "",
                                    u.split("//")[1], f"{esito} — {det}"))
        time.sleep(0.8)      # NON SI BRUCIA LA FONTE
    buone = [x["porta"] for x in fuori if x["esito"] == "INTERE"]
    print(f"\n   PORTE USABILI PER LA GARA: {len(buone)}")
    for b in buone:
        print("      " + b)
    if len(buone) < 2:
        print("   <<< UN OCCHIO SOLO: se cade, siamo ciechi sulla gara")
    d = "data/liquidazioni"
    tmp = f"{d}/censimento_porte.json.tmp"
    json.dump({"quando": time.time(), "esiti": fuori, "usabili": buone},
              open(tmp, "w"), indent=1)
    os.replace(tmp, f"{d}/censimento_porte.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
