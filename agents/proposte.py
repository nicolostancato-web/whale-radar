#!/usr/bin/env python3
"""
PROPOSTE — la coda fra il team e l'investitore.

Il team trova cose (es. su Robinhood una configurazione che vale 32 punti in più di quella in uso) e le
scrive nei suoi file. Ma una scoperta che resta in un file non è una scoperta: è un appunto. Qui diventa una
PROPOSTA con un numero, uno stato e una data — e resta aperta finché l'investitore non decide.

Il team NON applica da solo: cambiare la strategia viva è una decisione (STRATEGIA_LOOP.md). Questo file
serve a non perdere nulla per strada e a far vedere, in una pagina, cosa aspetta una risposta.
Scrive PROPOSTE.md + data/proposte.json. €0.
"""
import json, os, time, hashlib

now = int(time.time())
ARCHIVIO = "data/proposte.json"
STORICO = "data/proposte_storico.jsonl"      # append-only: qui NON si cancella mai niente
EVAPORATE = "data/evaporate.json"            # le configurazioni gia' cadute: non si ripescano
SOGLIA = 3.0        # sotto i 3 punti di guadagno non disturbiamo l'investitore


def impronta(chain, dettaglio):
    """firma di una configurazione: serve a riconoscerla se il team la ri-propone piu' avanti."""
    testo = chain + "|" + "|".join(f"{k}={dettaglio[k]}" for k in sorted(dettaglio) if k != "mask")
    return hashlib.md5(testo.encode()).hexdigest()[:10]


def carica_evaporate():
    if os.path.exists(EVAPORATE):
        try: return json.load(open(EVAPORATE))
        except Exception: pass
    return {}


def gia_caduta(chain, dettaglio):
    """(sì/no, cosa era successo). Se una configurazione è già evaporata una volta, il team lo deve SAPERE:
    ripescare una cosa già caduta è il modo più veloce di perdere tempo."""
    ev = carica_evaporate().get(impronta(chain, dettaglio))
    if not ev: return False, ""
    return True, (f"già proposta il {time.strftime('%d/%m alle %H:%M', time.gmtime(ev['ts']))} a "
                  f"{ev['era']:+.0f}% ed EVAPORATA (scesa a {ev['scesa_a']:+.0f}%)")


def registra_caduta(p, val):
    """una proposta che non ha retto finisce nello storico E nella lista delle evaporate, per sempre."""
    imp = impronta(p["chain"], p.get("dettaglio", {}))
    ev = carica_evaporate()
    voce = {"ts": int(time.time()), "chain": p["chain"], "tipo": p.get("tipo"),
            "era": p.get("a"), "scesa_a": round(val, 1), "regge_da_ore": round((time.time() - p.get("nata", time.time())) / 3600, 1),
            "dettaglio": p.get("dettaglio", {}), "cadute": ev.get(imp, {}).get("cadute", 0) + 1}
    ev[imp] = voce
    json.dump(ev, open(EVAPORATE, "w"))
    with open(STORICO, "a") as fo:
        fo.write(json.dumps(dict(voce, esito="EVAPORATA")) + "\n")


def carica():
    if os.path.exists(ARCHIVIO):
        try: return json.load(open(ARCHIVIO))
        except Exception: pass
    return {"proposte": []}


