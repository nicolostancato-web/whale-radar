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


def volume_orario():
    """{pool: volume mediano per candela} — la nostra misura di quanto e' vivo un mercato."""
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

    punti = []      # (taglia, rapporto posizione/volume, costo osservato)
    for mint, t in arch.items():
        pool = inv.get(mint.lower())
        v = vol.get(pool) if pool else None
        if not v or v <= 0: continue
        for s in TAGLIE:
            d = (t.get("size") or {}).get(s) or (t.get("size") or {}).get(int(s))
            if not isinstance(d, dict): continue
            c = d.get("costo_roundtrip_pct")
            if c is None or c >= 50: continue          # le trappole non sono un costo: sono altro
            punti.append((float(s), float(s) / v, c / 100.0))

    L = [f"# 📈 QUANTO COSTA USCIRE, SECONDO QUANTO E' LIQUIDO IL TOKEN",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · {len(punti)} osservazioni "
         f"(token con **sia** una misura vera su Jupiter **sia** le nostre candele) · €0*", "",
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
    L += ["", "> Nota: le trappole (costo ≥ 50%) sono escluse. Non sono un costo alto: sono una perdita",
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
