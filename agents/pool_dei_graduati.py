"""IL LATO POOL DELLE MONETE CHE SONO ARRIVATE AL MERCATO, per TUTTI i portafogli.

== PERCHE' ESISTE (6/10/2026) ==

Misurando il rendimento per posizione in fila ho separato le monete «graduate» (che arrivano al
mercato pubblico) da quelle morte sulla curva, ed e' uscito che le graduate rendono MENO:
0,31x contro 0,88x per chi entra primo.

**Quel numero era un artefatto, e per poco non lo pubblicavo.** Per le monete graduate l'uscita
avviene NEL POOL, e noi i pool li seguiamo solo per i 499 portafogli della lista candidati.
Quindi stavo contando come «non ha mai venduto» chiunque fosse uscito in un posto che non
guardavo. E' l'errore inverso della sopravvivenza: un'assenza nei dati letta come «non ha
venduto» invece che come «non ho guardato».

Questo file apre quella finestra. Due numeri lo rendono possibile:
 · le monete graduate sono **5.169 su 675.145 (lo 0,8%)**: pochissime, quindi leggibili tutte;
 · la mappa transazione -> firmatario copre **146.452 portafogli**, non solo i 499.

== COSA PRODUCE ==

Per ogni (portafoglio x pool graduato): quanta valuta e' entrata e uscita, quanti gettoni, e il
nome della valuta. Stesse regole di sempre: la quantita' accanto al suo asset, mai una somma fra
asset diversi, e gli hash delle transazioni come prova verificabile a mano.

== COSTO ==

ZERO: legge i file degli scambi che abbiamo gia'. Nessuna chiamata a pagamento.
"""
import glob
import gzip
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a_fette as AF          # noqa: E402
import verso as V             # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
# I NOMI DELLE CARTELLE SI LEGGONO DALL'AGENTE CHE GIA' FUNZIONA, non si inventano.
# Il 6/10 avevo scritto "scambi,scambi_storici" a memoria: le cartelle vere sono
# storico/vivo/trades, e la corsia ha letto ZERO file dichiarando 11.489 pool da leggere —
# cioe' e' «riuscita» senza fare niente. Un lavoro che riesce leggendo zero file e' peggio di
# uno che fallisce: il secondo lo vedi.
CARTELLE = tuple(os.environ.get("CARTELLE", "storico,vivo,trades").split(","))
BUDGET = int(os.environ.get("BUDGET_SEC", "900"))


def graduate():
    """Le monete nate sulla curva che hanno poi un pool. Senza l'elenco lanci non si sa."""
    p = f"{BASE}/curva_lanci.json.gz"
    if not os.path.exists(p):
        raise SystemExit(f"GRADUATI | manca {p}: senza l'elenco dei lanci non so quali monete "
                         f"sono nate sulla curva, e non lo invento")
    nati = set(t.lower() for t in json.load(gzip.open(p, "rt"))["da"])
    pc = f"{BASE}/coppie.json"
    if not os.path.exists(pc):
        raise SystemExit(f"GRADUATI | manca {pc}")
    pool_di = {}
    for pool, v in json.load(open(pc))["coppie"].items():
        for lato in ("t0", "t1"):
            a = (v.get(lato) or "").lower()
            if a and a != "0x" + "0" * 40 and a in nati:
                pool_di[pool.lower()] = a
    return nati, pool_di


