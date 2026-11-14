"""DALL'INDIRIZZO AL DENARO: verificare una rivendicazione passando solo dalla chain.

== PERCHE' (8/10/2026) ==

Grok ha trovato su X indirizzi pubblicati con cifre enormi su $PONS. Nicolo' chiede da giorni
portafogli veri, e questi lo sono — ma una rivendicazione non e' un dato: va verificata.

Questo agente fa il percorso completo per un (portafoglio, gettone): quando ha comprato, **quanto
dopo la nascita del gettone**, quanti gettoni ha mosso, e quanto denaro si riesce ad agganciare.

== LE TRE REGOLE IMPARATE FACENDOLO ==

1. **Le finestre, sempre.** La prima lettura chiedeva 81 milioni di blocchi in una volta (il
   limite col filtro sull'indirizzo e' 10 milioni): l'RPC dava errore e il codice leggeva «zero
   trasferimenti». Stavo per dichiarare FALSA una rivendicazione vera. Qui le finestre sono da
   10 milioni e gli errori si **contano**: se una finestra fallisce, non si conclude.
2. **Il denaro si aggancia per corrispondenza, non per registro.** In ogni transazione si cerca
   lo scambio in cui una gamba e' **esattamente** la quantita' di gettoni mossa dal portafoglio:
   l'altra gamba e' il denaro. Nessuna assunzione su quale lato sia la valuta, nessuna dipendenza
   dal nostro elenco di pool (che copriva 2 transazioni su 52).
3. **Vendere non e' trasferire.** Il post stesso indicava DUE indirizzi: uno compra, l'altro
   vende. Un conto fatto sul primo soltanto dice «non ha mai venduto», che e' falso.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as CP                                      # noqa: E402
import prima_la_prova as PP                                  # noqa: E402

TRASF = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
PREZZO_ETH = float(os.environ.get("PREZZO_ETH", "2575.78"))


def _seg(z):
    return z - (1 << 256) if z >= (1 << 255) else z


def _logs_a_finestre(gettone, topics, bn):
    """Tutti i log, a finestre da 10 milioni. (None se una finestra fallisce.)"""
    fuori, b = [], 0
    while b <= bn:
        a = min(bn, b + 9999999)
        r = CP.chiama("eth_getLogs", [{"fromBlock": hex(b), "toBlock": hex(a),
                                       "address": gettone, "topics": topics}])
        if r is None:
            return None
        fuori += r
        b = a + 1
    return fuori


def nascita(gettone, bn):
    """Il blocco del primo trasferimento del gettone: la sua nascita."""
    b = 0
    while b <= bn:
        a = min(bn, b + 999999)
        r = CP.chiama("eth_getLogs", [{"fromBlock": hex(b), "toBlock": hex(a),
                                       "address": gettone, "topics": [TRASF]}])
        if r:
            return min(int(x["blockNumber"], 16) for x in r)
        b = a + 1
    return None


def verifica(portafoglio, gettone, decimali=18):
    w, g = portafoglio.lower(), gettone.lower()
    pad = "0x" + "0" * 24 + w[2:]
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        return {"esito": "la chain non risponde"}
    ric = _logs_a_finestre(g, [TRASF, None, pad], bn)
    inv = _logs_a_finestre(g, [TRASF, pad, None], bn)
    if ric is None or inv is None:
        return {"esito": "lettura incompleta: non concludo"}
    if not ric and not inv:
        return {"esito": "questo indirizzo non ha mai toccato questo gettone",
                "trasferimenti": 0}
    q = lambda x: int(x.get("data", "0x0"), 16) / 10 ** decimali      # noqa: E731
    tx = {}
    for x in ric:
        d = tx.setdefault(x["transactionHash"], {"ric": 0.0, "inv": 0.0,
                                                 "b": int(x["blockNumber"], 16)})
        d["ric"] += q(x)
    for x in inv:
        d = tx.setdefault(x["transactionHash"], {"ric": 0.0, "inv": 0.0,
                                                 "b": int(x["blockNumber"], 16)})
        d["inv"] += q(x)
    speso = incassato = 0.0
    agganciate = non_agganciate = 0
    operazioni = []
    for h, d in sorted(tx.items(), key=lambda kv: kv[1]["b"]):
        r = CP.chiama("eth_getTransactionReceipt", [h])
        if not r:
            continue
        mossi = d["ric"] if d["ric"] > d["inv"] else d["inv"]
        denaro = None
        for l in r["logs"]:
            if (l.get("topics") or [None])[0] not in (PP.SWAP_V4, PP.SWAP_V3, PP.SWAP_V2):
                continue
            n = CP._numeri(l.get("data", "0x"))
            if len(n) < 2:
                continue
            a0, a1 = _seg(n[0]) / 1e18, _seg(n[1]) / 1e18
            for lato_g, lato_d in ((a0, a1), (a1, a0)):
                if mossi > 0 and abs(abs(lato_g) - mossi) / mossi < 0.02:
                    denaro = abs(lato_d)
                    break
            if denaro is not None:
                break
        if denaro is None:
            non_agganciate += 1
            continue
        agganciate += 1
        verso = "compra" if d["ric"] > d["inv"] else "vende"
        if verso == "compra":
            speso += denaro
        else:
            incassato += denaro
        operazioni.append({"blocco": d["b"], "verso": verso, "gettoni": round(mossi, 2),
                           "denaro_eth": round(denaro, 9),
                           "denaro_dollari": round(denaro * PREZZO_ETH, 2), "tx": h})
    nato = nascita(g, bn)
    primo = min(d["b"] for d in tx.values())
    return {
        "esito": "ok", "portafoglio": w, "gettone": g,
        "nascita_gettone": nato, "primo_movimento": primo,
        "blocchi_dopo_la_nascita": (primo - nato) if nato else None,
        "secondi_dopo_la_nascita": round((primo - nato) / 10, 1) if nato else None,
        "gettoni_ricevuti": round(sum(q(x) for x in ric), 2),
        "gettoni_inviati": round(sum(q(x) for x in inv), 2),
        "transazioni": len(tx), "agganciate": agganciate, "non_agganciate": non_agganciate,
        "speso_eth": round(speso, 9), "speso_dollari": round(speso * PREZZO_ETH, 2),
        "incassato_eth": round(incassato, 9),
        "incassato_dollari": round(incassato * PREZZO_ETH, 2),
        "operazioni": operazioni[:40],
        "avvertenza": ("il totale e' misurato solo sulle transazioni agganciate; se sono poche, "
                       "qualunque cifra complessiva sarebbe un calcolo e non una misura"),
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("uso: verifica_una_rivendicazione.py <portafoglio> <gettone>")
        sys.exit(1)
    d = verifica(sys.argv[1], sys.argv[2])
    print(json.dumps(d, indent=1)[:2000])
    if d.get("esito") == "ok":
        print(f"\nnato al blocco {d['nascita_gettone']:,}, primo movimento {d['primo_movimento']:,} "
              f"-> {d['secondi_dopo_la_nascita']} secondi dopo")
        print(f"gettoni: ricevuti {d['gettoni_ricevuti']:,.0f}, inviati {d['gettoni_inviati']:,.0f}")
        print(f"agganciate {d['agganciate']}/{d['transazioni']} transazioni  |  "
              f"speso {d['speso_dollari']:,.0f}$  incassato {d['incassato_dollari']:,.0f}$")
