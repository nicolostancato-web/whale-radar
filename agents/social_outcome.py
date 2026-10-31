"""SOCIAL OUTCOME — cosa e' successo DOPO la fotografia, misurato senza poterla ritoccare.

IL PATTO CHE RENDE VALIDO L'ESPERIMENTO. Lo snapshot decide i token con cio' che si sapeva in quel
momento e non si tocca mai piu'. Questo agente guarda cosa e' successo dopo e lo scrive ALTROVE,
in un file separato. Non ha il permesso di modificare uno snapshot, e non ce l'ha per una ragione
sola: la tentazione di aggiustare a posteriori una selezione che e' andata male non e' un rischio
teorico, e' il modo normale in cui un risultato falso viene costruito da persone oneste.

LE FINESTRE: T+5 minuti, +30 minuti, +1 ora, +6 ore, +24 ore dall'ISTANTE DELLO SNAPSHOT — non da
quando gira questo agente. Ogni finestra si misura quando e' matura e poi si congela.

COSA SI MISURA: rendimento, massimo rialzo, massimo ribasso, prezzo massimo, volume, liquidita',
e se il token e' morto/non piu' scambiabile. Se una finestra non e' disponibile, si SCRIVE che non
lo e'. Una finestra mancante taciuta diventa, mesi dopo, una media calcolata solo sui sopravvissuti.

IL PREZZO DI PARTENZA E' UN PROBLEMA VERO, e va detto. Lo snapshot registra l'istante in cui Grok
ha risposto, ma il prezzo a quell'istante non lo conoscevamo: lo chiediamo ADESSO, alla prima
misura utile. Finche' la prima misura e' vicina allo snapshot (pochi minuti) lo scarto e' piccolo;
se questo agente parte in ritardo, il prezzo di riferimento e' gia' contaminato dal movimento.
Per questo ogni riga porta scritto QUANTO tardi e' stata presa la base: chi analizza deve poter
buttare via le righe con una base presa troppo tardi, invece di scoprirlo dopo.

GRATIS: GeckoTerminal, la stessa fonte che il progetto usa gia' altrove. Nessuna API a pagamento.
"""
import json
import os
import time
import urllib.request

GT = "https://api.geckoterminal.com/api/v2"
DIR = "data/social/snapshots"
OUT = "data/social/esiti.jsonl"
FINESTRE = [("T+5m", 300), ("T+30m", 1800), ("T+1h", 3600), ("T+6h", 21600), ("T+24h", 86400)]
TOLLERANZA = 900          # una finestra si misura entro un quarto d'ora dalla sua maturita'
BUDGET = int(os.environ.get("BUDGET_SEC", 300))
t0 = time.time()


