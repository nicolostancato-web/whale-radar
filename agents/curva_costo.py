#!/usr/bin/env python3
"""
CURVA_COSTO — quanto costa uscire, in funzione di QUANTO E' LIQUIDO il token in quel momento.

Ultima correzione dell'audit avversariale del 03/09, e la piu' importante:

    «non voglio ne' il vecchio 33% fisso, ne' un nuovo 4% fisso, ne' un x3 arbitrario permanente.
     Il costo deve dipendere dallo stato di liquidita' AL MOMENTO DELL'USCITA.»

Aveva ragione due volte. Un costo costante e' comodo e sbagliato: su un pool che gira 50.000 dollari
l'ora, uscire con 25 dollari non si sente; sullo stesso token quando il volume e' crollato a 200,
quei 25 dollari sono meta' del mercato. E lo stop scatta proprio nel secondo caso, mai nel primo.

Come si calibra, con dati che abbiamo gia' e a costo zero:
  - per ogni token misurato su Jupiter conosciamo il costo vero di andata e ritorno
  - dalle nostre candele conosciamo il volume orario di quel token
  - si mette in relazione il costo con il rapporto POSIZIONE/VOLUME e si guarda che forma ha

Non si impone una formula: si misura per fasce e si vede cosa dicono i dati. Se la relazione non
c'e', il verbale lo dice e il moltiplicatore fisso resta — meglio un'assunzione dichiarata che una
curva inventata che sembra scienza.

Scrive CURVA_COSTO.md + la curva dentro data/costo_modello.json. Sola lettura. €0.
"""
import json, os, glob, gzip, time, math, statistics as st

TAGLIE = ("25", "100", "500")
MIN_PER_FASCIA = 8
now = int(time.time())


def volume_all_istante(pool_file_cache, pool, quando, finestra=3600):
    """Il volume nell'ORA PRECEDENTE un certo istante — la STESSA grandezza che usa il backtest.

    CORREZIONE GRAVE (07/09, trovata dal consulente esterno e confermata da una verifica indipendente).
    Prima calibravo la curva sul volume MEDIANO DI TUTTA LA STORIA del token, e poi il backtest la
    applicava al volume dell'ora prima dell'uscita. Due grandezze diverse: e' come tarare una bilancia
    in chili e poi usarla per pesare litri.
    Non e' un dettaglio di precisione. Il volume dei memecoin cade di ordini di grandezza dopo il
    lancio, quindi la mediana storica e' molto piu' alta del volume nel momento in cui esci: ogni
    token finiva in una fascia piu' economica di quella vera, e la pendenza misurata risultava piu'
    piatta del reale. Conseguenza stimata: i costi sui token sottili sottostimati di 2-4 volte.
    Con questa funzione calibrazione e applicazione guardano finalmente la stessa cosa."""
    cs = pool_file_cache.get(pool)
    if not cs: return None
    v = [c[1] for c in cs if quando - finestra <= c[0] < quando and c[1]]
    if v: return sum(v) / len(v)
    # se non abbiamo candele in quella finestra il dato non c'e': meglio scartare la misura che
    # sostituirla con un numero comodo. Un punto in meno e' meglio di un punto sbagliato.
    return None


def candele_per_pool():
    """{pool: [(ts, vol), ...]} — serve per sapere quanto girava un token in un dato momento."""
    out = {}
    for ch in ("solana", "base", "bsc", "robinhood"):
        for d in ("candles", "serie"):
            for f in glob.glob(f"data/multichain/{ch}/{d}/*.jsonl.gz"):
                pool = os.path.basename(f).replace(".jsonl.gz", "").lower()
                if pool in out: continue
                try:
                    cs = []
                    for l in gzip.open(f, "rt"):
                        dd = json.loads(l)
                        if dd.get("vol") is not None: cs.append((int(dd["ts"]), float(dd["vol"])))
                    if cs: out[pool] = sorted(cs)
                except Exception: pass
    return out


