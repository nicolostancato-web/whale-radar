#!/usr/bin/env python3
"""
COSTI_REALI — smettere di ASSUMERE il costo di un trade e MISURARLO.

Il punto piu' importante della consulenza esterna del 01/09: con i costi che abbiamo messo nel modello
(15% slippage per lato + 1% fee + 8% latenza) un token deve salire del 50% SOLO PER PAREGGIARE. Con
l'impatto di mercato al 45%, deve fare 2,9x. Ecco perche' tutte le chain risultano negative.
Ma quel 15% non l'abbiamo mai misurato: l'abbiamo scritto. Se il costo vero fosse il 5%, il pareggio
scenderebbe a ~1,12x e tutti i numeri andrebbero rifatti.

Qui si misura davvero: per ogni token vivo si chiede a Jupiter (gratis) quanto costa comprare N dollari
e rivenderli subito. La differenza e' il costo di andata e ritorno REALE, con la route vera e l'impatto vero.
E se non c'e' route per vendere, quello e' il dato piu' importante di tutti: il token non e' vendibile.

Scrive COSTI_REALI.md + data/costi_reali.json. €0 (Jupiter lite-api, nessuna chiave).
"""
import json, os, glob, time, urllib.request, statistics as st

USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDC_DEC = 6
API = "https://lite-api.jup.ag/swap/v1/quote"
SIZES = [25, 100, 500]          # dollari per posizione: il costo dipende da quanto compri
PAUSA = 1.1                     # free tier: ~1 richiesta al secondo
MAX_TOKEN = int(os.environ.get("MAX_TOKEN", 40))
ARCHIVIO = "data/costi_archivio.json"                  # storico, resta per non perdere il passato
# UN ARCHIVIO PER SCRITTORE (04/09). Il motore e la ricerca eseguono ENTRAMBI questo agente, e
# scrivevano lo stesso file. Ogni processo committa con `git add -A` e risolve i conflitti tenendo
# la PROPRIA copia: cosi' chi pubblicava per ultimo riportava indietro l'archivio alla sua versione,
# distruggendo misure che non aveva mai toccato. L'archivio e' passato da 800 a 609 senza che nessuno
# cancellasse niente — il piu' insidioso dei guasti, perche' i numeri scendono e il codice e' corretto.
# Due file separati non possono sovrascriversi. Chi legge li somma.
SORGENTE = os.environ.get("SORGENTE", "engine")
MIO = f"data/costi/{SORGENTE}.json"
BUDGET = int(os.environ.get("BUDGET_SEC", 500))
now = int(time.time()); t0 = time.time()


def quote(inp, out, amount):
    """(outAmount, impatto%) oppure (None, motivo) — la mancanza di route E' un dato, non un errore."""
    url = f"{API}?inputMint={inp}&outputMint={out}&amount={int(amount)}&slippageBps=300"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}),
                                    timeout=20) as r:
            d = json.loads(r.read())
        return int(d["outAmount"]), float(d.get("priceImpactPct") or 0) * 100
    except urllib.error.HTTPError as e:
        return None, ("nessuna route" if e.code in (400, 404) else f"http {e.code}")
    except Exception as e:
        return None, type(e).__name__


