"""Quanto ha GUADAGNATO ognuno: il conto in dollari, persona per persona.

PERCHE' ESISTE (3/10, domanda di Nicolo'): «questi wallet piccoli fanno dei profitti loro?»

E' la domanda che non avevo fatto. Finora misuravo **cosa succede al pool** toccato da una
flotta — cioe' cosa guadagneremmo NOI comprando al quinto scambio. Lui chiede se guadagnano
LORO, che e' diverso e dice una cosa in piu':

  · se loro guadagnano e noi no, escono prima di noi: sono estrattori, e il valore e' sapere
    quando NON comprare;
  · se loro guadagnano e il prezzo sale anche dopo, si possono seguire.

COSA CONTA E COSA NO. Si somma la VALUTA entrata e uscita dalle loro mani, in dollari, usando
la valuta del pool e i suoi decimali. Ma un portafoglio che ha comprato e non ha ancora venduto
ha un conto NEGATIVO che non e' una perdita: e' una posizione aperta. Per questo si tiene
separato:
  · `speso` e `incassato`, in dollari;
  · `chiuso`: quanto ha incassato di cio' che ha comprato in pool dove ha ANCHE venduto;
  · `aperto`: quanto ha speso in pool dove non ha mai venduto.
Confondere i due e' il modo piu' rapido di dichiarare perdente chi sta ancora dentro.

COSTA ZERO CHIAMATE: legge i file degli scambi che abbiamo gia' e la mappa delle persone.
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

CHAIN = os.environ.get("CHAIN", "base")
BUDGET = int(os.environ.get("BUDGET_SEC", 1080))
BASE = f"data/multichain/{CHAIN}"
CARTELLE = ("storico", "vivo", "trades")


def persone():
    p = f"{BASE}/iniziatori.json.gz"
    if not os.path.exists(p):
        raise SystemExit(f"PROFITTO | manca {p}: senza sapere chi ha firmato non conto niente")
    return {k.lower(): v for k, v in
            json.load(gzip.open(p, "rt")).get("da", {}).items()}


def main():
    t0 = time.time()
    mappa = persone()
    verso = V.carica(CHAIN)
    print(f"PROFITTO | {CHAIN}: {len(mappa):,} transazioni con persona nota, "
          f"{len(verso):,} pool con il verso noto", flush=True)
    conti = {}
    letti = saltati = senza_valuta = 0
    assurdi = [0, 0.0]
    giro_piu_lungo = 0.0
    file_tutti = []
    for c in CARTELLE:
        file_tutti += sorted(glob.glob(os.path.join(BASE, c, "*.jsonl.gz")))
    file_tutti = AF.mia_parte(file_tutti)
    i_f, n_f = AF.quale_fetta()
    if n_f > 1:
        print(f"PROFITTO | fetta {i_f+1} di {n_f}: {len(file_tutti):,} file", flush=True)
    for percorso in file_tutti:
        passato = time.time() - t0
        if passato + giro_piu_lungo >= BUDGET:
            print(f"PROFITTO | mi fermo a {passato/60:.0f} min per fare in tempo a salvare",
                  flush=True)
            break
        inizio = time.time()
        pool = os.path.basename(percorso).split(".")[0]
        vp = V.valuta_lato(CHAIN, pool)
        if not vp:
            senza_valuta += 1
            continue
        lato, decimali, in_dollari = vp
        try:
            righe = [json.loads(l) for l in gzip.open(percorso, "rt") if l.strip()]
        except Exception:
            continue
        letti += 1
        # per pool: chi ha comprato e chi ha venduto, per distinguere chiuso da aperto
        per_pool = {}
        for x in righe:
            chi = mappa.get(str(x.get("tx", "")).lower())
            if not chi:
                continue
            q = V.quantita_lato(x, lato)
            if q <= 0:
                continue
            dollari = (q / (10 ** decimali)) * in_dollari
            # UN IMPORTO ASSURDO SI DICHIARA, NON SI SOMMA (3/10). Prima bastava un pool col
            # verso sbagliato per attribuire dodici milioni di dollari a un indirizzo che non
            # ha mai fatto una transazione, e quel numero finiva in un totale senza farsi
            # vedere. Sopra il milione per singolo scambio su una moneta appena nata non e'
            # un affare: e' un'unita' sbagliata. Si conta a parte e si stampa.
            if dollari > 1_000_000:
                assurdi[0] += 1
                assurdi[1] += dollari
                continue
            d = per_pool.setdefault(chi, {"compra": 0.0, "vende": 0.0})
            d["vende" if not V.entra_valuta(x, lato) else "compra"] += dollari
        for chi, d in per_pool.items():
            c = conti.setdefault(chi, {"speso": 0.0, "incassato": 0.0,
                                       "chiuso_speso": 0.0, "chiuso_incassato": 0.0,
                                       "aperto": 0.0, "pool": 0, "pool_chiusi": 0})
            c["speso"] += d["compra"]
            c["incassato"] += d["vende"]
            c["pool"] += 1
            if d["vende"] > 0 and d["compra"] > 0:
                c["chiuso_speso"] += d["compra"]
                c["chiuso_incassato"] += d["vende"]
                c["pool_chiusi"] += 1
            elif d["compra"] > 0:
                c["aperto"] += d["compra"]
        giro_piu_lungo = max(giro_piu_lungo, time.time() - inizio)
    if not conti:
        print("PROFITTO | nessun conto: NON scrivo un pezzo vuoto", flush=True)
        return
    pezzo = AF.nome_pezzo(BASE, "profitto")
    os.makedirs(BASE, exist_ok=True)
    json.dump({k: {kk: (round(vv, 2) if isinstance(vv, float) else vv)
                   for kk, vv in v.items()} for k, v in conti.items()}, open(pezzo, "w"))
    chiusi = [c for c in conti.values() if c["pool_chiusi"] >= 1]
    vincenti = [c for c in chiusi if c["chiuso_incassato"] > c["chiuso_speso"]]
    if assurdi[0]:
        print(f"PROFITTO | {assurdi[0]:,} scambi sopra il milione di dollari SCARTATI "
              f"(${assurdi[1]:,.0f} in tutto): sono unita' sbagliate, non affari", flush=True)
    print(f"PROFITTO | {CHAIN}: {len(conti):,} persone su {letti:,} pool letti "
          f"({saltati:,} senza verso, {senza_valuta:,} senza valuta nota)", flush=True)
    print(f"PROFITTO | di chi ha almeno un pool CHIUSO ({len(chiusi):,}): "
          f"{len(vincenti):,} in guadagno "
          f"({100*len(vincenti)/max(1,len(chiusi)):.0f}%)", flush=True)


if __name__ == "__main__":
    main()
