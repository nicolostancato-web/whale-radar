#!/usr/bin/env python3
"""
QUOTAZIONE_ALTROVE — esperimento 6 della coda.

L'INTUIZIONE (economica, non statistica). Le sei piste morte chiedevano tutte "chi altro sta comprando?".
I voti DAO chiedevano "chi e' costretto a comprare?" e sono morti perche' i compratori obbligati erano le
stesse persone di prima, su mercati che leggono gli stessi annunci pubblici.
Qui la domanda e' diversa: "chi vuole comprare ma NON PUO' comprarlo altrove?". Un token che esisteva gia'
su Base o Solana e viene quotato dentro un'app riceve compratori che non hanno un portafoglio on-chain,
non sanno arbitrare e non possono andare a prendere l'offerta piu' economica sull'altra chain. La domanda
nuova e' costretta a pagare il pool locale. E' una barriera, non un'opinione.

IL CRITERIO DI MORTE, scritto adesso e prima di guardare i numeri:
su almeno 15 quotazioni per gruppo, se il rendimento a 72h dei token "gia' esistenti altrove" non batte
quello dei nati nativi su Robinhood — con la t calcolata sui GIORNI indipendenti e non sulle righe —
l'idea e' morta. Non si allarga la finestra, non si cambia il ritardo d'ingresso, non si prova a 24h.

Nessuna chiamata di rete: usa solo dati gia' scaricati. Sola lettura. €0.
"""
import json, gzip, os, glob, time, sys, statistics as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from indipendenza import t_onesto
except Exception:
    t_onesto = None

MC = "data/multichain"
RITARDO_H = 3         # i nostri dati arrivano dopo: non si compra al secondo zero, si compra quando lo vediamo
ESITO_H = 72
MIN_SIMBOLO = 4       # sotto le 4 lettere i nomi si ripetono per caso: meglio perdere eventi che inventarli
ALTRE = ("base", "solana")


def simbolo(nome):
    return (nome or "").split("/")[0].strip().split(" ")[0].upper()