def token_vivi():
    """I mint dei token che seguiamo.

    Attenzione: nei nostri dati salviamo l'indirizzo del POOL, non del token. Jupiter vuole il mint.
    DexScreener risolve i due (30 pool per chiamata, gratis) — e questo e' anche il motivo per cui
    il primo tentativo dava zero risultati: stavamo chiedendo quote su indirizzi sbagliati."""
    pools = []
    pf = "data/multichain/solana/pools.json"
    if os.path.exists(pf):
        try:
            p = json.load(open(pf))
            pools = [a for a, v in sorted(p.items(), key=lambda kv: kv[1].get("created", ""), reverse=True)]
        except Exception: pass
    if not pools:
        pools = [os.path.basename(f).replace(".jsonl.gz", "")
                 for f in glob.glob("data/multichain/solana/trades/*.jsonl.gz")]
    # ROTAZIONE (02/09): senza questa, ogni giro ripartiva dai pool piu' recenti e rimisurava gli stessi
    # token. Alle 23:26 ne ha rifatti 16 gia' in archivio: l'archivio sembrava "fermo a 24" mentre in
    # realta' lavorava — su cio' che sapeva gia'. Un contatore che non sale non e' sempre un motore fermo:
    # a volte e' un motore che gira a vuoto, ed e' piu' difficile da vedere.
    if len(pools) > 300:
        salto = int((now // 3600) * 300) % len(pools)
        pools = pools[salto:] + pools[:salto]
    mint = []
    # PRIMA I TOKEN DI CUI ABBIAMO LE CANDELE (03/09).
    # Scoperta imbarazzante: delle 212 misure accumulate, ZERO erano agganciabili a un pool con una
    # serie di prezzi. Stavamo misurando benissimo il costo di token che non studiamo, e studiando
    # token di cui non conosciamo il costo. Due meta' di dato che non si parlano — lo stesso errore
    # gia' trovato sul censimento, ripetuto qui senza accorgersene.
    # Serve per calibrare il costo di uscita sulla LIQUIDITA' vera: senza l'aggancio candele-costo
    # quella curva non si puo' nemmeno stimare, e resta un moltiplicatore assunto.
    try:
        rub = json.load(open("data/multichain/solana/token_map.json"))
        low = {k.lower(): v for k, v in rub.items()}
        con_serie = set()
        for pat in ("candles", "serie", "candele"):   # nomi storici diversi, cerchiamo tutti
            con_serie |= {os.path.basename(x).replace(".jsonl.gz", "").lower()
                          for x in glob.glob(f"data/multichain/solana/{pat}/*.jsonl.gz")}
        studiabili = [(low[a], 0, "STUDIABILE") for a in con_serie if a in low]
        mint += studiabili
        mint += [(low[a.lower()], 0, "?") for a in pools[:400] if a.lower() in low]
        if studiabili: print(f"COSTI_REALI | {len(studiabili)} token hanno ANCHE le candele: misurati per primi", flush=True)
    except Exception: pass
    for i in range(0, min(len(pools), 300), 30):
        chunk = pools[i:i + 30]
        try:
            url = "https://api.dexscreener.com/latest/dex/pairs/solana/" + ",".join(chunk)
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "wr"}),
                                        timeout=20) as r:
                d = json.loads(r.read())
            for pr in (d.get("pairs") or []):
                b = (pr.get("baseToken") or {}).get("address")
                liq = float((pr.get("liquidity") or {}).get("usd") or 0)
                if b and b != "So11111111111111111111111111111111111111112":
                    mint.append((b, liq, (pr.get("baseToken") or {}).get("symbol", "?")))
        except Exception: pass
        time.sleep(0.3)
        if len(mint) >= MAX_TOKEN * 2: break
    return mint


def leggi_tutti():
    """l'unione di tutti gli archivi: il mio, quelli degli altri scrittori, e lo storico."""
    out = {}
    for f in sorted(glob.glob("data/costi/*.json")) + [ARCHIVIO]:
        try: out.update(json.load(open(f)))
        except Exception: pass
    return out


