#!/usr/bin/env python3
"""
LIQUIDITA_IMPEGNATA — esperimento 7 della coda.

L'INTUIZIONE (economica). Il prezzo puo' salire con due euro su un pool vuoto: e' un'opinione, e
costa niente esprimerla. La liquidita' aggiunta al pool e' capitale immobilizzato che non puo'
scappare in un secondo: chi la mette si espone davvero e ci mette dei soldi che restano li'. Fra i
due gesti, guardiamo quello COSTOSO DA FALSIFICARE invece di quello facile.

LA DOMANDA, in forma di gara: a parita' di tutto, la crescita di LIQUIDITA' separa gli esiti futuri
meglio della crescita di PREZZO? Non "correla": separa meglio del concorrente ovvio.

IL CRITERIO DI MORTE, scritto adesso e prima di guardare i numeri:
si misura la distanza fra la mediana del quinto piu' alto e quella del quinto piu' basso. Se questa
distanza, ordinando per liquidita', non e' maggiore di quella ordinando per prezzo — su almeno 15
giorni indipendenti — l'idea non aggiunge niente e muore. Un solo orizzonte, deciso adesso: 24h.
Non si prova a 6h, a 48h o a 72h dopo aver visto il risultato: cercando abbastanza si trova sempre
qualcosa, ed e' il modo piu' facile di prendere il rumore per un vantaggio.

MEDIANE E NON MEDIE: l'esperimento 6 ci ha mostrato che il 99% della media di un gruppo puo' venire
da un token solo. Una lotteria non deve decidere un verdetto.

Nessuna chiamata di rete: usa solo la serie 'pulse' gia' scaricata (liq, prezzo, ogni ~30 minuti).
Sola lettura. €0.
"""
import json, gzip, os, glob, time, sys, statistics as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from indipendenza import t_onesto
except Exception:
    t_onesto = None

MC = "data/multichain"
CHAINS = ("base", "solana", "robinhood")
FINESTRA_H = 2        # su quanto misuro la crescita (liquidita' e prezzo, la stessa finestra per entrambi)
RITARDO_H = 1         # non si compra all'istante in cui si guarda: i dati arrivano dopo
ESITO_H = 24          # orizzonte unico, deciso prima
MIN_LIQ = 3000
MIN_VOL = 500         # scambi veri nella finestra osservata: senza, non e' un mercato ma un pool fermo        # sotto, il pool e' un giocattolo e ogni percentuale e' rumore


def serie(f):
    out = []
    try:
        for l in gzip.open(f, "rt"):
            if not l.strip(): continue
            try:
                d = json.loads(l)
                out.append((int(d["ts"]), float(d.get("cl") or 0), float(d.get("liq") or 0),
                            float(d.get("vol") or 0)))
            except Exception: pass
    except Exception: return []
    out.sort()
    return out


def eventi():
    """Un evento per pool: guardo a meta' della serie, per avere passato E futuro veri."""
    ev = []
    for ch in CHAINS:
        for f in glob.glob(f"{MC}/{ch}/pulse/*.jsonl.gz"):
            s = serie(f)
            if len(s) < 12: continue
            for i in range(len(s)):
                t, pz, lq, vl = s[i]
                if lq < MIN_LIQ or pz <= 0: continue
                # DEVE ESSERE UN MERCATO, NON UN POOL FERMO (09/09). Alla prima misura il 78% degli
                # esiti era ESATTAMENTE zero: non e' il mercato che non si muove, sono pool morti in
                # cui la serie ripete l'ultimo prezzo. Una mediana su quei numeri e' zero per
                # costruzione, e infatti i due candidati pareggiavano a +0,0%.
                # Il filtro guarda SOLO IL PASSATO — che il pool abbia scambiato prima di guardarlo —
                # mai l'esito: se poi muore, quel morte e' un risultato vero e deve contare.
                if vl < MIN_VOL: continue
                # PASSATO: solo punti precedenti. Nessuno sguardo in avanti, mai.
                pre = [x for x in s[:i] if t - x[0] >= FINESTRA_H * 3600]
                if not pre: continue
                t0, pz0, lq0, _v0 = pre[-1]
                if pz0 <= 0 or lq0 <= 0: continue
                cre_liq = lq / lq0 - 1
                cre_pz = pz / pz0 - 1
                # FUTURO: compro RITARDO_H dopo aver guardato, vendo ESITO_H dopo
                ent = [x for x in s if x[0] >= t + RITARDO_H * 3600]
                if not ent: continue
                pe = ent[0][1]
                usc = [x for x in ent if x[0] <= ent[0][0] + ESITO_H * 3600]
                if len(usc) < 3 or pe <= 0: continue
                ev.append({"gio": time.strftime("%Y-%m-%d", time.gmtime(t)),
                           "liq": cre_liq, "pz": cre_pz, "res": usc[-1][1] / pe - 1})
                break        # UN evento per pool: mille punti dello stesso token non sono mille prove
    return ev