def main():
    arch = carica()
    aperte = {p["id"]: p for p in arch["proposte"]}

    # 1. dagli esploratori: configurazioni che battono quella in uso
    for f, chain, campo_live in (("data/explorer_rh.json", "robinhood", "partenza"),
                                 ("data/explorer_base.json", "base", None),
                                 ("data/explorer_solana.json", "solana", None)):
        if not os.path.exists(f): continue
        try: st = json.load(open(f))
        except Exception: continue
        best = st.get("best") or {}
        val = st.get("punteggio", st.get("robusta"))
        if val is None: continue
        rif = st.get("partenza")
        if rif is None:
            # per le chain multichain il riferimento è la percentuale attuale del loop 1
            try:
                recs = [json.loads(l) for l in open("data/multichain_history.jsonl") if l.strip()]
                recs = [r for r in recs if r.get("chain") == chain]
                rif = recs[-1]["robusta"] if recs else None
            except Exception: rif = None
        if rif is None: continue
        guadagno = val - rif
        if guadagno < SOGLIA: continue
        pid = f"{chain}-configurazione"
        vecchia = aperte.get(pid)
        # QUANTO REGGE NEL TEMPO: una proposta trovata in due ore non e' un fatto, e' una scoperta. Contiamo
        # da quanti controlli consecutivi resta in piedi e da quante ore esiste: solo cosi' si puo' decidere.
        conferme = (vecchia.get("conferme", 0) + 1) if vecchia and val >= vecchia.get("a", -999) - 3 else 0
        nata = vecchia.get("nata", now) if vecchia and conferme else now
        if vecchia and vecchia.get("a", -999) > val + 3:
            # e' PEGGIORATA: non ha retto. Va nello STORICO e nella lista delle evaporate, cosi' se il team
            # la ri-propone fra una settimana sappiamo subito che ci abbiamo gia' sbattuto la testa.
            registra_caduta(vecchia, val)
            aperte[pid] = dict(vecchia, ts=now, calata_da=vecchia.get("a"), a=round(val, 1),
                               guadagno=round(guadagno, 1), conferme=0, nata=now)
            continue
        caduta, storia = gia_caduta(chain, {k: v for k, v in best.items() if k != "mask"})
        aperte[pid] = {"id": pid, "ts": now, "chain": chain, "tipo": "configurazione",
                       "da": round(rif, 1), "a": round(val, 1), "guadagno": round(guadagno, 1),
                       "dettaglio": {k: v for k, v in best.items() if k != "mask"},
                       "conferme": conferme, "nata": nata, "stato": "APERTA",
                       "gia_caduta": storia if caduta else ""}

    # 2. dal ricercatore: segnali nuovi promossi
    for chain in ("base", "solana", "robinhood"):
        f = f"data/ricerca_{chain}.json"
        if not os.path.exists(f): continue
        try: st = json.load(open(f))
        except Exception: continue
        for p in st.get("promosse", []):
            pid = f"{chain}-segnale-{p['nome']}"
            if pid in aperte: continue
            aperte[pid] = {"id": pid, "ts": now, "chain": chain, "tipo": "segnale nuovo",
                           "da": st.get("partenza"), "a": p["robusta"], "guadagno": p["guadagno"],
                           "dettaglio": {"segnale": p["nome"]}, "stato": "APERTA"}

    # DEDUP FINALE: restano proposte vecchie con id di formato superato, e cosi' la stessa configurazione
    # compariva tre volte con numeri diversi. Ne teniamo UNA per chain+tipo: la migliore.
    migliori = {}
    for p in sorted(aperte.values(), key=lambda p: -p.get("a", -999)):
        k = (p.get("chain"), p.get("tipo"))
        if k in migliori:
            # non si perde la memoria: se la doppione era piu' vecchia, ne conserviamo le conferme
            migliori[k]["conferme"] = max(migliori[k].get("conferme", 0), p.get("conferme", 0))
            migliori[k]["nata"] = min(migliori[k].get("nata", now), p.get("nata", now))
            continue
        migliori[k] = p
    arch["proposte"] = sorted(migliori.values(), key=lambda p: -p["guadagno"])[:60]
    json.dump(arch, open(ARCHIVIO, "w"))

    # IL VERDETTO DEL GIUDICE CHIUDE LA PROPOSTA (01/09).
    # Difetto trovato dal loop: il validatore bocciava una proposta ("in cassaforte fa -49%: era rumore") e
    # quella restava sul tavolo con il suo bel +67%, come se niente fosse. Il giro completo — scoperta,
    # validazione, verdetto, archiviazione — non si chiudeva mai. Ora si chiude: una proposta bocciata sui
    # dati mai visti esce dalla coda e finisce nel cimitero, dove resta consultabile per sempre.
    for p in arch["proposte"]:
        v = p.get("validazione")
        if p.get("stato") == "APERTA" and v and v.get("robusta", 999) <= 0:
            p["stato"] = "BOCCIATA"
            try:
                registra_caduta(dict(p, a=p.get("a")), v.get("robusta", 0))
            except Exception:
                pass
    json.dump(arch, open(ARCHIVIO, "w"))

    ap = [p for p in arch["proposte"] if p["stato"] == "APERTA"]
    bocciate_ora = [p for p in arch["proposte"] if p.get("stato") == "BOCCIATA"]
    L = ["# 📋 PROPOSTE — cosa aspetta una tua decisione",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · {len(ap)} aperte*", ""]
    if not ap:
        L += ["**Nessuna proposta aperta.** Il team sta cercando e finora non ha trovato niente che valga",
              f"almeno {SOGLIA:.0f} punti in più di quello che facciamo adesso.", ""]
    if bocciate_ora:
        L += [f"> **{len(bocciate_ora)} proposte sono state bocciate dal giudice** e tolte dal tavolo: sui token",
              "> mai visti dalla ricerca non reggevano. Le trovi nel cimitero qui sotto.", ""]
    else:
        L += ["| # | chain | cosa propone | da → a | guadagno | **quanto regge** |", "|---|---|---|---|---|---|"]
        for i, p in enumerate(ap, 1):
            d = p["dettaglio"]
            desc = (d.get("segnale") or ", ".join(f"{k}={v}" for k, v in list(d.items())[:5]))
            ore = (now - p.get("nata", now)) / 3600
            conf = p.get("conferme", 0)
            if p.get("calata_da"):
                tenuta = f"⚠️ **calata** da {p['calata_da']:+.0f}%: non ha retto"
            elif conf >= 12 and ore >= 12:
                tenuta = f"✅ **solida** — regge da {ore:.0f}h ({conf} controlli)"
            elif conf >= 4:
                tenuta = f"🟡 regge da {ore:.0f}h ({conf} controlli)"
            else:
                tenuta = f"🆕 appena trovata ({ore:.0f}h) — **troppo presto**"
            if p.get("gia_caduta"): tenuta = f"🔁 **RIPESCATA** — {p['gia_caduta']}"
            L.append(f"| {i} | {p['chain']} | {p['tipo']}: `{desc}` | "
                     f"{('%+.0f%%' % p['da']) if p.get('da') is not None else '?'} → **{p['a']:+.0f}%** | "
                     f"**{p['guadagno']:+.0f} punti** | {tenuta} |")
        L += ["", "> **Quando una proposta è matura:** quando regge per almeno **12 ore** e **12 controlli**",
              "> consecutivi senza calare. Una configurazione trovata in due ore di ricerca non è un fatto:",
              "> è una scoperta, e le scoperte a volte evaporano al controllo successivo.", "",
              "> **Come si approva:** basta dirlo — la decisione viene scritta in `DECISIONS.md` e la",
              "> configurazione applicata al sistema. Il team non lo fa da solo di proposito: cambiare la",
              "> strategia viva è una scelta dell'investitore, non un'ottimizzazione automatica.", ""]
    # IL CIMITERO: cosa abbiamo già provato e non ha retto. Non si cancella mai.
    storia = []
    if os.path.exists(STORICO):
        try: storia = [json.loads(l) for l in open(STORICO) if l.strip()]
        except Exception: storia = []
    if storia:
        L += ["## ⚰️ Il cimitero — proposte che NON hanno retto", "",
              "| quando | chain | era | è scesa a | aveva retto | quante volte è caduta |", "|---|---|---|---|---|---|"]
        for e in storia[-12:][::-1]:
            L.append(f"| {time.strftime('%d/%m %H:%M', time.gmtime(e['ts']))} | {e['chain']} | "
                     f"{e.get('era', 0):+.0f}% | {e['scesa_a']:+.0f}% | {e.get('regge_da_ore', 0):.0f}h | "
                     f"{e.get('cadute', 1)} |")
        L += ["", "> Queste non si ripescano. Se il team ri-propone una configurazione già caduta, la riga",
              "> sopra viene marcata **RIPESCATA** con la data della volta scorsa: così non ci sbattiamo la",
              "> testa due volte. Lo storico completo è in `data/proposte_storico.jsonl`, append-only.", ""]
    L += ["> Le proposte nascono quando il team trova qualcosa che batte di almeno "
          f"{SOGLIA:.0f} punti ciò che facciamo oggi, misurato con lo stesso metro severo (deve reggere anche",
          "> sui token recenti)."]
    open("PROPOSTE.md", "w").write("\n".join(L))
    print(f"PROPOSTE | {len(ap)} aperte", flush=True)


if __name__ == "__main__":
    main()
