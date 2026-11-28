"""CHI ENTRA ALL'INIZIO FA TANTE X? Il giro completo, in una sola valuta.

== LA DOMANDA (Nicolo', 6/10/2026) ==

«Dobbiamo capire se c'e' gente che entra all'inizio all'inizio e fa tante X. Riusciamo a vedere
con quanti soldi investono all'inizio e con quanti se ne portano a casa.»

== PERCHE' SI PUO' FARE SENZA PREZZI ==

Il giro e' questo:

    paga sulla CURVA  ->  (la moneta gradua, nasce il pool)  ->  vende nel POOL

La curva si paga in un asset, e il pool paga nello stesso asset quando e' lo stesso. Allora il
multiplo e' un **rapporto fra quantita' della stessa cosa**: nessun prezzo, nessuna conversione,
nessun modo di sbagliare le unita'. Il 3/10 un prezzo sbagliato ha prodotto 16 milioni di dollari
inesistenti, e il 6/10 ho quasi scritto una somma di importi in 72 valute diverse: qui quel
rischio non esiste per costruzione.

**Se i due asset sono diversi, la posizione si SCARTA e si conta.** Non si converte. Una
posizione scartata e dichiarata e' onesta; una convertita con un prezzo inventato e' una bugia.

== CHE COSA NON PUO' DIRE ==

 · solo robinhood (su base il meccanismo di lancio e' un altro, va misurato a parte);
 · solo i portafogli nella nostra lista di candidati, perche' solo per loro conosciamo le
   posizioni nel pool. Quindi questa NON e' la popolazione intera: e' il campione che sappiamo
   seguire su entrambi i mercati. Va detto ogni volta.
 · il costo del gas non c'e'. Su posizioni da pochi centesimi puo' essere decisivo: la riga
   «quanto si paga di gas» e' la prima cosa da aggiungere se un multiplo risulta appena sopra 1.
"""
import collections
import glob
import gzip
import json
import os
import statistics
import sys
import time

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
SOMME = os.environ.get("SOMME", f"{BASE}/curva_somme_pezzo_*.json.gz")
FILE = os.environ.get("FILA", f"{BASE}/curva_fila_pezzo_*.json.gz")
DETTAGLI = os.environ.get("DETTAGLI", f"{BASE}/dettaglio_candidati_pezzo_*.json")
FUORI = os.environ.get("FUORI", f"{BASE}/x_chi_entra_prima.json")
POSIZIONI = [1, 2, 3, 5, 10, 20, 50]
# IL CONTO ONESTO. Una posizione comprata e MAI venduta vale zero, non «non misurabile»: e' la
# lezione del fondale onesto (5/10). Il 6/10, applicata qui, ha ribaltato il segno della risposta:
# il +20,6% del primo arrivato e' diventato -14,6%, perche' il 39,5% dei primi arrivati non vende
# mai. Senza questa riga l'agente darebbe il numero piu' convincente e piu' sbagliato.
GIORNI_PER_PERDUTA = float(os.environ.get("GIORNI_PER_PERDUTA", "3"))
SEC_PER_BLOCCO = 0.101          # misurato su tutte le epoche della chain: 0,1003-0,1012
# IL GAS, MISURATO il 6/10 su 50 transazioni vere (non assunto): acquisto 0,0000038 e vendita
# 0,0000043 in valuta nativa, mediani. Su una scommessa da 0,05 e' lo 0,02% e non conta; su una
# da 0,00005 e' il 15% e decide il segno. Per questo si sottrae sempre, invece di dire «e'
# piccolo»: «piccolo» dipende dalla scommessa, non dal gas.
GAS_GIRO = float(os.environ.get("GAS_GIRO", "0.000008135"))


def _quantili(L):
    L = sorted(L)
    q = lambda p: L[int(p * (len(L) - 1))]
    return {"mediana": q(0.5), "q25": q(0.25), "q75": q(0.75), "q90": q(0.9), "max": L[-1]}


