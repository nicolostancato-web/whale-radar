"""RIPARA ORARIO — rimette l'istante vero nei record scritti col riferimento che invecchiava.

PERCHE' (16/09, secondo rilievo della revisione esterna). Stamattina ho riparato CHI produce
l'orario e ho scritto un documento sul difetto. Il revisore ha fatto notare la cosa ovvia che non
avevo visto: **documentare un difetto non e' ripararlo**. I record gia' scritti hanno ancora il
`ts` sbagliato fino a 32 minuti, e con quel `ts` hanno gia' deciso la propria `classe`, sono gia'
entrati in unioni e hanno gia' superato o mancato l'embargo.
«Errore 0 secondi» vale solo da stamattina in avanti. Il passato resta sporco finche' non lo si
pulisce o non lo si butta.

PERCHE' SI PUO' FARE. Il campo `blocco` e' esatto — viene dalla catena, non da un calcolo — quindi
l'istante vero e' sempre recuperabile. E il nodo accetta le chiamate in LOTTO: 25 blocchi in 0,4
secondi, sessanta volte piu' veloce che uno per volta. Una bonifica che sarebbe stata impraticabile
costa ore invece di settimane.

COSA FA, esattamente:
  - per ogni pool, legge i record e raccoglie i blocchi distinti;
  - chiede alla catena gli istanti veri, in lotti;
  - riscrive `ts` con quello vero, e RICALCOLA `ritardo` e `classe` di conseguenza;
  - lascia intatti blocco, tx, li, bh, acq e le quantita', che erano gia' giusti;
  - scrive quanti record ha corretto e di quanto, cosi' la bonifica stessa e' verificabile.

I record di cui la catena non sa dire l'istante NON vengono indovinati: restano com'erano e vengono
contati a parte. Un dato che non si riesce a ripristinare va dichiarato, non inventato una seconda
volta.
"""
import gzip
import json
import os
import time
import urllib.request

# QUANTI BLOCCHI PER LOTTO, MISURATO (16/09, seconda misura). Stamattina base aveva
# rifiutato un lotto da 25 e ne avevo concluso «base non fa i lotti»: una conclusione
# affrettata da UN solo tentativo, che e' costata dieci volte la velocita'.
# Riprovato per gradi: 2 -> ok, 5 -> ok, 10 -> ok in 2,1s, 25 -> rifiuta (-32014).
# Il limite non e' «niente lotti», e' «lotti fino a dieci». Una domanda fatta una volta
# sola da una risposta sola, non una regola.
RPC = {"base": ("https://mainnet.base.org", 10),
       "robinhood": ("https://rpc.mainnet.chain.robinhood.com", 100)}
CHAIN = os.environ.get("CHAIN", "robinhood")
BUDGET = int(os.environ.get("BUDGET_SEC", 400))
SOGLIA_PIT = int(os.environ.get("SOGLIA_PIT", 900))
CK = f"data/multichain/{CHAIN}/riparazione_ckpt.json"
t0 = time.time()


