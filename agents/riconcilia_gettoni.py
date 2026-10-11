"""I GETTONI TORNANO? La prova che non ha bisogno di nessun prezzo.

== PERCHE' QUESTA MISURA E NON UN MULTIPLO IN EURO ==

Per dire «questo portafoglio ha guadagnato X» serve un prezzo, e un prezzo sbagliato ha gia'
prodotto due disastri in questo progetto (un valore di 16 milioni inesistente il 3/10, e il 6/10
una somma di importi in 72 valute diverse che stavo per scrivere in euro).

Questa misura non ne ha bisogno. Chiede solo: **i gettoni venduti erano stati comprati?**
E' un conteggio di pezzi, non di soldi. Se i pezzi non tornano, qualunque multiplo e' finto;
se tornano, il multiplo si puo' calcolare dopo, con calma e con le unita' giuste.

I memecoin creati dalla fabbrica hanno sempre 18 decimali, quindi questa misura **non e' stata
toccata** dall'errore sulle valute di quotazione: il lato gettoni era giusto anche quando il lato
denaro era sbagliato.

== IL RISULTATO DEL 6/10, su 66 posizioni confrontabili ==

                              solo col pool     con la curva
  venduti/comprati (mediana)       1,50             0,98
  casi impossibili (vende e
  non ha mai comprato)              43                0

**Tutti e 43 i casi impossibili hanno trovato la provenienza.** Il 53% quadra entro il 5%.
Quello che restava fuori non era un difetto del nostro conto: era un mercato che non leggevamo.

Il 47% che ancora non quadra ha una spiegazione candidata e NON verificata: i gettoni spostati
fra due portafogli della stessa persona (un semplice trasferimento, nessuno swap). Va misurato,
non assunto.

== LA CATENA, E DOVE SI PUO' ROMPERE ==

  portafoglio + curva  ->  gettone  ->  pool  ->  la nostra posizione

 · curva -> gettone  viene dall'elenco dei lanci (675.145 monete);
 · gettone -> pool   viene dal registro delle coppie (69.697 pool);
 · un gettone puo' avere PIU' pool: si confronta con ognuno, e si dichiara quante volte capita.

Dove un anello manca, la posizione NON si confronta e si conta a parte. Un confronto saltato in
silenzio diventa «quadra», che e' la conclusione piu' comoda e quella sbagliata.
"""
import collections
import glob
import gzip
import json
import os
import statistics
import sys

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
SOMME = os.environ.get("SOMME", f"{BASE}/curva_somme_pezzo_*.json.gz")
DETTAGLI = os.environ.get("DETTAGLI", f"{BASE}/dettaglio_candidati_pezzo_*.json")
FUORI = os.environ.get("FUORI", f"{BASE}/riconciliazione.json")
BANDA = 0.05


