#!/usr/bin/env python3
"""
RITARDO — il movimento succede PRIMA che possiamo entrare?

DA DOVE VIENE (11/09, revisione esterna). L'assunzione invisibile: trattiamo il ritardo reale di
osservazione (3-7 ore) come un COSTO, cioe' come qualcosa che ci toglie un po' di rendimento. Ma il
metodo dichiara orizzonti da 5 minuti, 30 minuti e 2 ore: su quelli il bot arriva quando l'orizzonte
e' GIA' FINITO. Non e' un costo, e' una cancellazione. Se il movimento sta tutto prima della nostra
entrata, LOOP 1 sta valutando segnali economicamente morti — e li sta valutando da settimane.

LA DOMANDA, in una riga: quanto del movimento accade PRIMA che potremmo comprare, e quanto DOPO?

CRITERIO DI MORTE (di chi sta fuori, scritto prima di guardare): l'ipotesi "il segnale sopravvive al
ritardo" e' morta se il rendimento netto DOPO l'entrata e' <= 0 su almeno 25 giorni indipendenti,
mentre quello prima e' positivo. In quel caso gli orizzonti brevi non sono evidenza economica: sono
cose che qualcun altro ha gia' incassato.

Sola lettura, nessuna chiamata. €0.
"""
import json, gzip, os, glob, time, sys, statistics as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from indipendenza import t_onesto
except Exception:
    t_onesto = None

MC = "data/multichain"
CHAINS = ("base", "robinhood", "solana")
RITARDO_H = 3          # il piu' OTTIMISTA dei nostri: se muore anche cosi', a 7 ore e' sepolto
ORIZZONTI = (2, 6, 24)
MIN_CANDELE = 6
MIN_VOL = 500          # scambi veri nella finestra osservata: sotto, non e un mercato


def serie(f):
    out = []
    try:
        for l in gzip.open(f, "rt"):
            if not l.strip(): continue
            try:
                d = json.loads(l)
                out.append((int(d["ts"]), float(d.get("cl") or 0), float(d.get("vol") or 0)))
            except Exception: pass
    except Exception: return []
    out.sort(); return out


def prezzo_a(s, t):
    dopo = [p for ts, p, _v in s if ts >= t]
    return dopo[0] if dopo else None


def selezionati(chain):
    """I trade che il modello SCEGLIE davvero, non l'universo intero: e' la differenza fra la domanda
    che il consulente ha posto e quella a cui rispondevo prima. Stessa identica selezione di LOOP 1 —
    non una copia che puo' divergere."""
    try:
        import multichain_brain as B
        righe = B.load_rows(chain)
        if len(righe) < 40: return []
        return [r for r in B.walkforward_righe(righe) if r.get("pool")]
    except Exception:
        return []


def prova_selezionati(ch):
    sel = selezionati(ch)
    prima, dopo, gio = [], {h: [] for h in ORIZZONTI}, []
    for r in sel:
        f = f"{MC}/{ch}/candles/{r['pool']}.jsonl.gz"
        s = serie(f)
        if len(s) < MIN_CANDELE: continue
        t0 = r.get("t0") or s[0][0]
        ent = r["ent"]
        p0, pe = prezzo_a(s, t0), prezzo_a(s, ent)
        if not p0 or not pe: continue
        prima.append(pe / p0 - 1)
        gio.append(time.strftime("%Y-%m-%d", time.gmtime(ent)))
        for h in ORIZZONTI:
            pf = prezzo_a(s, ent + h * 3600)
            if pf: dopo[h].append(pf / pe - 1)
    return sel, prima, dopo, gio


