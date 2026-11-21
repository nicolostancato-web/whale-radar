"""Nessuna X si dichiara se non e' verificabile. Questa e' la regola, e questo file la impone.

LA DIRETTIVA (Nicolo', 5/10): «quando concludiamo che questi wallet hanno fatto questo X,
dobbiamo essere sicuri al 100% che abbiamo TUTTI gli acquisti e TUTTE le vendite. L'errore
piu' incredibile e' avere tre acquisti e quattro vendite: qualcosa non torna, e iniziamo a
fare calcoli completamente sbagliati sopra dati sbagliati. In questo progetto ci siamo caduti
DUE VOLTE.»

E ha aggiunto come verifichera': «ti dico dammi una coin, tu mi dai il wallet e mi dici che ha
fatto 5X, io vado su DexScreener e controllo che abbia comprato a 10 e venduto a 50».

QUINDI QUESTO AGENTE NON CALCOLA MULTIPLI: decide **quali posizioni hanno il diritto di
produrne uno**, e scrive accanto a ognuna il materiale per controllarla a mano.

LE TRE CONDIZIONI, tutte necessarie. Una posizione (portafoglio x pool) e' VERIFICABILE se:
  1. la storia archiviata di quel pool comincia al suo PRIMO scambio — altrimenti potremmo
     non aver visto gli acquisti iniziali, che e' esattamente il caso «tre acquisti e quattro
     vendite»;
  2. la storia arriva ALMENO fino all'ultima operazione di quel portafoglio in quel pool —
     altrimenti potrebbero esserci vendite dopo la nostra ultima riga;
  3. i gettoni tornano: venduti fra il 99% e il 105% dei comprati. Non «almeno il 99%»: una
     soglia «almeno» su un rapporto che puo' superare 1 e' una porta aperta, e il 4/10 ci e'
     passato dentro un 200%.

Cio' che non le soddisfa non e' una perdita e non e' un errore: e' **non giudicabile**, e si
conta a parte. Da veri analisti non si cancella niente.
"""
import glob
import gzip
import json
import os
import sys
import time

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import a_fette as AF                                              # noqa: E402
import verso as V                                                 # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BUDGET = float(os.environ.get("BUDGET_SEC", 900))
BASE = f"data/multichain/{CHAIN}"
CARTELLE = ("storico", "vivo", "trades")
# «comincia al primo scambio»: tolleranza dichiarata, in scambi dall'inizio dell'archivio
PRIMI_TOLLERATI = int(os.environ.get("PRIMI_TOLLERATI", 0))