def istanti(url, blocchi, per_lotto):
    """Gli istanti veri, a lotti se il nodo li accetta."""
    out = {}
    falliti = set()
    i = 0
    while i < len(blocchi):
        gruppo = blocchi[i:i + per_lotto]
        if per_lotto > 1:
            req = [{"jsonrpc": "2.0", "method": "eth_getBlockByNumber",
                    "params": [hex(b), False], "id": k} for k, b in enumerate(gruppo)]
        else:
            req = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber",
                   "params": [hex(gruppo[0]), False], "id": 0}
        try:
            r = urllib.request.Request(url, data=json.dumps(req).encode(),
                                       headers={"Content-Type": "application/json",
                                                "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=90) as x:
                d = json.load(x)
        except Exception:
            # NON PROVATO NON E' IRRECUPERABILE (16/09). Un lotto che fallisce — timeout, 429,
            # nodo occupato — faceva saltare i suoi blocchi, e i record relativi finivano contati
            # come «irrecuperabili»: 3.162 su un giro solo, un numero che dice «questi dati sono
            # perduti» quando la verita' e' «non ho insistito».
            # E' lo stesso errore che avevo gia' corretto nel controllo di canonicita' stamattina.
            # Farlo due volte in un giorno vuol dire che non era una disattenzione: e' un riflesso,
            # e va tolto ovunque. Qui si riprova, si stringe il lotto, e si rinuncia solo dopo.
            if per_lotto > 1:
                per_lotto = max(1, per_lotto // 4)
                time.sleep(4)
                continue                      # stesso gruppo, lotti piu' piccoli
            tentato_uno = out.get(gruppo[0])
            if tentato_uno is None and gruppo[0] not in falliti:
                falliti.add(gruppo[0])
                time.sleep(4)
                continue                      # una seconda possibilita', poi basta
            i += per_lotto
            continue
        items = d if isinstance(d, list) else [d]
        for item in items:
            if not isinstance(item, dict):
                continue
            k = item.get("id")
            res = item.get("result")
            if isinstance(k, int) and 0 <= k < len(gruppo) and res and res.get("timestamp"):
                out[gruppo[k]] = int(res["timestamp"], 16)
        i += per_lotto
        time.sleep(0.2)
    return out


def main():
    url, per_lotto = RPC.get(CHAIN, (None, None))
    if not url:
        print(f"RIPARA | {CHAIN}: nessun nodo", flush=True)
        return
    d = f"data/multichain/{CHAIN}/vivo"
    if not os.path.isdir(d):
        print(f"RIPARA | {CHAIN}: niente da riparare", flush=True)
        return
    ck = {}
    if os.path.exists(CK):
        try:
            ck = json.load(open(CK))
        except Exception:
            ck = {}
    fatti = set(ck.get("fatti", []))

    corretti = invariati = irrecuperabili = pool_fatti = 0
    scarti = []
    for fn in sorted(os.listdir(d)):
        if time.time() - t0 > BUDGET:
            break
        if fn in fatti:
            continue
        p = os.path.join(d, fn)
        try:
            righe = [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]
        except Exception:
            fatti.add(fn)
            continue
        if not righe:
            fatti.add(fn)
            continue
        # solo i record del vecchio produttore: quelli nuovi portano gia' il ritardo scritto
        da_fare = [r for r in righe if r.get("ritardo") is None and r.get("blocco")]
        if not da_fare:
            fatti.add(fn)
            continue
        blocchi = sorted({r["blocco"] for r in da_fare})
        veri = istanti(url, blocchi, per_lotto)
        cambiato = False
        for r in righe:
            if r.get("ritardo") is not None or not r.get("blocco"):
                continue
            v = veri.get(r["blocco"])
            if v is None:
                irrecuperabili += 1
                continue
            vecchio = r.get("ts")
            if vecchio and abs(vecchio - v) > 2:
                scarti.append(abs(vecchio - v))
                corretti += 1
            else:
                invariati += 1
            r["ts"] = v
            acq = r.get("acq") or v
            r["ritardo"] = max(0, acq - v)
            r["classe"] = "point-in-time" if r["ritardo"] <= SOGLIA_PIT else "ricostruzione-storica"
            r["orario"] = "catena"        # da dove viene l'istante, scritto nel record
            cambiato = True
        if cambiato:
            tmp = p + ".tmp"
            try:
                with gzip.open(tmp, "wt") as fo:
                    for r in sorted(righe, key=lambda x: (x.get("blocco", 0), x.get("li", 0))):
                        fo.write(json.dumps(r) + "\n")
                os.replace(tmp, p)
            except Exception:
                try:
                    os.remove(tmp)
                except Exception:
                    pass
                continue
        fatti.add(fn)
        pool_fatti += 1

    ck["fatti"] = sorted(fatti)
    try:
        json.dump(ck, open(CK, "w"))
    except Exception:
        pass
    tot = len(os.listdir(d))
    med = sorted(scarti)[len(scarti) // 2] / 60 if scarti else 0
    print(f"RIPARA | {CHAIN}: {pool_fatti} pool in questo giro, {len(fatti)}/{tot} in tutto | "
          f"corretti {corretti} record (scarto mediano {med:.1f} min), gia' giusti {invariati}, "
          f"irrecuperabili {irrecuperabili}", flush=True)


if __name__ == "__main__":
    main()