def main():
    if CHAIN != "robinhood":
        print(f"GRADUATI | la curva di Pons e' di robinhood: su {CHAIN} non c'e' niente da "
              f"leggere qui. Su base il lancio funziona in un altro modo e va misurato a parte.")
        return 0
    nati, pool_di = graduate()
    print(f"GRADUATI | {len(nati):,} monete nate sulla curva, {len(pool_di):,} con un pool "
          f"({100*len(pool_di)/max(1,len(nati)):.1f}%)", flush=True)
    if not pool_di:
        print("GRADUATI | nessun pool graduato: non scrivo un file che direbbe «nessuno ha "
              "venduto nel pool». Uno zero ripetuto non e' un dato.")
        return 0

    pi = f"{BASE}/iniziatori.json.gz"
    if not os.path.exists(pi):
        raise SystemExit(f"GRADUATI | manca {pi}: senza sapere chi ha firmato non conto niente")
    mappa = {k.lower(): str(v).lower()
             for k, v in json.load(gzip.open(pi, "rt")).get("da", {}).items()}
    print(f"GRADUATI | {len(mappa):,} transazioni con il firmatario noto", flush=True)

    file_tutti = []
    for c in CARTELLE:
        for pool in pool_di:
            file_tutti += glob.glob(os.path.join(BASE, c, f"{pool}.jsonl.gz"))
    file_tutti = AF.mia_parte(sorted(set(file_tutti)))
    i_f, n_f = AF.quale_fetta()
    print(f"   fetta {i_f+1}/{n_f}: {len(file_tutti):,} file di pool graduati", flush=True)

    t0, letti, senza_verso, fuori = time.time(), 0, 0, {}
    for percorso in file_tutti:
        if time.time() - t0 >= BUDGET:
            print(f"   budget speso dopo {letti:,} file: salvo quello che ho", flush=True)
            break
        pool = os.path.basename(percorso).split(".")[0]
        vp = V.valuta_lato(CHAIN, pool)
        if not vp:
            senza_verso += 1
            continue
        lato, decimali, _ = vp
        valuta = V.indirizzo_valuta(CHAIN, pool, lato)
        meme = "t1" if lato == "t0" else "t0"
        try:
            righe = [json.loads(l) for l in gzip.open(percorso, "rt") if l.strip()]
        except Exception:
            continue
        letti += 1
        qui = {}
        for x in righe:
            chi = mappa.get(str(x.get("tx", "")).lower())
            if not chi:
                continue
            q = V.quantita_lato(x, lato)
            if q <= 0:
                continue
            quanta = q / (10 ** decimali)
            gettoni = V.quantita_lato(x, meme) / 1e18
            d = qui.setdefault(chi, {"vin": 0.0, "vout": 0.0, "gin": 0.0, "gout": 0.0,
                                     "n": 0, "tx": [], "primo": None, "ultimo": None})
            if V.entra_valuta(x, lato):
                d["vin"] += quanta
                d["gin"] += gettoni
            else:
                d["vout"] += quanta
                d["gout"] += gettoni
            d["n"] += 1
            h = str(x.get("tx", ""))
            if h and len(d["tx"]) < 2:
                d["tx"].append(h)
            tt = x.get("ts") or x.get("t")
            if isinstance(tt, (int, float)):
                d["primo"] = tt if d["primo"] is None else min(d["primo"], tt)
                d["ultimo"] = tt if d["ultimo"] is None else max(d["ultimo"], tt)
        for chi, d in qui.items():
            # LA VALUTA DENTRO LA VOCE, non in una nota a margine: e' la regola nata il 6/10
            # dopo aver sommato unita' diverse quattro volte in un giorno.
            fuori[f"{chi}|{pool}"] = {**d, "valuta": valuta, "moneta": pool_di.get(pool)}

    if letti == 0 and file_tutti:
        print(f"GRADUATI | ATTENZIONE: {len(file_tutti):,} file trovati ma ZERO letti. "
              f"Non e' un risultato, e' un guasto.", flush=True)
    elif not file_tutti:
        print(f"GRADUATI | ATTENZIONE: {len(pool_di):,} pool graduati ma NESSUN file trovato "
              f"in {CARTELLE}. Le cartelle esistono? Un lavoro che riesce senza leggere niente "
              f"e' un guasto silenzioso.", flush=True)
    pz = AF.nome_pezzo(BASE, "pool_graduati")
    pz = pz.replace(".json", ".json.gz")
    with gzip.open(pz, "wt") as f:
        json.dump({"acq": int(time.time()), "chain": CHAIN, "fetta": i_f, "fette": n_f,
                   "pool_letti": letti, "pool_senza_verso": senza_verso,
                   "pool_graduati_totali": len(pool_di), "da": fuori}, f)
    print(f"GRADUATI | {len(fuori):,} coppie (portafoglio x pool) da {letti:,} pool "
          f"({senza_verso:,} senza il verso noto, non indovinati) -> {pz}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
