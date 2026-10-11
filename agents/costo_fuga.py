#!/usr/bin/env python3
"""
COSTO_FUGA — quanto costa uscire NEL MOMENTO in cui vuoi uscire davvero.

Dalla revisione esterna del 04/09:

    «Il costo di fuga va misurato, non stimato con 3x. Quando un paper trade tocca lo stop, il
     sistema deve chiedere subito una quotazione realmente eseguibile, registrando anche le quote
     fallite, le route disponibili e la liquidita'. Ripetere dopo 15, 30 e 60 secondi.»

E' l'unica misura che non si puo' recuperare dopo. Tutte le nostre quote finora sono prese su token
vivi in un momento qualunque — cioe' nel momento sbagliato. Il prezzo che conta e' quello che
avresti pagato mentre il pool si svuotava e tutti scappavano insieme a te, e quel momento dura
pochi secondi: o lo catturi mentre accade, o e' perso per sempre.

Per questo l'agente non gira "ogni tanto": gira QUANDO uno stop scatta, e in quell'istante chiede
tre taglie ($25, $50, $100) e ripete a +15s, +30s, +60s. Cosi' vediamo anche come il costo peggiora
mentre esiti — che e' esattamente cio' che il moltiplicatore x3 stava indovinando.

I FALLIMENTI SONO IL DATO PIU' IMPORTANTE: una quota che non torna significa "in quel momento non
saresti uscito affatto", e vale piu' di dieci quote riuscite. Vengono registrati, non scartati.

Scrive data/costi_fuga.jsonl (append, un solo scrittore) + COSTO_FUGA.md. €0 (Jupiter lite-api).
"""
import json, os, time, urllib.request

USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
API = "https://lite-api.jup.ag/swap/v1/quote"
TAGLIE = (25, 50, 100)
RITARDI = (0, 15, 30, 60)
USCITA = "data/costi_fuga.jsonl"
now = int(time.time())


def quota(mint, usd):
    """(quanto torna indietro, impatto, route) oppure (None, motivo, None). Il motivo E' un dato."""
    lam = int(usd * 1e6)
    url = f"{API}?inputMint={USDC}&outputMint={mint}&amount={lam}&slippageBps=300"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}),
                                    timeout=15) as r:
            d = json.loads(r.read())
    except urllib.error.HTTPError as e:
        return None, ("nessuna route" if e.code in (400, 404) else f"http {e.code}"), None
    except Exception as e:
        return None, type(e).__name__, None
    out = int(d.get("outAmount") or 0)
    if not out: return None, "quantita' nulla", None
    # e ora la parte che conta: quei token, li rivendo?
    url2 = f"{API}?inputMint={mint}&outputMint={USDC}&amount={out}&slippageBps=300"
    try:
        with urllib.request.urlopen(urllib.request.Request(url2, headers={"Accept": "application/json"}),
                                    timeout=15) as r:
            d2 = json.loads(r.read())
    except urllib.error.HTTPError as e:
        return None, ("USCITA IMPOSSIBILE" if e.code in (400, 404) else f"uscita http {e.code}"), None
    except Exception as e:
        return None, f"uscita {type(e).__name__}", None
    back = int(d2.get("outAmount") or 0) / 1e6
    rotte = len(d2.get("routePlan") or [])
    return back / usd - 1.0, float(d2.get("priceImpactPct") or 0) * 100, rotte


def misura(mint, motivo="stop"):
    """la sequenza completa nel momento della fuga. Ritorna le righe registrate."""
    righe = []
    t0 = time.time()
    for r in RITARDI:
        attesa = r - (time.time() - t0)
        if attesa > 0: time.sleep(attesa)
        for usd in TAGLIE:
            resa, imp, rotte = quota(mint, usd)
            righe.append({"ts": int(time.time()), "mint": mint, "motivo": motivo, "ritardo_s": r,
                          "size_usd": usd,
                          **({"resa_pct": round(resa * 100, 2), "impatto_pct": imp, "rotte": rotte}
                             if resa is not None else {"fallita": imp})})
            time.sleep(1.1)      # free tier: ~1 richiesta al secondo
    os.makedirs("data", exist_ok=True)
    with open(USCITA, "a") as f:
        for x in righe: f.write(json.dumps(x) + "\n")
    return righe


def riassunto():
    """cosa abbiamo imparato finora sul costo di uscire quando scappi."""
    import statistics as st
    righe = []
    if os.path.exists(USCITA):
        for l in open(USCITA):
            try: righe.append(json.loads(l))
            except Exception: pass
    L = ["# 🏃 QUANTO COSTA USCIRE MENTRE SCAPPI",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · {len(righe)} misure prese "
         f"**nell'istante dello stop**, non a mercato calmo · €0*", "",
         "> Tutte le altre nostre quote sono prese in un momento qualunque, cioè nel **momento",
         "> sbagliato**. Il prezzo che conta è quello che avresti pagato mentre il pool si svuotava e",
         "> tutti scappavano insieme a te — e quel momento dura pochi secondi: o lo catturi mentre",
         "> accade, o è perso per sempre.", "",
         "> **Le quote fallite sono il dato più prezioso**: una quota che non torna significa «in quel",
         "> momento non saresti uscito affatto», e vale più di dieci quote riuscite.", ""]
    if not righe:
        L += ["*Nessuna misura ancora: si registrano quando un paper trade tocca lo stop.*"]
    else:
        L += ["| dopo | $25 | $50 | $100 | quote fallite |", "|---|---|---|---|---|"]
        for r in RITARDI:
            cel = []
            fal = sum(1 for x in righe if x["ritardo_s"] == r and "fallita" in x)
            for usd in TAGLIE:
                v = [x["resa_pct"] for x in righe if x["ritardo_s"] == r and x["size_usd"] == usd
                     and "resa_pct" in x]
                cel.append(f"{st.median(v):+.1f}%" if v else "—")
            L.append(f"| {r}s | {cel[0]} | {cel[1]} | {cel[2]} | {fal} |")
        tot = len(righe); fall = sum(1 for x in righe if "fallita" in x)
        L += ["", f"Su **{tot}** tentativi, **{fall}** non hanno prodotto una quota eseguibile "
                  f"(**{fall*100//max(tot,1)}%**): in quei casi non saresti uscito."]
    open("COSTO_FUGA.md", "w").write("\n".join(L))
    return len(righe)


if __name__ == "__main__":
    m = os.environ.get("MINT", "").strip()
    if m:
        r = misura(m, os.environ.get("MOTIVO", "stop"))
        print(f"COSTO_FUGA | {len(r)} misure su {m[:8]}", flush=True)
    n = riassunto()
    print(f"COSTO_FUGA | archivio: {n} misure", flush=True)