def main():
    righe = {ch: {"prima": [], "gio": [], **{f"dopo{h}": [] for h in ORIZZONTI}} for ch in CHAINS}
    for ch in CHAINS:
        for f in glob.glob(f"{MC}/{ch}/candles/*.jsonl.gz"):
            s = serie(f)
            if len(s) < MIN_CANDELE: continue
            t0 = s[0][0]                      # il primo momento in cui il token esiste per noi
            p0 = s[0][1]
            # DEVE ESSERE UN MERCATO, NON UN POOL FERMO. Senza questo filtro il 78% degli esiti e'
            # ESATTAMENTE zero — non perche' il prezzo non si muove, ma perche' nessuno scambia e la
            # serie ripete l'ultimo valore. Una mediana su quei numeri e' zero per costruzione, e
            # avrebbe fatto dichiarare "il segnale muore" a un'analisi che non stava guardando niente.
            # Il filtro usa SOLO il passato: scambi veri prima del momento in cui potremmo entrare.
            scambi = sum(v for ts, _p, v in s if ts <= t0 + RITARDO_H * 3600)
            if scambi < MIN_VOL: continue
            ent = t0 + RITARDO_H * 3600
            pe = prezzo_a(s, ent)
            if not p0 or not pe: continue
            righe[ch]["prima"].append(pe / p0 - 1)
            righe[ch]["gio"].append(time.strftime("%Y-%m-%d", time.gmtime(t0)))
            for h in ORIZZONTI:
                pf = prezzo_a(s, ent + h * 3600)
                righe[ch][f"dopo{h}"].append((pf / pe - 1) if pf else None)

    L = ["# ⏳ IL MOVIMENTO SUCCEDE PRIMA CHE POSSIAMO ENTRARE?",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · nato dalla revisione esterna "
         f"dell'11/09 · sola lettura · €0*", "",
         "> Trattavamo il ritardo di osservazione (3-7 ore) come **un costo**: qualcosa che ci toglie",
         "> un po' di rendimento. Ma con orizzonti da 5 minuti, 30 minuti e 2 ore il bot arriva quando",
         "> l'orizzonte è **già finito**. Non è un costo: è una cancellazione.", "",
         f"Ritardo usato: **{RITARDO_H}h**, il più ottimista dei nostri. Se il segnale muore già così,",
         "a 7 ore è sepolto.", "",
         "| chain | token | **prima** dell'entrata | dopo +2h | dopo +6h | dopo +24h |",
         "|---|---|---|---|---|---|"]
    for ch in CHAINS:
        r = righe[ch]
        if len(r["prima"]) < 20:
            L.append(f"| **{ch}** | {len(r['prima'])} | *troppo pochi* | | | |")
            continue
        c = [f"**{st.median(r['prima'])*100:+.1f}%**"]
        for h in ORIZZONTI:
            v = [x for x in r[f"dopo{h}"] if x is not None]
            c.append(f"{st.median(v)*100:+.1f}%" if len(v) >= 20 else "—")
        L.append(f"| **{ch}** | {len(r['prima']):,} | " + " | ".join(c) + " |")
    L += ["", "*Mediane: una lotteria non deve decidere un verdetto.*", ""]

    # IL VERDETTO, sulla chain su cui stiamo decidendo
    r = righe["base"]
    v6 = [x for x in r["dopo6"] if x is not None]
    if len(r["prima"]) >= 20 and len(v6) >= 20:
        prima = st.median(r["prima"]); dopo = st.median(v6)
        gg = 0
        if t_onesto:
            _t, gg, _ti = t_onesto(v6, r["gio"][:len(v6)])
        L += ["## Verdetto su Base", ""]
        if prima > 0 and dopo <= 0:
            L += [f"> ❌ **Il segnale non sopravvive al ritardo.** Prima che potessimo comprare il",
                  f"> prezzo ha già fatto **{prima*100:+.1f}%**; da quando compriamo in poi fa",
                  f"> **{dopo*100:+.1f}%**. Il movimento c'è — **ma lo incassa qualcun altro**.", "",
                  "> Non è un costo da limare: gli orizzonti brevi non sono evidenza economica, sono",
                  "> cose già successe quando arriviamo. Chi vuole salvarli deve prima accorciare il",
                  "> ritardo, non ritoccare la soglia."]
        elif dopo > 0:
            L += [f"> ✅ **Qualcosa resta dopo l'entrata**: {dopo*100:+.1f}% mediano a 6h "
                  f"(prima: {prima*100:+.1f}%). Il ritardo morde ma non cancella.",
                  f"> Giorni indipendenti: {gg}."]
        else:
            L += [f"> ⏸️ Prima {prima*100:+.1f}%, dopo {dopo*100:+.1f}%: nessuno dei due è positivo, "
                  "non c'è un segnale da salvare né da uccidere."]
    L += ["", "---", "",
          "> ⚠️ **Cosa questo test NON dice ancora.** Qui guardo **tutti** i token con candele, non i",
          "> **349 trade che il modello sceglie** su Base: sono due domande diverse, e la mediana",
          "> dell'universo intero è piatta per costruzione — la maggior parte dei token non fa niente.",
          "> La domanda vera è se il movimento dei **selezionati** stia prima della nostra entrata, e",
          "> per rispondere serve la lista dei segnali con il loro momento, non l'universo.",
          "> Scriverlo è meglio che far passare per verdetto una misura che risponde a un'altra cosa."]
    # --- LA DOMANDA VERA: sui trade che il modello SCEGLIE ---
    L += ["", "## Sui trade che il modello sceglie davvero", "",
          "*Non l'universo: la stessa identica selezione che produce la percentuale di LOOP 1.*", "",
          "| chain | trade scelti | **prima** dell'entrata | dopo +2h | dopo +6h | dopo +24h |",
          "|---|---|---|---|---|---|"]
    verdetti = {}
    for ch in CHAINS:
        sel, prima, dopo, gio = prova_selezionati(ch)
        if len(prima) < 20:
            L.append(f"| **{ch}** | {len(sel)} | *misurabili solo {len(prima)}* | | | |")
            continue
        c = [f"**{st.median(prima)*100:+.1f}%**"]
        for h in ORIZZONTI:
            c.append(f"{st.median(dopo[h])*100:+.1f}%" if len(dopo[h]) >= 20 else "—")
        L.append(f"| **{ch}** | {len(sel)} | " + " | ".join(c) + " |")
        verdetti[ch] = (st.median(prima), dopo, gio)
    L += [""]
    if "base" in verdetti:
        pr, dp, gio = verdetti["base"]
        d6 = st.median(dp[6]) if len(dp[6]) >= 20 else None
        gg = 0
        if t_onesto and len(dp[6]) >= 20:
            _t, gg, _ti = t_onesto(dp[6], gio[:len(dp[6])])
        L += ["### Verdetto sui selezionati di Base", ""]
        if d6 is None:
            L += ["> ⏸️ Non abbastanza trade con esito a 6h per giudicare."]
        elif pr > 0 and d6 <= 0:
            L += [f"> ❌ **Il segnale non sopravvive al ritardo.** Sui trade scelti il prezzo fa",
                  f"> **{pr*100:+.1f}%** prima che potessimo entrare e **{d6*100:+.1f}%** dopo.",
                  "> Il movimento esiste: **lo incassa chi arriva prima di noi.** Non è un costo da",
                  "> limare — o si accorcia il ritardo, o quegli orizzonti non sono nostri.",
                  f"> ({gg} giorni indipendenti.)"]
        elif d6 > 0:
            L += [f"> ✅ **Qualcosa resta dopo l'entrata**: {d6*100:+.1f}% mediano a 6h contro "
                  f"{pr*100:+.1f}% prima. Il ritardo morde ma non cancella. ({gg} giorni indipendenti.)"]
        else:
            L += [f"> ⏸️ Prima {pr*100:+.1f}%, dopo {d6*100:+.1f}%: non c'è un vantaggio né da salvare "
                  "né da uccidere."]
    open("RITARDO.md", "w").write("\n".join(L))
    print("RITARDO | " + " ".join(f"{c}:{len(righe[c]['prima'])}" for c in CHAINS), flush=True)


if __name__ == "__main__":
    main()