def main():
    lista = token_vivi()
    # PRIMA i mint mai misurati. Riverificare un token gia' in archivio ha un valore (il costo cambia
    # nel tempo), ma molto minore di coprirne uno nuovo: con 24 misure non possiamo ancora permettercelo.
    try: gia = set(json.load(open(ARCHIVIO)))
    except Exception: gia = set()
    lista = [x for x in lista if x[0] not in gia] + [x for x in lista if x[0] in gia]
    if not lista:
        print("COSTI_REALI | nessun mint risolto", flush=True); return

    ris = []; senza_uscita = 0; provati = 0
    for a, liq, sym in lista:
        if time.time() - t0 > BUDGET or provati >= MAX_TOKEN: break
        riga = {"mint": a, "simbolo": sym, "liquidita": round(liq), "size": {}}
        vivo = False
        for s in SIZES:
            if time.time() - t0 > BUDGET: break
            # 1) compro s dollari di token
            out, imp_buy = quote(USDC, a, s * 10 ** USDC_DEC)
            time.sleep(PAUSA)
            if out is None:
                riga["size"][s] = {"errore": f"acquisto: {imp_buy}"}; continue
            vivo = True
            # 2) li rivendo subito: quanto torna indietro?
            back, imp_sell = quote(a, USDC, out)
            time.sleep(PAUSA)
            if back is None:
                riga["size"][s] = {"errore": f"VENDITA IMPOSSIBILE: {imp_sell}", "buy_impact": imp_buy}
                senza_uscita += 1; continue
            tornati = back / 10 ** USDC_DEC
            costo = (1 - tornati / s) * 100          # costo di andata e ritorno, in %
            riga["size"][s] = {"costo_roundtrip_pct": round(costo, 2),
                               "impatto_acquisto_pct": round(imp_buy, 3),
                               "impatto_vendita_pct": round(imp_sell, 3)}
        if vivo: ris.append(riga); provati += 1

    json.dump({"ts": now, "token": ris, "senza_uscita": senza_uscita}, open("data/costi_reali.json", "w"))

    # ARCHIVIO CUMULATIVO (aggiunto 02/09 dopo la consulenza esterna).
    # Prima ogni giro RISCRIVEVA il file: restavano 5 token, e su 5 token non si decide niente —
    # eppure quel numero e' il piu' importante del sistema, perche' da lui dipende il pareggio.
    # Ora ogni misura si somma alle precedenti e il verdetto si legge sull'archivio intero.
    tutto = leggi_tutti()          # quello che sanno tutti gli scrittori, storico incluso
    mio = {}
    if os.path.exists(MIO):
        try: mio = json.load(open(MIO))
        except Exception: mio = {}
    for r in ris:
        r["ts"] = now; mio[r["mint"]] = r; tutto[r["mint"]] = r
    os.makedirs("data/costi", exist_ok=True)
    json.dump(mio, open(MIO, "w"))     # scrivo SOLO il mio: nessuno puo' sovrascrivere nessuno
    ris = list(tutto.values())
    senza_uscita = sum(1 for r in ris for s in r["size"].values()
                       if isinstance(s, dict) and "VENDITA IMPOSSIBILE" in str(s.get("errore", "")))

    L = ["# 💸 COSTI REALI — quanto costa DAVVERO entrare e uscire",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · quote vere da Jupiter su {len(ris)} token "
         f"Solana vivi · €0*", "",
         "> **Perché**: nel modello assumiamo 15% di slippage per lato. Non l'abbiamo mai misurato.",
         "> Con quel 15% un token deve salire del **50% solo per pareggiare**; se il costo vero fosse molto",
         "> più basso, tutti i numeri di questi giorni andrebbero rifatti.", ""]
    if not ris:
        L += ["Nessuna quota ottenuta in questo giro."]
    else:
        L += ["| size | costo andata+ritorno (mediana) | migliore | peggiore | token misurati |",
              "|---|---|---|---|---|"]
        riassunto = {}
        for s in SIZES:
            v = [r["size"][s]["costo_roundtrip_pct"] for r in ris
                 if s in r["size"] and "costo_roundtrip_pct" in r["size"][s]]
            if not v: continue
            v.sort(); riassunto[s] = st.median(v)
            L.append(f"| ${s} | **{st.median(v):.1f}%** | {v[0]:.1f}% | {v[-1]:.1f}% | {len(v)} |")
        vendibili = sum(1 for r in ris if any("costo_roundtrip_pct" in v for v in r["size"].values()
                                              if isinstance(v, dict)))
        quota_morti = (1 - vendibili / len(ris)) * 100 if ris else 0
        L += ["", f"- misure accumulate finora: **{len(ris)} token** (l'archivio cresce a ogni giro)",
              f"- token che NON si possono rivendere: **{len(ris)-vendibili}** su {len(ris)} "
              f"(**{quota_morti:.0f}%**)", "",
              "> Il costo qui sotto vale **solo per i token vendibili**. Quelli invendibili non sono un costo",
              "> alto: sono una perdita totale, e vanno contati a parte — non spalmati sulla media.", ""]
        if riassunto:
            base = riassunto.get(100) or list(riassunto.values())[0]
            # break-even col costo misurato, stessa formula della consulenza
            r = base / 100
            be = 1 / (1 - r) if r < 0.95 else 99
            L += ["## Cosa cambia", "",
                  f"Costo misurato di andata e ritorno su ${100}: **{base:.1f}%** contro il **~30%** che assumiamo.",
                  f"Pareggio necessario: **{be:.2f}x** contro l'**1,50x** del modello attuale.", ""]
            if base < 20:
                L += ["> ⚠️ **Il costo assunto è molto più alto di quello misurato.** Prima di dichiarare morto",
                      "> un mercato, i numeri vanno rifatti con il costo vero — su questi token, in questo momento.", ""]
    L += ["> Nota onesta: sono quote **indicative** al momento della misura, su token vivi oggi. Non dicono",
          "> quanto sarebbe costato uscire durante un crollo, né includono gas e transazioni fallite. Servono",
          "> a sapere se l'ordine di grandezza che usiamo è giusto — e quello è già molto più di un'assunzione."]
    open("COSTI_REALI.md", "w").write("\n".join(L))
    print(f"COSTI_REALI | {len(ris)} token misurati | {senza_uscita} non vendibili", flush=True)


if __name__ == "__main__":
    main()
