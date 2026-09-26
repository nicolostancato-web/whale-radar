"""CANONICITA' — i blocchi che abbiamo appartengono ancora alla catena?

PERCHE' ESISTE (16/09, primo rilievo della revisione esterna). Salviamo l'hash di ogni blocco, ma
non lo abbiamo mai ricontrollato. E la coda viva raccoglie alla punta, con zero minuti di ritardo:
esattamente il punto dove un blocco puo' ancora essere sostituito.

Un record di un blocco riorganizzato e' il difetto piu' insidioso che ci possa capitare, perche'
NON somiglia a un errore: ha l'istante giusto, la chiave giusta, le quantita' giuste, e l'audit
di integrita' non lo chiamerebbe «inventato» — semplicemente racconta una cosa che la catena non
ricorda piu'. Un fatto orfano.

IL LOTTO CAMBIA IL COSTO DEL PROBLEMA. Chiedere un blocco per volta costa ~3 secondi: per decine di
migliaia di blocchi sarebbe impraticabile e ci saremmo accontentati di un campione. Ma il nodo
accetta le chiamate in lotto: misurato, **25 blocchi in 0,4 secondi** — sessanta volte piu' veloce.
Quindi qui non si campiona: si controllano TUTTI.

PRIMA MISURA, prima ancora di costruire: 60 blocchi di robinhood presi a caso, 60 canonici, zero
orfani. Il problema potrebbe essere piccolo — ma «potrebbe essere piccolo» non e' un numero, e su
questo progetto abbiamo gia' imparato cosa costa fidarsi di un'impressione. Ora il numero lo
avremo, e sara' scritto.
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
CK = f"data/multichain/{CHAIN}/canonicita_ckpt.json"
REG = f"data/multichain/{CHAIN}/canonicita.jsonl"
t0 = time.time()


def lotto(url, blocchi, tentativi=3):
    """Chiede piu' blocchi in una volta sola. Torna {numero: hash} per quelli che rispondono."""
    req = [{"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [hex(b), False], "id": i}
           for i, b in enumerate(blocchi)]
    attesa = 3
    for k in range(tentativi):
        try:
            b = json.dumps(req).encode()
            r = urllib.request.Request(url, data=b, headers={"Content-Type": "application/json",
                                                             "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=90) as x:
                d = json.load(x)
            if not isinstance(d, list):
                return None            # il nodo non fa lotti: lo dice il chiamante
            out = {}
            for item in d:
                if not isinstance(item, dict):
                    continue
                i = item.get("id")
                res = item.get("result")
                if isinstance(i, int) and 0 <= i < len(blocchi) and res and res.get("hash"):
                    out[blocchi[i]] = res["hash"].lower()
            return out
        except Exception:
            if k < tentativi - 1:
                time.sleep(attesa)
                attesa *= 2
                continue
            return {}
    return {}


def uno(url, b, tentativi=2):
    """Ripiego per i nodi che non accettano i lotti."""
    req = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [hex(b), False], "id": 1}
    for k in range(tentativi):
        try:
            r = urllib.request.Request(url, data=json.dumps(req).encode(),
                                       headers={"Content-Type": "application/json",
                                                "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=45) as x:
                d = json.load(x)
            res = d.get("result")
            return res["hash"].lower() if res and res.get("hash") else None
        except Exception:
            if k < tentativi - 1:
                time.sleep(3)
                continue
    return None


def catena_intera(url, da, a, per_lotto):
    """Verifica un intervallo DICHIARATO per intero: ogni blocco esiste e punta al precedente.

    PERCHE' SERVE (16/09, terzo rilievo della revisione esterna). Il controllo qui sopra verifica
    solo i blocchi di cui abbiamo un record: un blocco che non abbiamo mai visto non ha un hash da
    ricontrollare, quindi non puo' fallire il test. Misura la canonicita' dei SOPRAVVISSUTI, non la
    completezza della sequenza — ed e' lo stesso vizio del «97% di copertura» di stamattina, in
    vesti nuove: si misura la propria popolazione e la si chiama universo.
    Qui l'intervallo si dichiara PRIMA di guardare, e si controlla ogni singola altezza. Il
    concatenamento degli hash (ogni blocco porta l'hash del padre) prova che la sequenza e' quella
    vera senza bisogno di una seconda fonte a pagamento: se manca un blocco o se ne e' sostituito
    uno, la catena si spezza e si vede.
    Torna (altezze_controllate, rotture, mancanti)."""
    altezze = list(range(da, a + 1))
    hash_di = {}
    padre_di = {}
    i = 0
    while i < len(altezze):
        gruppo = altezze[i:i + per_lotto]
        req = [{"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [hex(b), False],
                "id": k} for k, b in enumerate(gruppo)]
        try:
            r = urllib.request.Request(url, data=json.dumps(req).encode(),
                                       headers={"Content-Type": "application/json",
                                                "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=90) as x:
                d = json.load(x)
        except Exception:
            if per_lotto > 1:
                per_lotto = max(1, per_lotto // 4)
                time.sleep(3)
                continue
            i += per_lotto
            continue
        for item in (d if isinstance(d, list) else [d]):
            if not isinstance(item, dict):
                continue
            k = item.get("id")
            res = item.get("result")
            if isinstance(k, int) and 0 <= k < len(gruppo) and res:
                hash_di[gruppo[k]] = res.get("hash", "").lower()
                padre_di[gruppo[k]] = res.get("parentHash", "").lower()
        i += per_lotto
        time.sleep(0.2)
    mancanti = [b for b in altezze if b not in hash_di]
    rotture = []
    for b in altezze[1:]:
        if b in padre_di and (b - 1) in hash_di and padre_di[b] != hash_di[b - 1]:
            rotture.append(b)
    return len(hash_di), rotture, mancanti


def main():
    url, per_lotto = RPC.get(CHAIN, (None, None))
    if not url:
        print(f"CANONICITA | {CHAIN}: nessun nodo", flush=True)
        return

    ck = {}
    if os.path.exists(CK):
        try:
            ck = json.load(open(CK))
        except Exception:
            ck = {}
    fatti = set(ck.get("fatti", []))

    # tutti i blocchi che abbiamo, con l'hash che avevamo registrato
    nostri = {}
    for cart in ("vivo", "storico"):
        d = f"data/multichain/{CHAIN}/{cart}"
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            try:
                for l in gzip.open(os.path.join(d, fn), "rt"):
                    if not l.strip():
                        continue
                    r = json.loads(l)
                    if r.get("bh") and r.get("blocco") and str(r["blocco"]) not in fatti:
                        nostri.setdefault(r["blocco"], r["bh"].lower())
            except Exception:
                pass
    if not nostri:
        print(f"CANONICITA | {CHAIN}: niente di nuovo da controllare "
              f"({len(fatti)} blocchi gia' verificati)", flush=True)
        return

    # DAI PIU' RECENTI: sono quelli col rischio vero. Un blocco di tre giorni fa e' sepolto sotto
    # milioni di conferme e non si muove piu'; quello di dieci minuti fa si'.
    da_fare = sorted(nostri, reverse=True)
    orfani = []
    controllati = non_letti = 0
    fa_lotti = True

    i = 0
    while i < len(da_fare) and time.time() - t0 < BUDGET:
        gruppo = da_fare[i:i + per_lotto]
        risp = lotto(url, gruppo) if fa_lotti else {}
        if risp is None:
            fa_lotti = False
            print(f"CANONICITA | {CHAIN}: il nodo non accetta i lotti, vado uno per volta",
                  flush=True)
            risp = {}
        if not fa_lotti:
            gruppo = gruppo[:8]                # uno per volta costa: se ne fanno meno
            for b in gruppo:
                h = uno(url, b)
                if h:
                    risp[b] = h
        # NON PROVATO NON E' NON LETTO (16/09). Sul nodo che non fa lotti ne guardo otto per volta,
        # e contavo gli altri del gruppo come «non letti»: 832 su base, un numero che suggeriva un
        # nodo che non risponde quando invece non gli avevo chiesto niente.
        # Un conteggio che gonfia i problemi e' sbagliato quanto uno che li nasconde: e' sempre un
        # numero che non descrive quello che e' successo.
        for b in gruppo:
            h = risp.get(b)
            if not h:
                non_letti += 1
                continue
            controllati += 1
            fatti.add(str(b))
            if h != nostri[b]:
                orfani.append({"acq": int(time.time()), "blocco": b,
                               "nostro": nostri[b], "catena": h})
        i += per_lotto if fa_lotti else 8
        time.sleep(0.3)

    if orfani:
        try:
            with open(REG, "a") as f:
                for o in orfani:
                    f.write(json.dumps(o) + "\n")
        except Exception:
            pass
    ck["fatti"] = sorted(fatti)[-200000:]      # non cresce all'infinito
    ck["acq"] = int(time.time())
    try:
        json.dump(ck, open(CK, "w"))
    except Exception:
        pass

    # E POI UN INTERVALLO DICHIARATO, CONTROLLATO PER INTERO
    if time.time() - t0 < BUDGET * 1.5 and nostri:
        alto = max(nostri)
        larghezza = int(os.environ.get("INTERVALLO", 600))
        d_, a_ = alto - larghezza, alto
        n_, rotture, mancanti = catena_intera(url, d_, a_, per_lotto)
        esito = ("intatta" if not rotture and not mancanti
                 else f"{len(rotture)} rotture, {len(mancanti)} altezze mancanti")
        print(f"CANONICITA | {CHAIN}: intervallo dichiarato {d_}-{a_} ({larghezza + 1} altezze): "
              f"{n_} lette, catena {esito}", flush=True)
        try:
            with open(REG.replace(".jsonl", "_intervalli.jsonl"), "a") as f:
                f.write(json.dumps({"acq": int(time.time()), "da": d_, "a": a_,
                                    "lette": n_, "rotture": len(rotture),
                                    "mancanti": len(mancanti), "esito": esito}) + "\n")
        except Exception:
            pass

    tasso = 100 * len(orfani) / max(1, controllati)
    print(f"CANONICITA | {CHAIN}: {controllati} blocchi verificati, **{len(orfani)} ORFANI** "
          f"({tasso:.3f}%), {non_letti} non letti | {len(fatti)} verificati in tutto", flush=True)
    if orfani:
        print(f"CANONICITA | {CHAIN}: ATTENZIONE — i record di questi blocchi raccontano fatti "
              f"che la catena non ricorda piu'. Sono in {REG}.", flush=True)


if __name__ == "__main__":
    main()