def gt(percorso, tentativi=3):
    for k in range(tentativi):
        try:
            r = urllib.request.Request(f"{GT}{percorso}",
                                       headers={"Accept": "application/json",
                                                "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=30) as x:
                return json.load(x), None
        except Exception as e:
            if k < tentativi - 1:
                time.sleep(4 * (k + 1))
                continue
            return None, f"{type(e).__name__} {getattr(e, 'code', '')}"
    return None, "esauriti"


def mercato(chain, contract):
    """Prezzo, volume e liquidita' adesso. None se il token non si trova: non si inventa."""
    if not chain or not contract:
        return None
    d, err = gt(f"/networks/{chain}/tokens/{contract}")
    if not d:
        return {"errore": err}
    a = (d.get("data") or {}).get("attributes") or {}
    def num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None
    vol = a.get("volume_usd") or {}
    return {
        "prezzo": num(a.get("price_usd")),
        "volume_24h": num(vol.get("h24")),
        "liquidita": num(a.get("total_reserve_in_usd")),
        "market_cap": num(a.get("market_cap_usd") or a.get("fdv_usd")),
        "preso_a": int(time.time()),
    }


def main():
    os.makedirs("data/social", exist_ok=True)
    if not os.path.isdir(DIR):
        print("ESITI | nessuno snapshot", flush=True)
        return
    fatti = set()
    if os.path.exists(OUT):
        try:
            for l in open(OUT):
                if l.strip():
                    r = json.loads(l)
                    fatti.add((r.get("run_id"), r.get("token"), r.get("finestra"),
                               r.get("gruppo", "segnalato")))
        except Exception:
            pass

    ora = time.time()
    nuovi = mancate = 0
    for fn in sorted(os.listdir(DIR)):
        if time.time() - t0 > BUDGET:
            break
        try:
            snap = json.load(open(os.path.join(DIR, fn)))
        except Exception:
            continue
        ts = snap.get("ts")
        if not ts:
            continue
        # LO STESSO METRO PER SEGNALATI E CONTROLLO (16/09). Il gruppo di controllo serve a niente
        # se lo si misura con un altro strumento, in un altro momento o con altre finestre: la
        # differenza che si troverebbe potrebbe essere tutta li' dentro. Stesso agente, stesse
        # finestre, stessa fonte prezzi, stessa tolleranza. L'unica cosa che cambia e' l'etichetta.
        gruppi = ([("segnalato", tk) for tk in (snap.get("token") or [])] +
                  [("controllo", tk) for tk in (snap.get("controllo") or [])])
        for gruppo, tk in gruppi:
            sym = tk.get("symbol")
            chain = tk.get("chain")
            contract = tk.get("contract")
            for nome, quanti in FINESTRE:
                chiave = (snap["run_id"], sym, nome, gruppo)
                if chiave in fatti:
                    continue
                maturita = ts + quanti
                if ora < maturita:
                    continue                       # non ancora ora: si aspetta
                riga = {"run_id": snap["run_id"], "ts_snapshot": ts, "token": sym,
                        "chain": chain, "contract": contract, "finestra": nome,
                        "maturita": maturita, "misurato_a": int(ora),
                        "ritardo_misura_s": int(ora - maturita),
                        "versione_prompt": snap.get("versione_prompt"),
                        "classe": tk.get("classe"), "gruppo": gruppo,
                        "prezzo_allo_snapshot": tk.get("prezzo_allo_snapshot"),
                        "liquidita_allo_snapshot": tk.get("liquidita_allo_snapshot")}
                if ora - maturita > TOLLERANZA:
                    # TROPPO TARDI NON E' UNA MISURA (16/09). Misurare «T+5 minuti» tre ore dopo
                    # non da' un dato impreciso: da' un dato di un'altra cosa. Si registra la
                    # finestra come PERSA, cosi' nel conteggio finale si vede che quel dato non
                    # c'e' — invece di sparire e far sembrare completo un campione bucato.
                    riga.update({"esito": "FINESTRA PERSA",
                                 "motivo": f"misurabile solo {int((ora-maturita)/60)} min dopo la maturita'"})
                    mancate += 1
                else:
                    m = mercato(chain, contract)
                    if m is None:
                        riga.update({"esito": "NON MISURABILE",
                                     "motivo": "contract o chain assenti nello snapshot"})
                        mancate += 1
                    elif m.get("errore"):
                        riga.update({"esito": "NON MISURABILE", "motivo": m["errore"]})
                        mancate += 1
                    else:
                        riga.update({"esito": "ok", **m})
                        # UN PREZZO FERMO NON E' UNA MISURA (17/09). Nel primo confronto i token
                        # segnalati davano rapporti ESATTAMENTE 1.000 in ogni finestra: GIGADOG
                        # faceva 1.000 da T+5m a T+30m, a T+1h, a T+6h. Un prezzo che non si muove
                        # di un millesimo per sei ore non e' un prezzo fermo: e' l'ultimo prezzo
                        # noto di un token che NON SCAMBIA PIU', ripetuto dalla fonte.
                        # Contarlo come «rendimento zero» e' peggio che non misurarlo: mette in
                        # media con gli altri un dato che non esiste, e fa sembrare stabile una
                        # cosa che e' morta. Il gruppo di controllo intanto si muoveva davvero
                        # (un token a -82%), quindi il confronto sarebbe stato falsato in pieno.
                        # Adesso si guarda il volume: senza scambi, l'esito e' NON SCAMBIATO.
                        vol = m.get("volume_24h")
                        if vol is not None and vol < 1:
                            riga["esito"] = "NON SCAMBIATO"
                            riga["motivo"] = (f"volume 24h ${vol}: il prezzo e' l'ultimo noto, "
                                              f"non una quotazione viva")
                            mancate += 1
                        else:
                            nuovi += 1
                with open(OUT, "a") as f:
                    f.write(json.dumps(riga) + "\n")
                fatti.add(chiave)
    print(f"ESITI | {nuovi} misure nuove, {mancate} finestre perse o non misurabili", flush=True)


if __name__ == "__main__":
    main()