def main():
    pl = f"{BASE}/curva_lanci.json.gz"
    pc = f"{BASE}/coppie.json"
    for p in (pl, pc):
        if not os.path.exists(p):
            raise SystemExit(f"X | manca {p}: non invento la corrispondenza fra curva e pool")
    dl = json.load(gzip.open(pl, "rt"))
    assets = dl.get("assets", {})
    curva2tok, curva2asset = {}, {}
    for t, v in dl["da"].items():
        cu = v["curva"].lower()
        curva2tok[cu] = t.lower()
        curva2asset[cu] = (v.get("quote") or "").lower() or None

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
    somme = {}
    for p in sorted(glob.glob(SOMME, recursive=True)):
        try:
            somme.update(json.load(gzip.open(p, "rt")).get("da", {}))
        except Exception as e:
            print(f"   {os.path.basename(p)} illeggibile ({str(e)[:50]}): lo salto e lo dico")
    fila = {}
    for p in sorted(glob.glob(FILE, recursive=True)):
        try:
            fila.update(json.load(gzip.open(p, "rt")).get("da", {}))
        except Exception as e:
            print(f"   {os.path.basename(p)} illeggibile ({str(e)[:50]}): lo salto e lo dico")
    bn = 0
    try:
        from curva_pons import chiama as _ch
        bn = int(_ch("eth_blockNumber"), 16)
    except Exception:
        pass
    taglio_blocco = (bn - int(GIORNI_PER_PERDUTA * 86400 / SEC_PER_BLOCCO)) if bn else 0
    if not bn:
        print("X | non so il blocco attuale: considero PERDUTA ogni posizione senza uscita. "
              "E' la scelta prudente: il contrario gonfierebbe il risultato.", flush=True)
    print(f"X | {len(curva2tok):,} curve, {len(fila):,} con la fila, {len(somme):,} somme, "
          f"{len(pos):,} portafogli con posizioni nel pool", flush=True)
    if not fila or not pos:
        print("X | senza la fila o senza le posizioni non misuro niente, e non scrivo un file "
              "che direbbe «nessuno guadagna».")
        return 0

    per_pos = collections.defaultdict(list)
    capitale = collections.defaultdict(lambda: [0.0, 0.0])
    # chiave (posizione, ASSET): vedi la nota dentro il ciclo
    perdute = collections.defaultdict(lambda: [0.0, 0])
    ancora_aperte = 0
    esempi, scartati_valuta, senza_uscita, tot, grezzi = [], 0, 0, 0, 0
    for cu, L in fila.items():
        a_cur = curva2asset.get(cu)
        tok = curva2tok.get(cu)
        if not tok or not a_cur:
            continue
        for i, r in enumerate(L, 1):
            w = r[2]
            sm = somme.get(w + "|" + cu)
            if not sm or sm["compra_valuta"] <= 0:
                continue
            # SI RIFIUTA DI SOMMARE UN IMPORTO GREZZO CON UNO CONVERTITO. Il 6/10 mescolarli ha
            # prodotto multipli da 5 miliardi di miliardi: il lato curva era grezzo (asset
            # ignoto) e il lato pool diviso per i decimali. Un rapporto fra i due non e' un
            # numero grande: e' un numero che non esiste.
            if sm.get("grezzo"):
                grezzi += 1
                continue
            dentro = sm["compra_valuta"]
            fuori_ = sm["vende_valuta"]            # eventuale uscita sulla CURVA
            uscita_pool = 0.0
            trovato = False
            for pool in tok2pool.get(tok, []):
                z = pos.get(w, {}).get(pool)
                if not z:
                    continue
                # LA VALUTA DEVE ESSERE LA STESSA, altrimenti si scarta e si conta
                if (z.get("valuta") or "").lower() != a_cur:
                    scartati_valuta += 1
                    continue
                dentro += z.get("vin", 0.0)
                uscita_pool += z.get("vout", 0.0)
                trovato = True
            if not trovato and fuori_ <= 0:
                # NESSUNA USCITA. Non si salta: vale ZERO. Si salta solo se e' troppo recente
                # per aver avuto il tempo di uscire — altrimenti conterei come perdita una
                # posizione ancora viva.
                ultimo = sm.get("ultimo") or 0
                if ultimo >= taglio_blocco:
                    ancora_aperte += 1
                    continue
                # LA CHIAVE DELL'ASSET ANCHE QUI. Scritta senza, questa riga sommava le
                # perdite di TUTTI gli asset (489 milioni di USDG compresi) e le divideva per
                # i guadagni del solo nativo: il conto onesto usciva 0,0013x invece di 0,854x.
                # QUARTA volta in un giorno che sbaglio sommando unita' diverse — e stavolta
                # dentro la correzione di quell'errore stesso.
                # La regola che ne deriva: **ogni contenitore di denaro nasce con la chiave
                # dell'asset.** Non gliela si aggiunge dopo, perche' dopo si dimentica.
                perdute[(i, a_cur)][0] += dentro + GAS_GIRO
                perdute[(i, a_cur)][1] += 1
                senza_uscita += 1
                continue
            # il gas si somma al COSTO: e' denaro uscito dal portafoglio come il resto
            dentro += GAS_GIRO
            m = (fuori_ + uscita_pool) / dentro
            tot += 1
            per_pos[i].append(m)
            # IL RITORNO SUL CAPITALE, non la mediana (lezione di Astra, 5/10). Con una coda
            # grassa la mediana e il guadagno vanno in direzioni opposte: qui la mediana e'
            # 0,94 (si perde) ma il massimo e' 84x. La domanda vera non e' «quanto fa il caso
            # tipico», e' «se scommetto la stessa cifra su ognuno, quanto torna in tutto».
            # Si tengono MESSO e TORNATO separati, e si dividono alla fine: sommare rapporti
            # darebbe peso uguale a una scommessa da 1 e a una da 1.000.
            # IL CAPITALE SI SOMMA PER ASSET, MAI FRA ASSET (6/10, terzo caso oggi).
            # I singoli rapporti sono validi perche' numeratore e denominatore sono lo stesso
            # asset. Ma SOMMARLI fra curve quotate in asset diversi (nativo, USDG, «Index»,
            # «SHROOM»…) da' un totale che non e' denaro: e' la stessa famiglia dell'errore che
            # ha prodotto 16 milioni di dollari inesistenti.
            # Quindi la chiave e' (posizione, asset), e si pubblica un ritorno sul capitale
            # solo DENTRO un asset — di norma quello nativo, che e' l'87% dei lanci.
            capitale[(i, a_cur)][0] += dentro
            capitale[(i, a_cur)][1] += fuori_ + uscita_pool
            if m >= 5 and len(esempi) < 15:
                z = None
                for pool in tok2pool.get(tok, []):
                    z = pos.get(w, {}).get(pool) or z
                esempi.append({"posizione_in_fila": i, "portafoglio": w, "moneta": tok,
                               "curva": cu, "valuta": assets.get(a_cur, {}).get("simbolo"),
                               "messo": round(dentro, 10), "portato_a_casa": round(fuori_ + uscita_pool, 10),
                               "multiplo": round(m, 2),
                               "tx_acquisto_curva": sm.get("tx_compra", [])[:2],
                               "tx_vendita_pool": (z or {}).get("tx_vende", [])[:2]})

    print(f"\nX | {tot:,} giri completi misurati  "
          f"({scartati_valuta:,} scartati per valuta diversa, {grezzi:,} per importo "
          f"grezzo, {senza_uscita:,} senza uscita)",
          flush=True)
    print(f"{'pos':>4s} {'casi':>7s} {'mediana':>9s} {'75%':>9s} {'90%':>9s} "
          f"{'>=2x':>6s} {'>=10x':>6s} {'massimo':>12s}")
    tabella = {}
    for i in POSIZIONI:
        L = per_pos.get(i, [])
        if len(L) < 10:
            print(f"{i:>4d} {len(L):>7,}   (meno di 10 casi: non pubblico una mediana su niente)")
            continue
        q = _quantili(L)
        s2 = 100 * sum(1 for x in L if x >= 2) / len(L)
        s10 = 100 * sum(1 for x in L if x >= 10) / len(L)
        NATIVO = "0x" + "0" * 40
        cap = capitale[(i, NATIVO)]
        rit = (cap[1] / cap[0]) if cap[0] > 0 else None
        pe = perdute[(i, NATIVO)]
        onesto = (cap[1] / (cap[0] + pe[0])) if (cap[0] + pe[0]) > 0 else None
        quota_perse = 100 * pe[1] / (len(L) + pe[1]) if (len(L) + pe[1]) else 0
        tabella[i] = {"casi": len(L), **q, "pct_2x": s2, "pct_10x": s10,
                      "messo_nativo": cap[0], "tornato_nativo": cap[1],
                      "ritorno_capitale_nativo_solo_chi_vende": rit,
                      "ritorno_capitale_nativo_ONESTO": onesto,
                      "perdute_capitale": pe[0], "perdute_quante": pe[1],
                      "pct_mai_venduto": quota_perse,
                      "nota_capitale": "solo asset nativo: sommare asset diversi non da' denaro"}
        print(f"{i:>4d} {len(L):>7,} {q['mediana']:>8.3f}x {q['q75']:>8.3f}x {q['q90']:>8.3f}x "
              f"{s2:>5.1f}% {s10:>5.1f}% {q['max']:>11,.1f}x"
              # il condizionale NON va sulla stringa intera: scritto cosi' per sbaglio, con
              # `rit` assente faceva stampare "" — cioe' la riga SPARIVA invece di mostrarsi
              # senza quel campo. Una riga che scompare e' un dato che non esiste.
              f"  solo-chi-vende {('%.4f' % rit) if rit is not None else '?'}x"
              f"  mai-venduto {quota_perse:4.1f}%"
              f"  ONESTO {('%.4f' % onesto) if onesto is not None else '?'}x")

    per_asset = collections.defaultdict(lambda: [0.0, 0.0])
    for (i, a), c in capitale.items():
        per_asset[a][0] += c[0]
        per_asset[a][1] += c[1]
    print("\nX | ritorno sul capitale DENTRO ogni asset (i primi 5 per capitale messo):")
    for a, c in sorted(per_asset.items(), key=lambda z: -z[1][0])[:5]:
        sim = assets.get(a, {}).get("simbolo") or a[:10]
        print(f"   {sim:10s} messo {c[0]:>16,.2f}  tornato {c[1]:>16,.2f}  "
              f"= {c[1]/c[0]:.4f}x" if c[0] > 0 else f"   {sim}: niente")

    # i primi 3 contro il resto: la domanda e' se l'ORDINE conta
    primi = [x for i in (1, 2, 3) for x in per_pos.get(i, [])]
    dopo = [x for i, L in per_pos.items() if i >= 10 for x in L]
    confronto = None
    if len(primi) >= 20 and len(dopo) >= 20:
        confronto = {"primi3_mediana": statistics.median(primi), "primi3_casi": len(primi),
                     "dal10_mediana": statistics.median(dopo), "dal10_casi": len(dopo),
                     "primi3_pct10x": 100 * sum(1 for x in primi if x >= 10) / len(primi),
                     "dal10_pct10x": 100 * sum(1 for x in dopo if x >= 10) / len(dopo)}
        print(f"\nX | i primi 3 arrivati: mediana {confronto['primi3_mediana']:.3f}x, "
              f"{confronto['primi3_pct10x']:.1f}% sopra 10x  ({len(primi):,} casi)")
        print(f"X | dal 10° in poi    : mediana {confronto['dal10_mediana']:.3f}x, "
              f"{confronto['dal10_pct10x']:.1f}% sopra 10x  ({len(dopo):,} casi)")

    json.dump({"acq": int(time.time()), "chain": CHAIN, "giri": tot,
               "scartati_valuta_diversa": scartati_valuta, "scartati_grezzi": grezzi,
               "senza_uscita_contate_come_perdita": senza_uscita,
               "ancora_aperte_escluse": ancora_aperte,
               "giorni_per_considerarla_perduta": GIORNI_PER_PERDUTA,
               "gas_per_giro": GAS_GIRO,
               "per_posizione": tabella, "primi_contro_dopo": confronto,
               "nota": ("rapporto fra quantita' della STESSA valuta: nessun prezzo usato. "
                        "Solo i portafogli in lista candidati, quindi non la popolazione "
                        "intera. Il gas non e' incluso."),
               "esempi_sopra_5x": esempi},
              open(FUORI, "w"), indent=1)
    print(f"X | scritto {FUORI} con {len(esempi)} esempi sopra 5x", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