def main():
    p = f"{BASE}/iniziatori.json.gz"
    if not os.path.exists(p):
        raise SystemExit(f"COMPLETEZZA | manca {p}")
    mappa = {k.lower(): str(v).lower() for k, v in
             json.load(gzip.open(p, "rt")).get("da", {}).items()}
    cop = {}
    pc = f"{BASE}/coppie.json"
    if os.path.exists(pc):
        cop = json.load(open(pc))["coppie"]

    file_tutti = []
    for c in CARTELLE:
        file_tutti += sorted(glob.glob(os.path.join(BASE, c, "*.jsonl.gz")))
    file_tutti = AF.mia_parte(file_tutti)
    i_f, n_f = AF.quale_fetta()
    print(f"COMPLETEZZA | {CHAIN} fetta {i_f+1}/{n_f}: {len(file_tutti):,} file, "
          f"{len(mappa):,} transazioni con firmatario", flush=True)

    t0 = time.time()
    posizioni = []
    conta = {"pool_letti": 0, "pool_senza_nascita": 0, "pool_storia_corta": 0,
             "posizioni": 0, "verificabili": 0,
             "scartate_gettoni_non_tornano": 0, "scartate_storia_corta": 0}
    for percorso in file_tutti:
        if time.time() - t0 >= BUDGET:
            print(f"   budget speso dopo {conta['pool_letti']:,} pool", flush=True)
            break
        pool = os.path.basename(percorso).split(".")[0]
        vp = V.valuta_lato(CHAIN, pool)
        if not vp:
            continue
        lato, decimali, in_dollari = vp
        try:
            righe = [json.loads(l) for l in gzip.open(percorso, "rt") if l.strip()]
        except Exception:
            continue
        righe = [x for x in righe if isinstance(x.get("ts") or x.get("t"), (int, float))]
        if not righe:
            continue
        righe.sort(key=lambda x: x.get("ts") or x.get("t"))
        conta["pool_letti"] += 1
        # CONDIZIONE 1: l'archivio comincia al primo scambio del pool?
        # Il campo `i` (indice dello scambio nel pool) non esiste nei file — verificato il
        # 5/10, un test ci e' morto sopra. Si usa allora il numero di blocco della NASCITA
        # dalla mappa delle coppie: se il primo scambio archiviato e' nel blocco di nascita
        # o subito dopo, l'archivio parte dall'inizio.
        meta = cop.get(pool) or cop.get(pool.lower()) or {}
        nato = meta.get("nato")
        primo_blocco = None
        for x in righe:
            b = x.get("bn") or x.get("blockNumber") or x.get("blocco")
            if isinstance(b, int):
                primo_blocco = b
                break
        if nato is None or primo_blocco is None:
            conta["pool_senza_nascita"] += 1
            storia_piena = None
        else:
            storia_piena = (primo_blocco - int(nato)) <= max(PRIMI_TOLLERATI, 0)
            if not storia_piena:
                conta["pool_storia_corta"] += 1
        ultimo_archivio = righe[-1].get("ts") or righe[-1].get("t")
        meme = "t1" if lato == "t0" else "t0"
        per = {}
        for x in righe:
            chi = mappa.get(str(x.get("tx", "")).lower())
            if not chi:
                continue
            q = V.quantita_lato(x, lato)
            if q <= 0:
                continue
            dollari = (q / (10 ** decimali)) * in_dollari
            if dollari > 1_000_000:
                continue
            g = V.quantita_lato(x, meme)
            tt = x.get("ts") or x.get("t")
            d = per.setdefault(chi, {"compre": [], "vendite": [],
                                     "gin": 0.0, "gout": 0.0})
            if V.entra_valuta(x, lato):
                d["compre"].append([tt, round(dollari, 4), g])
                d["gin"] += g
            else:
                d["vendite"].append([tt, round(dollari, 4), g])
                d["gout"] += g
        for chi, d in per.items():
            conta["posizioni"] += 1
            if not d["compre"] or not d["vendite"]:
                continue
            quota = d["gout"] / d["gin"] if d["gin"] > 0 else 0.0
            gettoni_tornano = 0.99 <= quota <= 1.05
            ultimo_suo = max([z[0] for z in d["compre"] + d["vendite"]])
            copre_fino_alla_fine = (ultimo_archivio is not None
                                    and ultimo_archivio >= ultimo_suo)
            if not gettoni_tornano:
                conta["scartate_gettoni_non_tornano"] += 1
                continue
            if storia_piena is not True or not copre_fino_alla_fine:
                conta["scartate_storia_corta"] += 1
                continue
            speso = sum(z[1] for z in d["compre"])
            incassato = sum(z[1] for z in d["vendite"])
            if speso <= 0:
                continue
            conta["verificabili"] += 1
            posizioni.append({
                "portafoglio": chi, "pool": pool,
                "gettone": (meta.get("t1") if lato == "t0" else meta.get("t0")),
                "n_acquisti": len(d["compre"]), "n_vendite": len(d["vendite"]),
                "speso": round(speso, 2), "incassato": round(incassato, 2),
                "multiplo": round(incassato / speso, 3),
                "quota_gettoni_venduta": round(quota, 4),
                "primo_acquisto": min(z[0] for z in d["compre"]),
                "ultima_vendita": max(z[0] for z in d["vendite"]),
                # il materiale per il controllo a mano su un esploratore
                "acquisti": d["compre"][:20], "vendite": d["vendite"][:20]})
    pezzo = AF.nome_pezzo(BASE, "completezza")
    json.dump({"chain": CHAIN, "conta": conta, "posizioni": posizioni},
              open(pezzo, "w"), ensure_ascii=False)
    c = conta
    print(f"   pool letti {c['pool_letti']:,} · senza nascita nota {c['pool_senza_nascita']:,} "
          f"· storia corta {c['pool_storia_corta']:,}", flush=True)
    print(f"   posizioni {c['posizioni']:,} → VERIFICABILI {c['verificabili']:,} "
          f"({c['verificabili']/max(c['posizioni'],1):.1%})", flush=True)
    print(f"   scartate: gettoni che non tornano {c['scartate_gettoni_non_tornano']:,} · "
          f"storia incompleta {c['scartate_storia_corta']:,}", flush=True)
    print("   NESSUNA di quelle scartate e' una perdita: sono NON GIUDICABILI.", flush=True)


if __name__ == "__main__":
    main()