def separazione(ev, chiave):
    """Distanza fra la mediana del quinto migliore e quella del quinto peggiore, ordinando per 'chiave'."""
    if len(ev) < 25: return None
    o = sorted(ev, key=lambda e: e[chiave])
    q = max(5, len(o) // 5)
    basso = st.median([e["res"] for e in o[:q]])
    alto = st.median([e["res"] for e in o[-q:]])
    return alto - basso, o[-q:]


def main():
    ev = eventi()
    L = ["# 💧 I SOLDI CHE ENTRANO NEL POOL, NON IL PREZZO CHE SALE",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · esperimento 7 · solo dati già "
         f"scaricati · €0*", "",
         "> Il prezzo può salire con due euro su un pool vuoto: è un'opinione, e costa niente",
         "> esprimerla. La liquidità aggiunta è **capitale immobilizzato**, soldi che restano lì e non",
         "> scappano in un secondo. Fra i due gesti guardiamo quello **costoso da falsificare**.", "",
         "> La domanda è una gara, non una correlazione: **la crescita di liquidità separa gli esiti",
         "> futuri meglio della crescita di prezzo?** Se non batte il concorrente ovvio, non serve.", "",
         f"Crescita misurata su **{FINESTRA_H}h**, ingresso **{RITARDO_H}h dopo** averla vista, esito a "
         f"**{ESITO_H}h**. Un evento per pool: mille punti dello stesso token non sono mille prove.", "",
         f"**Eventi utilizzabili: {len(ev)}**", ""]

    if len(ev) >= 25:
        sl = separazione(ev, "liq"); sp = separazione(ev, "pz")
        L += ["| ordinando per | quinto alto − quinto basso (mediana a 24h) |", "|---|---|",
              f"| **liquidità che entra** | **{sl[0]*100:+.1f}%** |",
              f"| prezzo che sale | {sp[0]*100:+.1f}% |", ""]
        if t_onesto:
            top = sl[1]
            t_, n_, ting = t_onesto([e["res"] for e in top], [e["gio"] for e in top])
            L += [f"Sul quinto alto per liquidità: t sui **giorni indipendenti** **{t_:+.2f}** "
                  f"({n_} giorni distinti); sulle righe sarebbe {ting:+.2f}.", ""]
        vince = sl[0] > sp[0]
        abbastanza = (not t_onesto) or n_ >= 15
        L += ["## Verdetto", ""]
        if vince and abbastanza:
            L += ["> ✅ **La liquidità separa meglio del prezzo.** Prossimo passo: verificare che regga",
                  "> sul livello di validazione e che sopravviva ai costi misurati d'uscita."]
        elif not abbastanza:
            L += [f"> ⏸️ La liquidità {'batte' if vince else 'non batte'} il prezzo, ma i giorni",
                  "> indipendenti sono ancora sotto i 15 del criterio. L'accumulo continua a ogni giro."]
        else:
            L += ["> ❌ **Criterio di morte scattato**, scritto prima di guardare: guardare i soldi che",
                  "> entrano non separa meglio del guardare il prezzo. Non si prova a 6h, 48h o 72h per",
                  "> salvarla: un orizzonte era stato scelto prima, e resta quello."]
    else:
        L += [f"> ⏸️ Servono almeno 25 eventi per formare i quinti: ne abbiamo {len(ev)}.", ""]

    L += ["", "> **Perché questa gara è onesta**: i due candidati corrono sullo stesso orizzonte, sugli",
          "> stessi pool e negli stessi giorni. Se la liquidità vincesse solo cambiando finestra, non",
          "> avrebbe vinto: avrei scelto io."]
    open("LIQUIDITA_IMPEGNATA.md", "w").write("\n".join(L))
    print(f"LIQUIDITA_IMPEGNATA | eventi:{len(ev)}", flush=True)


if __name__ == "__main__":
    main()
