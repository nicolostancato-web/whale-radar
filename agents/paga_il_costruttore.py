"""I vincitori pagano il costruttore? Misurato senza nodo a pagamento.

PERCHE' ESISTE. Era la domanda aperta da giorni: il vincitore studiato (premio
947.639 $) ha pagato ZERO di priority fee, e la sua liquidazione stava in
posizione 2 subito dopo l'aggiornamento Chainlink -- esattamente la forma del
nostro pacchetto. Se paga il costruttore con un trasferimento interno a
block.coinbase, allora senza quel pagamento non entreremo MAI, e tutto il
resto del lavoro e' inutile. I nodi pubblici non danno le chiamate interne.

IL METODO (suggerito da Astra e confermato da Grok, 4/11):
  pagamento al costruttore = (saldo del coinbase a N - saldo a N-1)
                             - somma delle priority fee di tutte le tx
Sotto proof-of-stake l'emissione non passa dal coinbase dell'execution layer,
quindi la differenza e' robusta. Le priority fee si leggono dalle ricevute:
(effectiveGasPrice - baseFeePerGas) x gasUsed.

COME SI LEGGE IL RISULTATO: se nei blocchi con liquidazioni di valore la
differenza e' sistematicamente positiva e nei blocchi normali no, il
pagamento interno c'e' e va implementato. Il controllo e' un CONFRONTO fra
due popolazioni, non una misura su un blocco solo: un blocco con differenza
positiva da' solo l'illusione di una risposta (vedi la regola sulla
popolazione dentro la regola).
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pescatore import rpc

D = "data/liquidazioni"
FUORI = f"{D}/paga_il_costruttore.json"


# IL SALDO STORICO NON SI PUO' LEGGERE su nodo pubblico (403: serve un nodo
# d'archivio, che costa). Quindi il metodo del delta-saldo, giusto in teoria,
# qui non si puo' eseguire -- e dirlo e' meglio che ripiegare in silenzio su
# una misura peggiore spacciata per quella buona.
# LA VIA CHE FUNZIONA GRATIS: i relay di MEV-Boost pubblicano quanto il
# costruttore ha PAGATO AL PROPONENTE per ogni blocco. Quel valore e'
# l'incasso totale del blocco. Confrontandolo con la somma delle priority
# fee di tutte le transazioni si ottiene l'extra, cioe' quello che e'
# arrivato per vie diverse dalle commissioni normali: i pagamenti interni a
# block.coinbase.
RELAY = ("https://relay.ultrasound.money", "https://boost-relay.flashbots.net",
         "https://agnostic-relay.net")


def pagato_al_proponente(n):
    """ETH che il costruttore ha pagato al proponente per il blocco n."""
    import urllib.request
    for base in RELAY:
        u = (f"{base}/relay/v1/data/bidtraces/proposer_payload_delivered"
             f"?block_number={n}")
        try:
            r = urllib.request.Request(u, headers={"user-agent": "Mozilla/5.0"})
            d = json.load(urllib.request.urlopen(r, timeout=25))
        except Exception:
            continue
        if d:
            return int(d[0]["value"]) / 1e18, d[0].get("builder_pubkey", "")[:14]
    return None, None


def priority_del_blocco(n):
    """Somma delle priority fee, piu' i trasferimenti espliciti al coinbase."""
    b = rpc("eth_getBlockByNumber", [hex(n), True])
    if not b or not b.get("transactions"):
        return None
    base = int(b["baseFeePerGas"], 16)
    cb = b["miner"].lower()
    rr = rpc("eth_getBlockReceipts", [hex(n)])
    if not rr:
        return None
    prio = 0
    for r in rr:
        egp = int(r.get("effectiveGasPrice", "0x0"), 16)
        prio += max(0, egp - base) * int(r.get("gasUsed", "0x0"), 16)
    espliciti = sum(int(t.get("value", "0x0"), 16)
                    for t in b["transactions"]
                    if (t.get("to") or "").lower() == cb)
    return prio / 1e18, espliciti / 1e18, len(b["transactions"]), cb


def pagamento_nel_blocco(n):
    """(extra_eth, pagato_eth, priority_eth, quante_tx) oppure None."""
    pagato, _chi = pagato_al_proponente(n)
    pr = priority_del_blocco(n)
    if pagato is None or pr is None:
        return None
    prio, espliciti, quante, _cb = pr
    return pagato - prio - espliciti, pagato, prio, quante


def confronta(blocchi_ricchi, blocchi_normali):
    def misura(elenco, etichetta):
        out = []
        for n in elenco:
            r = pagamento_nel_blocco(n)
            if r is None:
                print(f"   {etichetta} {n}: la rete non ha risposto, salto")
                continue
            extra, pagato, prio, quante = r
            out.append(extra)
            print(f"   {etichetta} {n}: pagato al proponente {pagato:.5f} | "
                  f"priority {prio:.5f} | EXTRA {extra:+.5f} ETH | {quante} tx")
        return out
    a = misura(blocchi_ricchi, "RICCO ")
    b = misura(blocchi_normali, "normale")
    def med(v):
        v = sorted(v)
        return v[len(v) // 2] if v else None
    print()
    ma, mb = med(a), med(b)
    print(f"   blocchi con liquidazione di valore: {len(a)}, "
          f"EXTRA mediano {ma if ma is None else round(ma,5)} ETH")
    print(f"   blocchi normali                   : {len(b)}, "
          f"EXTRA mediano {mb if mb is None else round(mb,5)} ETH")
    return {"ricchi": a, "normali": b, "quando": time.time()}
