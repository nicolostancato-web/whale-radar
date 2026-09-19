#!/usr/bin/env python3
"""
MORTALITA' — quanti token muoiono e SPARISCONO dai nostri dati (survivorship bias).

Il problema, sollevato dalla revisione critica del 31/08: noi impariamo sui token che sono sopravvissuti
abbastanza da avere una serie di prezzi. I rug istantanei, i pool che nessuno scambia, quelli che le API
smettono di riportare — semplicemente non entrano nel campione. Risultato: nello storico ci sono meno
-100% di quanti ne incontreremmo comprando dal vivo, e ogni percentuale che calcoliamo è ottimista.

Qui il numero viene MISURATO, non ignorato: quanti pool scopriamo, quanti arrivano ad avere dati veri,
quanti spariscono per strada. E da lì esce una PENALITA' onesta da applicare alle percentuali.
Scrive MORTALITA.md + data/mortalita.json. €0.
"""
import json, os, glob, gzip, time, datetime, sys
sys.path.insert(0, "agents")
import multichain_brain as B

CHAINS = ["base", "solana", "bsc"]
now = int(time.time())


def eta_ore(p):
    c = p.get("created")
    if c:
        try:
            return (now - datetime.datetime.strptime(c, "%Y-%m-%dT%H:%M:%SZ")
                    .replace(tzinfo=datetime.timezone.utc).timestamp()) / 3600
        except Exception: pass
    return (now - p.get("seen", now)) / 3600


def analizza(chain):
    base = f"data/multichain/{chain}"
    pf = f"{base}/pools.json"
    if not os.path.exists(pf): return None
    try: pools = json.load(open(pf))
    except Exception: return None
    # guardiamo solo i pool abbastanza vecchi da aver AVUTO il tempo di produrre dati (>12h)
    maturi = {a: p for a, p in pools.items() if eta_ore(p) > 12}
    if len(maturi) < 50: return None
    con_serie = {os.path.basename(f).replace(".jsonl.gz", "") for f in B.serie_files(chain)}
    usabili = 0
    for f in B.serie_files(chain):
        addr = os.path.basename(f).replace(".jsonl.gz", "")
        if addr not in maturi: continue
        try:
            n = sum(1 for l in gzip.open(f, "rt") if json.loads(l).get("cl"))
            if n >= B.MIN_CANDLES: usabili += 1
        except Exception: pass
    # DISTINZIONE CRUCIALE: "senza dati" non vuol dire "morto". La maggior parte dei pool non ha dati
    # perche' non abbiamo mai provato a scaricarli (il collector ne fa poche decine per giro su migliaia).
    # Il tasso di MORTE vero si misura solo su quelli che abbiamo davvero TENTATO.
    tentati = set()
    ck = f"{base}/ckpt.json"
    if os.path.exists(ck):
        try: tentati = set(json.load(open(ck)).get("last_fetch", {}))
        except Exception: pass
    tent_maturi = [a for a in maturi if a in tentati]
    tent_con_dati = [a for a in tent_maturi if a in con_serie]
    visti = len(maturi)
    n_tent = len(tent_maturi)
    return {"scoperti": visti, "con_dati": usabili, "mai_tentati": visti - n_tent,
            "tentati": n_tent, "tentati_vuoti": n_tent - len(tent_con_dati),
            "tasso_morte": (n_tent - len(tent_con_dati)) / n_tent if n_tent else 0.0}


def main():
    out = {}
    for ch in CHAINS:
        a = analizza(ch)
        if a: out[ch] = a
    json.dump({"ts": now, "chain": out}, open("data/mortalita.json", "w"))

    L = ["# ⚰️ MORTALITÀ — quanti token spariscono prima di entrare nei nostri conti",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))}*", "",
         "> **Perché conta:** impariamo sui token sopravvissuti abbastanza da avere una serie di prezzi. Chi",
         "> muore subito non entra nel campione — quindi nello storico ci sono **meno −100% di quanti ne",
         "> incontreremmo davvero**, e ogni percentuale che calcoliamo è ottimista di conseguenza.", "",
         "| chain | pool scoperti (>12h) | mai tentati (limite nostro) | **tentati** | senza dati = morti | tasso di morte |",
         "|---|---|---|---|---|---|"]
    for ch, a in out.items():
        L.append(f"| {ch} | {a['scoperti']} | {a['mai_tentati']} | {a['tentati']} | "
                 f"**{a['tentati_vuoti']}** | **{a['tasso_morte']*100:.0f}%** |")
    if out:
        peggio = max(a["tasso_morte"] for a in out.values())
        media = sum(a["tasso_morte"] for a in out.values()) / len(out)
        L += ["", f"## Come si legge", "",
              "**\"Mai tentati\"** non è mortalità: è un limite nostro (le API gratuite ci lasciano scaricare",
              "poche decine di pool per giro su migliaia scoperti). Quelli non dicono niente sul mercato.", "",
              f"**Il tasso di morte vero** è calcolato solo sui pool che abbiamo davvero interrogato: in media",
              f"il **{media*100:.0f}%** di quelli non ha mai prodotto una serie di prezzi utilizzabile — nati morti,",
              "o morti entro poche ore.", "",
              f"**Regola prudente:** finché non misuriamo quanti muoiono DOPO l'entrata, trattiamo ogni",
              f"percentuale come ottimista di almeno qualche punto, e non apriamo mai il live su un numero",
              f"appena sopra la soglia. È uno dei motivi per cui il cancello è a +40% e non a +5%.", ""]
    L += ["> Prossimo passo su questo: contare i token che avevano dati e poi **smettono di aggiornarsi**",
          "> mentre il prezzo crolla — quelli sono i rug veri, ed è lì che si nasconde il -100% che non vediamo."]
    open("MORTALITA.md", "w").write("\n".join(L))
    print("MORTALITA | " + " · ".join(f"{c} {a['tasso_morte']*100:.0f}%" for c, a in out.items()), flush=True)


if __name__ == "__main__":
    main()
