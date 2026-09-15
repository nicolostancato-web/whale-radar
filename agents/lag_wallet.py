#!/usr/bin/env python3
"""
SUPERATO dal 02/09 da wallet_skill.py, che misura la bravura come extra-rendimento contro token
comparabili invece che come 'ha azzeccato due token'. Resta come traccia del primo test — quello
che ha chiuso il copy-trading — e non viene piu' convocato dal motore.

LAG_WALLET — il segnale di un wallet bravo sopravvive al RITARDO con cui lo seguiamo?

La consulenza esterna indicava il copy-trading come "la candidata piu' seria", con un avvertimento preciso:
va misurato il rendimento DOPO che il trade del wallet e' pubblico, e il ritardo di GitHub Actions
probabilmente distrugge l'edge. Questo agente risponde prima che ci costruiamo sopra.

Tre domande, in ordine di importanza:
  1. il vantaggio sopravvive al ritardo? (1 min, 5 min, 30 min, 2 ore)
  2. sopravvive ai COSTI veri? (slippage, fee, gas, latenza — gli stessi del resto del sistema)
  3. e' un VANTAGGIO o e' il mercato? — comprare a caso nello stesso istante rende uguale?
     Senza questa terza domanda un +20% non dice niente: se anche il caso rende +20%, il wallet non sa nulla.

NO-LOOKAHEAD: la bravura di un wallet si calcola solo su token gia' risolti PRIMA dell'acquisto valutato.
FASCE: i risultati sono separati fra ricerca e validazione (data/holdout_config.json) — la validazione
e' la fascia di tempo che la ricerca non ha mai visto, ed e' l'unica che fa fede.
Scrive LAG_WALLET.md. Sola lettura. €0.
"""
import json, os, gzip, time, sys, random, statistics as st
sys.path.insert(0, "agents")
import multichain_brain as B
import learner as L

CHAIN = os.environ.get("CHAIN", "base")
RITARDI = [0, 60, 300, 1800, 7200]
MIN_SUCCESSI = 2
ORIZZONTE = 24 * 3600
now = int(time.time())
rnd = random.Random(7)

try:
    _hc = json.load(open("data/holdout_config.json")); CONFINE = int(_hc["confine_validazione"])
except Exception:
    CONFINE = 0


def netto(lordo):
    """lo stesso metro del resto del sistema: cosa resta in tasca dopo slippage, fee, gas e latenza."""
    return L._net(1 + lordo, tr=True)


def prezzo_a(cs, quando):
    for c in cs:
        if c[0] >= quando and c[4]: return c[4]
    return None


def rendimento(cs, quando):
    e = prezzo_a(cs, quando)
    if not e or e <= 0: return None
    u = prezzo_a(cs, quando + ORIZZONTE) or cs[-1][4]
    return (u / e - 1) if u else None


def riga(v, etichetta):
    if len(v) < 10: return None
    lordi = [x for x, _ in v]; netti = [netto(x) for x, _ in v]
    return (f"| {etichetta} | {st.mean(lordi)*100:+.0f}% | **{st.mean(netti)*100:+.0f}%** | "
            f"{st.median(netti)*100:+.0f}% | {sum(1 for x in netti if x > 0)/len(netti)*100:.0f}% | {len(v)} |")


