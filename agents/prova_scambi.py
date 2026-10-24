"""La prova giusta: i nostri scambi registrati esistono negli eventi della pool?

PERCHE' IL CANCELLO PRECEDENTE ERA ROTTO (6/10). `prova_sulla_chain.py` cerca i trasferimenti
del GETTONE nel portafoglio a cui attribuiamo la posizione. Ha bocciato 10 casi su 10 — e poi
ho capito perche': in un mercato automatico il gettone in uscita viene mandato al
**destinatario** dello scambio, che e' un router o un contratto del bot, **mai al firmatario**.
Verificato: il destinatario di uno di quei casi e' `is_contract=True`.
Quindi il firmatario non riceve il gettone NEMMENO QUANDO IL DATO E' GIUSTO: il controllo
bocciava tutto, e un controllo che boccia tutto non e' severo, e' rotto. Terza volta che un mio
controllo guarda la fonte sbagliata (1/10 la guardia sugli atomi, 4/10 la menzione invece
dell'esecuzione).

LA PROVA CHE FUNZIONA, e che e' anche quella che Nicolo' puo' rifare a mano: non «chi tiene il
gettone» ma **«questo scambio e' avvenuto?»**. Si prendono gli eventi di scambio emessi da
QUELLA pool, si guarda chi ha firmato le transazioni, e si confronta con cio' che abbiamo
registrato. Se diciamo che il portafoglio X ha fatto N scambi in quella pool e sulla chain non
c'e' traccia, il dato e' falso. Se ci sono, la posizione e' reale.
Non richiede di sapere chi controlla quale contratto — che e' un problema di identita' aperto —
e usa l'endpoint /logs, che non ci strozza.

COSTO ZERO: esploratore pubblico.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

ESPLORATORI = {"base": "https://base.blockscout.com",
               "robinhood": "https://robinhoodchain.blockscout.com"}
SWAP = {"0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822": "V2",
        "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67": "V3",
        "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f": "V4"}
H = {"User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/129.0 Safari/537.36"),
     "Accept": "application/json"}
PAUSA = float(os.environ.get("PAUSA", 1.0))
TX_MAX = int(os.environ.get("TX_MAX", 12))


def _get(u, intest, tent=3):
    for i in range(tent):
        try:
            with urllib.request.urlopen(
                    urllib.request.Request(u, headers=intest), timeout=35) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 403, 503) and i < tent - 1:
                time.sleep(15)
                continue
            raise
        except Exception:
            if i < tent - 1:
                time.sleep(10)
                continue
            raise
    return None


def controlla(chain, portafoglio, pool):
    """Esistono scambi in quella pool firmati da quel portafoglio?"""
    base = ESPLORATORI.get(chain)
    if not base:
        return {"verdetto": "NON POSSO CONTROLLARE", "perche": f"nessun esploratore per {chain}"}
    if len(pool) != 42:
        return {"verdetto": "NON POSSO CONTROLLARE",
                "perche": "pool V4: e' un id dentro il PoolManager, non un contratto, "
                          "quindi non ha un elenco di log proprio da interrogare"}
    intest = dict(H)
    intest["Referer"] = base + "/"
    w = portafoglio.lower()
    try:
        lg = _get(f"{base}/api/v2/addresses/{pool.lower()}/logs", intest)
    except Exception as e:
        return {"verdetto": "NON POSSO CONTROLLARE",
                "perche": f"l'esploratore non ha risposto ({type(e).__name__}): "
                          f"non sapere non e' sapere"}
    sw = [l for l in (lg.get("items") or []) if (l.get("topics") or [None])[0] in SWAP]
    if not sw:
        return {"verdetto": "NON POSSO CONTROLLARE",
                "perche": "nessuno scambio nella pagina di log della pool"}
    firmatari = {}
    guardate = 0
    for l in sw[:TX_MAX]:
        tx = l.get("transaction_hash") or l.get("tx_hash")
        if not tx:
            continue
        try:
            t = _get(f"{base}/api/v2/transactions/{tx}", intest)
        except Exception:
            continue
        guardate += 1
        fr = str((t.get("from") or {}).get("hash") or "").lower()
        firmatari[fr] = firmatari.get(fr, 0) + 1
        time.sleep(PAUSA)
    if not guardate:
        return {"verdetto": "NON POSSO CONTROLLARE",
                "perche": "non ho potuto leggere nessuna transazione"}
    if w in firmatari:
        return {"verdetto": "VERO", "scambi_suoi": firmatari[w],
                "transazioni_guardate": guardate,
                "perche": f"ha firmato {firmatari[w]} degli ultimi {guardate} scambi di "
                          f"questa pool: la posizione e' reale"}
    return {"verdetto": "NON NELLA FINESTRA", "transazioni_guardate": guardate,
            "firmatari_visti": len(firmatari),
            "perche": f"non e' fra i firmatari degli ultimi {guardate} scambi, ma la pool ne "
                      f"ha molti di piu': NON si conclude che sia falso. Serve scorrere le "
                      f"pagine o cercare le sue transazioni direttamente."}


def main():
    if len(sys.argv) < 4:
        print("uso: prova_scambi.py <chain> <portafoglio> <pool>")
        return
    print(json.dumps(controlla(sys.argv[1], sys.argv[2], sys.argv[3]),
                     indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
