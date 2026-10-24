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
    arbitri = set()
    pa = f"{BASE}/arbitraggi.json.gz"
    if os.path.exists(pa):
        try:
            _da = json.load(gzip.open(pa, "rt"))
            arbitri = set(_da.get("da", []))
            print(f"PROFITTO | {len(arbitri):,} transazioni di arbitraggio da escludere "
                  f"(elenco {'completo' if _da.get('completo') else 'PARZIALE'})", flush=True)
        except Exception:
            pass
    else:
        print("PROFITTO | ATTENZIONE: manca l'elenco degli arbitraggi "
              "(agents/arbitraggi.py): i bot MEV finirebbero nei conti come posizioni.",
              flush=True)
    conti = {}
    letti = saltati = senza_valuta = 0
    assurdi = [0, 0.0]
    arbitraggi = [0]
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
        # OGNI POSIZIONE HA UNO STATO, E NESSUNA SI BUTTA (4/10, prescrizione di Astra,
        # confermata da Grok per un'altra strada).
        # Astra: «Create il conto al PRIMO EVENTO AMMISSIBILE OSSERVATO, non alla prima chiusura
        # ne' alla prima vittoria. Non convertite un prezzo mancante in zero, ne' una posizione
        # invenduta in un'osservazione esclusa.»
        # Grok, indipendentemente: «Chi vende i vincenti e tiene i perdenti ha un tasso alto sul
        # passato chiuso E sul futuro chiuso, perche' il futuro entra nel campione solo quando
        # viene venduto.»
        # La versione precedente contava SOLO chi aveva comprato e venduto: le posizioni
        # invendute uscivano dal campione, ed e' esattamente il difetto su cui due revisori
        # indipendenti sono arrivati per strade diverse. Le quattro flotte su cinque che non
        # hanno mai venduto erano la massa che quel filtro cancellava.
        # Qui ogni coppia (persona, pool) riceve uno STATO e nessuna sparisce:
        #   chiuso    = ha comprato e venduto, e il residuo in gettoni e' trascurabile
        #   parziale  = ha venduto una parte, ne tiene ancora
        #   aperto    = ha comprato e non ha mai venduto (NON e' una perdita)
        #   solo_uscite = ha solo venduto (gettoni arrivati da altrove: non ricostruibile)
        # Il residuo si tiene in GETTONI, mai valutato al prezzo marginale di una pool
        # illiquida: «un valore ricavato dal prezzo marginale non equivale a denaro incassabile».
        # L'ARBITRAGGIO ATOMICO NON E' UNA POSIZIONE (5/10). L'elenco delle transazioni
        # di arbitraggio lo costruisce agents/arbitraggi.py, che vede TUTTE le pool insieme:
        # un bot compra nella pool A e vende nella pool B, e un agente che legge un file per
        # volta non puo' accorgersene. La mia prima versione lo cercava dentro la singola
        # pool e catturava 2.400 casi su 50.000 posizioni — le briciole — e raddoppiava il
        # lavoro facendo morire cinque fette su otto per tempo scaduto.
        # Un difetto che attraversa i file non si corregge dentro un file che ne legge uno
        # per volta.
        per_pool = {}
        for x in righe:
            _tx = str(x.get("tx", "")).lower()
            if _tx in arbitri:
                arbitraggi[0] += 1
                continue
            chi = mappa.get(_tx)
            if not chi:
                continue
            q = V.quantita_lato(x, lato)
            if q <= 0:
                continue
            dollari = (q / (10 ** decimali)) * in_dollari
            lato_meme = "t1" if lato == "t0" else "t0"
            gettoni = V.quantita_lato(x, lato_meme)
            # UN IMPORTO ASSURDO SI DICHIARA, NON SI SOMMA (3/10). Prima bastava un pool col
            # verso sbagliato per attribuire dodici milioni di dollari a un indirizzo che non
            # ha mai fatto una transazione, e quel numero finiva in un totale senza farsi
            # vedere. Sopra il milione per singolo scambio su una moneta appena nata non e'
            # un affare: e' un'unita' sbagliata. Si conta a parte e si stampa.
            if dollari > 1_000_000:
                assurdi[0] += 1
                assurdi[1] += dollari
                continue
            d = per_pool.setdefault(chi, {"compra": 0.0, "vende": 0.0,
                                          "gettoni_in": 0.0, "gettoni_out": 0.0})
            if V.entra_valuta(x, lato):
                d["compra"] += dollari
                d["gettoni_in"] += gettoni
            else:
                d["vende"] += dollari
                d["gettoni_out"] += gettoni
        for chi, d in per_pool.items():
            c = conti.setdefault(chi, {
                "speso": 0.0, "incassato": 0.0, "pool": 0,
                # i tre mondi, tenuti SEPARATI come chiede Astra
                "chiuso_speso": 0.0, "chiuso_incassato": 0.0, "pool_chiusi": 0,
                "parziale_speso": 0.0, "parziale_incassato": 0.0, "pool_parziali": 0,
                "aperto_speso": 0.0, "pool_aperti": 0,
                "pool_solo_uscite": 0, "solo_uscite_incassato": 0.0,
                # il residuo in GETTONI, non valutato: non e' denaro incassabile
                "gettoni_residui": 0.0,
            })
            c["speso"] += d["compra"]
            c["incassato"] += d["vende"]
            c["pool"] += 1
            residuo = d["gettoni_in"] - d["gettoni_out"]
            c["gettoni_residui"] += max(0.0, residuo)
            # «trascurabile» dichiarato: meno dell'1% di quanto ha comprato
            quasi_tutto_venduto = d["gettoni_in"] > 0 and residuo <= 0.01 * d["gettoni_in"]
            if d["compra"] <= 0 and d["vende"] > 0:
                c["pool_solo_uscite"] += 1
                c["solo_uscite_incassato"] += d["vende"]
            elif d["vende"] > 0 and quasi_tutto_venduto:
                c["chiuso_speso"] += d["compra"]
                c["chiuso_incassato"] += d["vende"]
                c["pool_chiusi"] += 1
            elif d["vende"] > 0:
                c["parziale_speso"] += d["compra"]
                c["parziale_incassato"] += d["vende"]
                c["pool_parziali"] += 1
            else:
                c["aperto_speso"] += d["compra"]
                c["pool_aperti"] += 1
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
    # I TRE MONDI SI RIPORTANO SEPARATI, SEMPRE (4/10, prescrizione di Astra). Un tasso
    # calcolato sui soli pool chiusi e' condizionato dalla politica di uscita: va letto accanto
    # a quante posizioni sono rimaste APERTE, altrimenti dice «questi vincono» quando vuol dire
    # «questi vendono».
    tot_pos = sum(c["pool"] for c in conti.values())
    ch = sum(c["pool_chiusi"] for c in conti.values())
    pa = sum(c["pool_parziali"] for c in conti.values())
    ap = sum(c["pool_aperti"] for c in conti.values())
    so = sum(c["pool_solo_uscite"] for c in conti.values())
    print(f"PROFITTO | {arbitraggi[0]:,} ARBITRAGGI ATOMICI esclusi (stessa transazione, "
          f"compra e vende: non sono posizioni, sono bot MEV)", flush=True)
    print(f"PROFITTO | {tot_pos:,} posizioni: {ch:,} chiuse ({100*ch/max(1,tot_pos):.0f}%), "
          f"{pa:,} parziali ({100*pa/max(1,tot_pos):.0f}%), "
          f"{ap:,} APERTE mai vendute ({100*ap/max(1,tot_pos):.0f}%), "
          f"{so:,} solo uscite", flush=True)
    print(f"PROFITTO | tasso sui soli pool chiusi: {len(vincenti):,}/{len(chiusi):,} = "
          f"{100*len(vincenti)/max(1,len(chiusi)):.0f}% — CONDIZIONATO DALLA CHIUSURA: "
          f"{100*ap/max(1,tot_pos):.0f}% delle posizioni non e' mai stato venduto e NON "
          f"compare in questo tasso", flush=True)


if __name__ == "__main__":
    main()