def quando(v):
    s = v.get("created")
    if not s: return None
    try:
        return int(time.mktime(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ")) - time.timezone)
    except Exception:
        return None


def pools(chain):
    p = f"{MC}/{chain}/pools.json"
    if not os.path.exists(p): return {}
    d = json.load(open(p))
    return d.get("pools", d) if isinstance(d, dict) else {}


def candele(chain, addr):
    f = f"{MC}/{chain}/candles/{addr}.jsonl.gz"
    if not os.path.exists(f): return []
    out = []
    try:
        for l in gzip.open(f, "rt"):
            if l.strip():
                try:
                    d = json.loads(l); out.append((int(d["ts"]), float(d["cl"]), float(d.get("vol") or 0)))
                except Exception: pass
    except Exception: return []
    out.sort()
    return out


def esito(cs, nascita):
    """Compro RITARDO_H dopo la nascita, vendo ESITO_H dopo. Solo candele che esistono davvero."""
    ent = nascita + RITARDO_H * 3600
    dopo = [c for c in cs if c[0] >= ent]
    if not dopo: return None
    p0 = dopo[0][1]
    fine = [c for c in dopo if c[0] <= ent + ESITO_H * 3600]
    if len(fine) < 3 or not p0: return None
    return fine[-1][1] / p0 - 1


def main():
    rh = pools("robinhood")
    # PRIMA APPARIZIONE ALTROVE: per ogni simbolo, la data piu' antica vista su un'altra chain.
    prima = {}
    for ch in ALTRE:
        for a, v in pools(ch).items():
            s = simbolo(v.get("name"))
            t = quando(v)
            if len(s) < MIN_SIMBOLO or not t: continue
            if s not in prima or t < prima[s]: prima[s] = t

    gruppi = {"gia' esisteva altrove": [], "nato qui": []}
    chiavi = {"gia' esisteva altrove": [], "nato qui": []}
    for a, v in rh.items():
        t = quando(v)
        s = simbolo(v.get("name"))
        if not t or len(s) < MIN_SIMBOLO: continue
        cs = candele("robinhood", a)
        if not cs: continue
        r = esito(cs, t)
        if r is None: continue
        # NIENTE SGUARDO NEL FUTURO: conta solo se esisteva altrove PRIMA di nascere qui.
        g = "gia' esisteva altrove" if (s in prima and prima[s] < t) else "nato qui"
        gruppi[g].append(r)
        chiavi[g].append(time.strftime("%Y-%m-%d", time.gmtime(t)))   # un giorno = una prova

    L = ["# 🚪 CHI VUOLE COMPRARE E NON PUÒ COMPRARLO ALTROVE",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · esperimento 6 · solo dati già scaricati · €0*", "",
         "> Le sei piste morte chiedevano tutte **«chi altro sta comprando?»**. I voti DAO chiedevano",
         "> «chi è *costretto* a comprare?» e sono morti perché gli obbligati erano le stesse persone",
         "> di prima, davanti agli stessi annunci pubblici.", "",
         "> Qui la domanda è un'altra: **«chi vuole comprare e non può comprarlo altrove?»**. Un token",
         "> già esistente su Base o Solana, quotato dentro un'app, riceve compratori senza portafoglio",
         "> on-chain: non sanno arbitrare e non possono andare a prendere l'offerta più economica",
         "> sull'altra chain. La domanda nuova **deve** pagare il pool locale. È una barriera, non",
         "> un'opinione — ed è l'unico caso in cui sappiamo in anticipo che arrivano compratori", 
         "> che non possono scegliere.", "",
         f"Ingresso **{RITARDO_H}h dopo** la nascita (i dati ci arrivano dopo, non al secondo zero), "
         f"uscita a **{ESITO_H}h**. Simboli sotto le {MIN_SIMBOLO} lettere esclusi: si ripetono per caso.", ""]

    L += ["| gruppo | quotazioni | media 72h | mediana |", "|---|---|---|---|"]
    for g in ("gia' esisteva altrove", "nato qui"):
        v = gruppi[g]
        if v:
            L.append(f"| {g} | {len(v)} | **{st.mean(v)*100:+.1f}%** | {st.median(v)*100:+.1f}% |")
        else:
            L.append(f"| {g} | 0 | — | — |")
    L += [""]

    a, b = gruppi["gia' esisteva altrove"], gruppi["nato qui"]
    # QUANTO DELLA MEDIA E' UN BIGLIETTO SOLO (08/09). Su questi mercati una media puo' essere fatta
    # da un token solo che ha fatto 100x: e' successo, +1444% di media contro una mediana negativa.
    # Una media che sparisce togliendo una riga non e' una misura del gruppo, e' un aneddoto.
    def peso_del_primo(v):
        if len(v) < 3: return 0.0
        s = sorted(v, reverse=True)
        tot = sum(s)
        return 0.0 if tot <= 0 else s[0] / tot
    L += ["*Quanto della media viene da **un solo token**: "
          + ", ".join(f"{g} **{peso_del_primo(gruppi[g])*100:.0f}%**" for g in gruppi if gruppi[g])
          + ". Dove è alto, la media non descrive il gruppo: guarda la mediana.*", ""]
    if len(a) >= 15 and len(b) >= 15:
        diff = st.median(a) - st.median(b)      # mediana: una lotteria non deve decidere un verdetto
        riga = f"Differenza fra i due gruppi sulla **mediana**: **{diff*100:+.1f}%** a 72h."
        if t_onesto:
            ta, na, ting = t_onesto(a, chiavi["gia' esisteva altrove"])
            riga += (f" Sul gruppo che ci interessa la t sui **giorni indipendenti** è **{ta:+.2f}** "
                     f"({na} giorni distinti); sulle righe sarebbe {ting:+.2f}, ed è la differenza fra "
                     f"contare le prove e contarsi addosso.")
        L += [riga, ""]
        vivo = diff > 0 and (not t_onesto or ta > 2)
        L += ["## Verdetto", ""]
        L += ([f"> ✅ **Il gruppo con la barriera rende di più**, e regge sui giorni indipendenti.",
               "> Prossimo passo: verificare che sopravviva ai costi misurati e sul livello di validazione."]
              if vivo else
              ["> ❌ **Criterio di morte scattato**, scritto prima di guardare: la barriera non si vede",
               "> nei prezzi. Non si allarga la finestra, non si sposta il ritardo d'ingresso, non si",
               "> prova a 24h per salvarla."])
    else:
        L += [f"> ⏸️ Servono 15 quotazioni per gruppo: ne abbiamo {len(a)} e {len(b)}. "
              "L'accumulo continua a ogni giro.", ""]

    L += ["", "> **Il limite onesto**: due token diversi possono chiamarsi uguale, e questo confronto",
          "> lega i due mondi solo per nome. Sotto le 4 lettere li ho esclusi; sopra, una parte delle",
          "> coppie resta un caso. Se il gruppo con la barriera vincesse, il passo successivo non è",
          "> festeggiare: è ricollegare i token per contratto e rifare la stessa misura."]
    open("QUOTAZIONE_ALTROVE.md", "w").write("\n".join(L))
    print(f"QUOTAZIONE_ALTROVE | altrove:{len(a)} nativi:{len(b)}", flush=True)


if __name__ == "__main__":
    main()