def main():
    pl = f"{BASE}/curva_lanci.json.gz"
    if not os.path.exists(pl):
        raise SystemExit(f"RICONCILIA | manca {pl}: senza l'elenco dei lanci non so a quale "
                         f"moneta appartiene una curva, e non invento la corrispondenza")
    dl = json.load(gzip.open(pl, "rt"))
    curva2tok = {v["curva"].lower(): t.lower() for t, v in dl["da"].items()}

    pc = f"{BASE}/coppie.json"
    if not os.path.exists(pc):
        raise SystemExit(f"RICONCILIA | manca {pc}: senza il registro delle coppie non so in "
                         f"quale pool si scambia una moneta")
    tok2pool = collections.defaultdict(list)
    for pool, v in json.load(open(pc))["coppie"].items():
        for lato in ("t0", "t1"):
            a = (v.get(lato) or "").lower()
            if a and a != "0x" + "0" * 40:
                tok2pool[a].append(pool.lower())

    pos = {}
    for f in sorted(glob.glob(DETTAGLI, recursive=True)):
        for w, d2 in json.load(open(f)).items():
            pos.setdefault(w.lower(), {}).update({k.lower(): v for k, v in d2.items()})
    if not pos:
        raise SystemExit(f"RICONCILIA | nessuna posizione in {DETTAGLI}: non confronto il nulla")
    print(f"RICONCILIA | {len(curva2tok):,} curve, {len(tok2pool):,} monete con pool, "
          f"{len(pos):,} portafogli con posizioni", flush=True)

    cand = set(pos)
    netti = collections.defaultdict(float)
    curve_senza_moneta = 0
    for p in sorted(glob.glob(SOMME, recursive=True)):
        try:
            d = json.load(gzip.open(p, "rt")).get("da", {})
        except Exception as e:
            print(f"   {os.path.basename(p)} illeggibile ({str(e)[:50]}): lo salto e lo dico",
                  flush=True)
            continue
        for k, v in d.items():
            w, cu = k.split("|")
            if w not in cand:
                continue
            t = curva2tok.get(cu)
            if not t:
                curve_senza_moneta += 1
                continue
            netti[(w, t)] += v["compra_gettoni"] - v["vende_gettoni"]
        del d
    print(f"RICONCILIA | {len(netti):,} coppie (portafoglio x moneta) con gettoni dalla curva, "
          f"{curve_senza_moneta:,} curve senza moneta nota", flush=True)

    prima, dopo, quadrano, senza_pool, senza_posizione, piu_pool = [], [], 0, 0, 0, 0
    esempi = []
    for (w, t), net in netti.items():
        pools = tok2pool.get(t, [])
        if not pools:
            senza_pool += 1
            continue
        if len(pools) > 1:
            piu_pool += 1
        trovata = False
        for pool in pools:
            z = pos.get(w, {}).get(pool)
            if not z:
                continue
            gin = z.get("gin", 0) / 1e18
            gout = z.get("gout", 0) / 1e18
            if gout <= 0:
                continue
            trovata = True
            prima.append(gout / gin if gin > 0 else None)
            d2 = gout / (gin + net) if (gin + net) > 0 else None
            dopo.append(d2)
            if d2 is not None and abs(d2 - 1) <= BANDA:
                quadrano += 1
                if len(esempi) < 12 and z.get("tx_vende"):
                    esempi.append({"portafoglio": w, "moneta": t, "pool": pool,
                                   "gettoni_dalla_curva": net, "gettoni_dal_pool": gin,
                                   "gettoni_venduti": gout, "rapporto": round(d2, 4),
                                   "tx_vende": z.get("tx_vende", [])[:2],
                                   "tx_compra": z.get("tx_compra", [])[:2]})
        if not trovata:
            senza_posizione += 1

    n = len(dopo)
    if not n:
        print("RICONCILIA | zero posizioni confrontabili: non scrivo un esito che direbbe "
              "«quadra tutto». Serve piu' copertura della curva.")
        return 0
    fin = lambda L: [x for x in L if x is not None]
    pa, pb = fin(prima), fin(dopo)
    print(f"\nRICONCILIA | {n:,} posizioni confrontabili", flush=True)
    print(f"   venduti/comprati SOLO col pool : mediana {statistics.median(pa):.2f}  "
          f"(impossibili, zero acquisti: {len(prima)-len(pa)})", flush=True)
    print(f"   venduti/comprati CON la curva  : mediana {statistics.median(pb):.2f}  "
          f"(impossibili: {len(dopo)-len(pb)})", flush=True)
    print(f"   quadrano entro il {int(BANDA*100)}%      : {quadrano:,} su {n:,} "
          f"({100*quadrano/n:.1f}%)", flush=True)
    print(f"   non confrontate: {senza_pool:,} senza pool noto, "
          f"{senza_posizione:,} senza una nostra posizione in quel pool", flush=True)
    print(f"   monete con piu' di un pool: {piu_pool:,} (confrontate con ognuno)", flush=True)

    json.dump({"acq": int(__import__("time").time()), "chain": CHAIN,
               "confrontabili": n,
               "mediana_solo_pool": statistics.median(pa),
               "mediana_con_curva": statistics.median(pb),
               "impossibili_solo_pool": len(prima) - len(pa),
               "impossibili_con_curva": len(dopo) - len(pb),
               "quadrano": quadrano, "banda": BANDA,
               "non_confrontate_senza_pool": senza_pool,
               "non_confrontate_senza_posizione": senza_posizione,
               "monete_con_piu_pool": piu_pool,
               "nota": ("misura in PEZZI, non in denaro: nessun prezzo usato, quindi immune "
                        "all'errore delle unita'"),
               "esempi_da_verificare_a_mano": esempi},
              open(FUORI, "w"), indent=1)
    print(f"RICONCILIA | scritto {FUORI} con {len(esempi)} esempi verificabili a mano",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
