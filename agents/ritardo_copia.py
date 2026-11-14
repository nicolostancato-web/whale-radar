"""Se copiamo N minuti dopo di loro, quanto resta? E' il numero che decide tutto.

PERCHE' (5/10). Sui 42 portafogli bravi di robinhood: 31 operazioni al mese, ~70$ spesi e 134$
di utile per operazione, 2,2 ore di tenuta mediana. Alla loro taglia non c'e' scivolamento,
quindi la capienza non e' il vincolo — l'aveva corretto Nicolo', e aveva ragione.

Resta un solo vincolo, e non e' mai stato misurato: **il ritardo**. Noi non compriamo
nell'istante in cui compra il bot: lo vediamo sulla chain, decidiamo, firmiamo. Se il guadagno
sopravvive a uno, cinque, quindici minuti si copia; se evapora in sessanta secondi, no.

COME SI MISURA, e la regola che evita la bugia piu' facile. Per ogni posizione chiusa di un
portafoglio bravo:
  · si trova il suo PRIMO acquisto in quel pool (istante t);
  · si prende il prezzo al primo scambio avvenuto a t+ritardo o dopo — NON il prezzo a t,
    perche' quello non e' ottenibile da chi arriva dopo;
  · si vende al prezzo del primo scambio avvenuto quando ha venduto LUI (l'ultimo suo scambio
    in quel pool), perche' copiare vuol dire anche uscire quando esce lui;
  · se dopo il ritardo non c'e' nessuno scambio, la posizione NON si scarta: vale -100%,
    perche' significa che non si entrava o non si usciva.
Il prezzo e' sempre quello di uno scambio ARCHIVIATO, mai interpolato: un prezzo inventato fra
due scambi e' la famiglia del segnaposto 1.0 che il 30/09 produsse un falso -35%.
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
BUDGET = int(os.environ.get("BUDGET_SEC", 600))
BASE = f"data/multichain/{CHAIN}"
CARTELLE = ("storico", "vivo", "trades")
RITARDI = [int(x) for x in os.environ.get("RITARDI", "0,60,300,900,3600").split(",")]


def prezzo_a(righe, da_quando, lato, decimali, in_dollari):
    """Prezzo del primo scambio avvenuto a `da_quando` o dopo. None se non ce n'e'."""
    meme = "t1" if lato == "t0" else "t0"
    for x in righe:
        t = x.get("ts") or x.get("t")
        if not isinstance(t, (int, float)) or t < da_quando:
            continue
        q = V.quantita_lato(x, lato)
        g = V.quantita_lato(x, meme)
        if q > 0 and g > 0:
            return ((q / (10 ** decimali)) * in_dollari) / g
    return None


def main():
    if not os.path.exists("data/bravi.json"):
        raise SystemExit("RITARDO | manca data/bravi.json: la lista la costruisce chi_incassa")
    bravi = set(x.lower() for x in json.load(open("data/bravi.json"))["da"].get(CHAIN, []))
    if not bravi:
        print(f"RITARDO | {CHAIN}: nessun bravo in lista")
        return
    p = f"{BASE}/iniziatori.json.gz"
    mappa = {k.lower(): str(v).lower() for k, v in
             json.load(gzip.open(p, "rt")).get("da", {}).items()
             if str(v).lower() in bravi}
    file_tutti = []
    for c in CARTELLE:
        file_tutti += sorted(glob.glob(os.path.join(BASE, c, "*.jsonl.gz")))
    file_tutti = AF.mia_parte(file_tutti)
    i_f, n_f = AF.quale_fetta()
    print(f"RITARDO | {CHAIN} fetta {i_f+1}/{n_f}: {len(bravi)} bravi, "
          f"{len(mappa):,} loro transazioni, {len(file_tutti):,} file", flush=True)

    t0 = time.time()
    esiti = {r: [] for r in RITARDI}
    coppie = []
    quante = 0
    for percorso in file_tutti:
        if time.time() - t0 >= BUDGET:
            print(f"   budget speso: salvo quello che ho", flush=True)
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
        righe.sort(key=lambda x: x.get("ts") or x.get("t"))
        # LE DUE MISURE SULLA STESSA OPERAZIONE (5/10). Prima questa corsia buttava in una
        # lista solo il rapporto di prezzo, senza dire DI CHI e DI QUALE POOL: le due misure
        # — dollari e prezzo — non si potevano unire, e la riconciliazione che Astra ha
        # prescritto era impossibile per come avevo scritto il file, non per mancanza di dati.
        # Un risultato senza la sua chiave non si puo' confrontare con niente: e' la stessa
        # famiglia di «stampare un numero senza il suo denominatore».
        # Ora la stessa passata calcola ANCHE dollari spesi e incassati, e scrive la chiave.
        meme_lato = "t1" if lato == "t0" else "t0"
        suoi = {}
        for x in righe:
            chi = mappa.get(str(x.get("tx", "")).lower())
            if not chi:
                continue
            tt = x.get("ts") or x.get("t")
            d = suoi.setdefault(chi, {"compra": None, "vende": None,
                                      "speso": 0.0, "incassato": 0.0,
                                      "gin": 0.0, "gout": 0.0})
            q = V.quantita_lato(x, lato)
            dollari = (q / (10 ** decimali)) * in_dollari if q > 0 else 0.0
            if dollari > 1_000_000:        # unita' sbagliate, non affari (3/10)
                continue
            g = V.quantita_lato(x, meme_lato)
            if V.entra_valuta(x, lato):
                if d["compra"] is None:
                    d["compra"] = tt
                d["speso"] += dollari
                d["gin"] += g
            else:
                d["vende"] = tt
                d["incassato"] += dollari
                d["gout"] += g
        for chi, d in suoi.items():
            if d["compra"] is None or d["vende"] is None or d["vende"] <= d["compra"]:
                continue
            p_out = prezzo_a(righe, d["vende"], lato, decimali, in_dollari)
            quante += 1
            # la riga di riconciliazione: chiave + le due misure, sulla STESSA operazione
            r0 = RITARDI[0]
            p0 = prezzo_a(righe, d["compra"] + r0, lato, decimali, in_dollari)
            coppie.append({
                "chi": chi, "pool": pool,
                "speso": round(d["speso"], 4), "incassato": round(d["incassato"], 4),
                "mult_dollari": (round(d["incassato"] / d["speso"], 4)
                                 if d["speso"] > 0 else None),
                "mult_prezzo": (round(p_out / p0, 4) if p0 and p_out and p0 > 0 else None),
                "gin": d["gin"], "gout": d["gout"]})
            for r in RITARDI:
                p_in = prezzo_a(righe, d["compra"] + r, lato, decimali, in_dollari)
                # NIENTE PREZZO = NIENTE SCAMBIO = non si entra o non si esce: -100%
                if not p_in or not p_out or p_in <= 0:
                    esiti[r].append(-1.0)
                else:
                    esiti[r].append(p_out / p_in - 1.0)
    pezzo = AF.nome_pezzo(BASE, "ritardo_copia")
    json.dump({"ritardi": RITARDI, "quante": quante,
               "esiti": {str(k): v for k, v in esiti.items()},
               "coppie": coppie}, open(pezzo, "w"))
    print(f"\n   {quante:,} operazioni dei bravi ricostruite")
    print(f"   {'ritardo':>9} {'mediana':>10} {'media':>10} {'in utile':>10}")
    for r in RITARDI:
        v = sorted(esiti[r])
        if len(v) < 20:
            print(f"   {r:8}s   troppo poche ({len(v)})")
            continue
        m = (v[len(v) // 2] if len(v) % 2
             else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2)
        print(f"   {r:8}s {m:9.1%} {sum(v)/len(v):9.1%} "
              f"{sum(1 for z in v if z > 0)/len(v):9.1%}")


if __name__ == "__main__":
    main()