def volume_orario():
    """{pool: volume mediano per candela} — resta per il ripiego quando manca il timestamp."""
    out = {}
    for ch in ("solana", "base", "bsc", "robinhood"):
        for d in ("candles", "serie"):
            for f in glob.glob(f"data/multichain/{ch}/{d}/*.jsonl.gz"):
                pool = os.path.basename(f).replace(".jsonl.gz", "").lower()
                if pool in out: continue
                try:
                    v = [float(json.loads(l)["vol"]) for l in gzip.open(f, "rt")
                         if json.loads(l).get("vol")]
                    if len(v) >= 3: out[pool] = st.median(v)
                except Exception: pass
    return out


def token_a_pool():
    inv = {}
    for f in glob.glob("data/multichain/*/token_map.json"):
        try: m = json.load(open(f))
        except Exception: continue
        for pa, tk in m.items():
            inv.setdefault((tk or "").lower(), pa.lower())
    return inv


def main():
    arch = {}
    for x in sorted(glob.glob("data/costi/*.json")) + ["data/costi_archivio.json"]:
        try: arch.update(json.load(open(x)))
        except Exception: pass
    if not arch:
        print("CURVA_COSTO | nessun archivio misure", flush=True); return
    vol = volume_orario(); inv = token_a_pool()

    cand = candele_per_pool()
    punti = []      # (taglia, rapporto posizione/volume, costo osservato)
    scartati = 0
    for mint, t in arch.items():
        pool = inv.get(mint.lower())
        quando = t.get("ts")
        v = volume_all_istante(cand, pool, int(quando)) if (pool and quando) else None
        if not v or v <= 0:
            scartati += 1
            continue
        for s in TAGLIE:
            d = (t.get("size") or {}).get(s) or (t.get("size") or {}).get(int(s))
            if not isinstance(d, dict): continue
            c = d.get("costo_roundtrip_pct")
            if c is None or c >= 50: continue          # le trappole non sono un costo: sono altro
            punti.append((float(s), float(s) / v, c / 100.0))

    L = [f"# 📈 QUANTO COSTA USCIRE, SECONDO QUANTO E' LIQUIDO IL TOKEN",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · {len(punti)} osservazioni "
         f"(misure con il volume dell'ORA in cui sono state prese, non la mediana storica) · €0*", "",
         "> Un costo costante è comodo e sbagliato. Su un pool che gira 50.000 dollari l'ora, uscire",
         "> con 25 dollari non si sente. Sullo stesso token quando il volume è crollato a 200, quei",
         "> 25 dollari sono metà del mercato — **e lo stop scatta proprio lì, mai nel primo caso.**", ""]

    if len(punti) < MIN_PER_FASCIA * 3:
        L += [f"## Non ancora calibrabile", "",
              f"Servono più osservazioni: adesso sono **{len(punti)}**. Fino ad allora resta il",
              "moltiplicatore dichiarato, che è un'assunzione — ma **dichiarata**, non travestita da misura."]
        open("CURVA_COSTO.md", "w").write("\n".join(L))
        print(f"CURVA_COSTO | solo {len(punti)} osservazioni", flush=True); return

    # fasce sul rapporto posizione/volume: niente formula imposta, si guarda cosa dicono i dati
    punti.sort(key=lambda x: x[1])
    fasce = []
    n = max(MIN_PER_FASCIA, len(punti) // 6)
    for i in range(0, len(punti), n):
        blocco = punti[i:i + n]
        if len(blocco) < MIN_PER_FASCIA: break
        r = [b[1] for b in blocco]; c = [b[2] for b in blocco]
        fasce.append({"rapporto_mediano": st.median(r), "rapporto_da": min(r), "rapporto_a": max(r),
                      "costo_mediano": st.median(c), "costo_p75": sorted(c)[int(len(c) * .75)],
                      "n": len(blocco)})

    L += ["| la posizione è, del volume orario | costo andata+ritorno | nei casi peggiori | osservazioni |",
          "|---|---|---|---|"]
    for f in fasce:
        L.append(f"| {f['rapporto_da']*100:.2f}% – {f['rapporto_a']*100:.2f}% | "
                 f"**{f['costo_mediano']*100:.1f}%** | {f['costo_p75']*100:.1f}% | {f['n']} |")

    prima, ultima = fasce[0], fasce[-1]
    salita = ultima["costo_mediano"] / max(1e-6, prima["costo_mediano"])
    L += ["", "## Cosa dicono i dati", ""]
    if salita >= 1.5:
        L += [f"> ✅ **La relazione c'è.** Passando dai token più liquidi ai più sottili il costo di uscita",
              f"> si moltiplica per **{salita:.1f}**. Non è più un'assunzione: è misurato, e il backtest può",
              "> usare la curva invece di una costante.", "",
              "> Il punto pratico: **lo stop scatta quando il volume è crollato**, cioè nella fascia più",
              "> cara. Un backtest che applica il costo medio a quell'uscita sta dichiarando un prezzo",
              "> che non avresti pagato."]
    else:
        L += [f"> ⚠️ **Relazione debole**: dai token liquidi ai sottili il costo cambia solo di "
              f"{salita:.1f} volte.", "",
              "> Può voler dire due cose, e non sappiamo ancora quale: che il volume mediano non è una",
              "> buona misura della profondità del pool, oppure che a queste taglie ($25-500) siamo",
              "> troppo piccoli perché la liquidità conti. **Finché non lo sappiamo, la curva non si usa**",
              "> e resta il moltiplicatore dichiarato."]
    L += ["", "## ⚠️ Cosa questa curva NON misura (dichiarato, non nascosto)", "",
          "Tre limiti, e il terzo non è correggibile con i dati che abbiamo:", "",
          "1. **È calibrata in condizioni di mercato calme**, su token vivi. Le quote sono state prese",
          "   in momenti qualunque, non durante una fuga.",
          "2. **Il volume scambiato è un surrogato della profondità**, non la profondità. Sono due cose",
          "   diverse.",
          "3. **Durante un crollo il volume ESPLODE mentre la profondità evapora.** Quindi proprio nel",
          "   momento peggiore la formula assegna la fascia più *economica*: il surrogato ha il segno",
          "   rovesciato dove conta di più. Il caso peggiore usato in fuga è un cerotto, non una cura.", "",
          "> **I costi di fuga vanno letti come limite inferiore ottimistico, non come stima.**",
          "> Lo stato di panico non è mai stato campionato, quindi questa curva non può contenerlo.",
          "> Per misurarlo davvero servono quote prese DURANTE un crollo — ed è esattamente quello che",
          "> fa `costo_fuga.py` quando un paper trade tocca lo stop. Quei dati, quando ci saranno,",
          "> sostituiranno questa estrapolazione.", "",
          f"> Nota sul campione: si usano solo le misure per cui esiste una candela nell'ora in cui sono",
          f"> state prese. Sono meno ({len(punti)} contro le oltre mille grezze), ma sono le uniche in cui",
          "> calibrazione e applicazione guardano la stessa grandezza. **Meno punti giusti battono più",
          "> punti sbagliati.**", "",
          "> Nota: le trappole (costo ≥ 50%) sono escluse. Non sono un costo alto: sono una perdita",
          "> totale, e vanno contate a parte — mescolarle qui rifarebbe l'errore del costo medio."]

    try:
        cm = json.load(open("data/costo_modello.json"))
    except Exception:
        cm = {}
    cm["curva"] = {"ts": now, "n": len(punti), "fasce": fasce, "salita": salita,
                   "usabile": bool(salita >= 1.5)}
    json.dump(cm, open("data/costo_modello.json", "w"))
    open("CURVA_COSTO.md", "w").write("\n".join(L))
    print(f"CURVA_COSTO | {len(punti)} osservazioni | {len(fasce)} fasce | "
          f"il costo si moltiplica per {salita:.1f} dai liquidi ai sottili | "
          f"{'USABILE' if salita >= 1.5 else 'relazione debole, non si usa'}", flush=True)


if __name__ == "__main__":
    main()