def main():
    serie = {}
    for f in B.serie_files(CHAIN):
        addr = os.path.basename(f).replace(".jsonl.gz", "")
        try:
            cs = []
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("cl"): cs.append([int(d["ts"]), d.get("op"), d.get("hi"), d.get("lo"), d["cl"], d.get("vol")])
            if len(cs) >= B.MIN_CANDLES: cs.sort(); serie[addr] = cs
        except Exception: pass
    if len(serie) < 60:
        print(f"LAG_WALLET | {CHAIN}: solo {len(serie)} serie", flush=True); return

    esito = {}
    for a, cs in serie.items():
        p = [c[4] for c in cs if c[4]]
        if len(p) > 3: esito[a] = ((max(p) / p[0]) >= 2, cs[-1][0])

    acquisti = []
    for a, cs in serie.items():
        for t in B.load_trades(CHAIN, a):
            if t.get("kind") == "buy" and t.get("w") and t.get("ts"):
                acquisti.append((int(t["ts"]), t["w"], a))
    acquisti.sort()
    if len(acquisti) < 500:
        print(f"LAG_WALLET | {CHAIN}: solo {len(acquisti)} acquisti", flush=True); return

    vivi = list(serie.keys())
    da_assorbire = sorted(((v[1], a) for a, v in esito.items() if v[0]))
    successi, pi = {}, 0
    seguiti = {r: {"ricerca": [], "validazione": []} for r in RITARDI}
    caso = {r: [] for r in RITARDI}          # il controllo: stesso istante, token a caso
    usati = 0
    for ts, w, addr in acquisti:
        while pi < len(da_assorbire) and da_assorbire[pi][0] < ts:
            _, a_ris = da_assorbire[pi]; pi += 1
            for t in B.load_trades(CHAIN, a_ris):
                if t.get("kind") == "buy" and t.get("w"):
                    successi[t["w"]] = successi.get(t["w"], 0) + 1
        if successi.get(w, 0) < MIN_SUCCESSI: continue
        cs = serie.get(addr)
        if not cs: continue
        fascia = "validazione" if (CONFINE and ts >= CONFINE) else "ricerca"
        altro = serie.get(rnd.choice(vivi))
        for r in RITARDI:
            v = rendimento(cs, ts + r)
            if v is not None: seguiti[r][fascia].append((v, ts))
            if altro is not None:
                vc = rendimento(altro, ts + r)
                if vc is not None: caso[r].append((vc, ts))
        usati += 1

    intestazione = ["| se arriviamo | lordo | **netto** | mediano netto | quanti in guadagno | casi |",
                    "|---|---|---|---|---|---|"]
    et = {0: "**subito** (impossibile per noi)", 60: "dopo 1 minuto", 300: "dopo 5 minuti",
          1800: "dopo 30 minuti", 7200: "dopo 2 ore"}

    if usati < 20:
        open("LAG_WALLET.md", "w").write(
            f"# ⏱️ IL SEGNALE SOPRAVVIVE AL RITARDO? ({CHAIN})\n\n*Solo {usati} acquisti da wallet con "
            f"almeno {MIN_SUCCESSI} successi alle spalle: campione troppo piccolo. Serve più storico.*\n")
        print(f"LAG_WALLET | {CHAIN}: solo {usati} acquisti di wallet bravi", flush=True); return

    L_ = [f"# ⏱️ IL SEGNALE SOPRAVVIVE AL RITARDO? ({CHAIN})",
          f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · {usati} acquisti da wallet con almeno "
          f"{MIN_SUCCESSI} successi alle spalle · posizione tenuta {ORIZZONTE//3600}h*", "",
          "> Tre domande in fila: il vantaggio regge al **ritardo**? regge ai **costi**? e soprattutto —",
          "> è un vantaggio o è solo il mercato che sale? L'ultima riga di ogni tabella compra **a caso**",
          "> nello stesso istante: se rende uguale, il wallet non sa nulla che non sappia il caso.", ""]

    for fascia, titolo in (("ricerca", "Fascia di ricerca (già vista dal sistema)"),
                           ("validazione", "🔒 Fascia di validazione (mai vista — è questa che fa fede)")):
        righe = [riga(seguiti[r][fascia], et[r]) for r in RITARDI]
        righe = [x for x in righe if x]
        if not righe:
            L_ += [f"## {titolo}", "", "*Campione ancora troppo piccolo in questa fascia.*", ""]; continue
        L_ += [f"## {titolo}", ""] + intestazione + righe
        c5 = riga(caso[300], "*comprando a caso, dopo 5 minuti*")
        if c5: L_.append(c5)
        L_.append("")
        v5 = [netto(x) for x, _ in seguiti[300][fascia]]
        c5v = [netto(x) for x, _ in caso[300]]
        if len(v5) >= 10 and len(c5v) >= 10:
            delta = (st.mean(v5) - st.mean(c5v)) * 100
            if st.mean(v5) > 0 and delta > 3:
                L_ += [f"> ✅ Seguire il wallet con 5 minuti di ritardo rende **{delta:.0f} punti più del caso**, "
                       f"e resta positivo dopo i costi.", ""]
            elif st.mean(v5) <= 0:
                L_ += ["> ❌ Dopo i costi il segnale è negativo: non è percorribile così com'è.", ""]
            else:
                L_ += [f"> ⚠️ Positivo, ma il vantaggio sul caso è di soli **{delta:.0f} punti**: "
                       f"potrebbe essere il mercato, non il wallet.", ""]

    L_ += ["> Nota metodo: la bravura di un wallet è calcolata solo sui token già chiusi PRIMA dell'acquisto",
           "> valutato. I costi sono gli stessi del resto del sistema (slippage, fee, gas, latenza doppia)."]
    open("LAG_WALLET.md", "w").write("\n".join(L_))
    print(f"LAG_WALLET | {CHAIN} | {usati} acquisti valutati", flush=True)


if __name__ == "__main__":
    main()
