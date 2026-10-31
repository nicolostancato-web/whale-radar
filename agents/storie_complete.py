"""LA STORIA COMPLETA DI OGNI PORTAFOGLIO — tentativi compresi, non solo le vincite.

== PERCHE' ESISTE (6/10/2026, correzione chiesta da ENTRAMBI i revisori) ==

Astra: «Un portafoglio puo' aver comprato dieci vincitori perche' ha comprato diecimila monete.»
Grok : «Il conteggio dei successi senza il numero di tentativi e' la classifica dei bot.»

Hanno ragione e il difetto e' grosso: ordinare i portafogli per «quante volte ha fatto molte X»
mette in cima chi ha fatto piu' TENTATIVI, non chi e' piu' bravo. Con 675.145 monete e ~146.000
portafogli, qualche ripetizione fortunata e' garantita.

Quindi qui si misura, per ogni portafoglio:
 · quanti tentativi ha fatto (quante curve diverse ha comprato);
 · quanto capitale ha messo IN TUTTO e quanto ne ha ripreso IN TUTTO;
 · quanti successi (un successo = quella posizione ha reso almeno SOGLIA volte);
 · e soprattutto **l'ECCESSO rispetto a chi ha fatto lo stesso numero di tentativi**.

L'eccesso e' il numero che conta. Un bot con 1.500 tentativi e 80 successi e' SOTTO la media di
chi ne ha 1.500. Un portafoglio con 20 tentativi e 6 successi e' fuori dal caso. Una classifica
per conteggio mette in cima il primo e butta il secondo.

== CHI SI TOGLIE PRIMA DI CONTARE ==

 · **i lanciatori**: chi crea la moneta non e' un compratore bravo, e' dall'altra parte del banco;
 · gli **esentati dalla tassa** dei primi 5 secondi: e' privilegio, non abilita'. Sono fino a 32
   indirizzi scritti nella transazione di creazione — NON li ho ancora, e finche' non ce li ho
   questo file lo DICHIARA invece di fingere che non esistano.

== LA SOGLIA SI DECIDE PRIMA ==

Grok: «Non potete scegliere la definizione dopo aver visto chi sembra bravo.» Quindi SOGLIA e'
un parametro dichiarato, non scelto guardando i risultati, e si riportano piu' soglie insieme
cosi' non si puo' barare scegliendo quella comoda.

== COSTO ==

ZERO: legge i file gia' prodotti.
"""
import collections
import glob
import gzip
import json
import math
import os
import statistics
import sys
import time

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
SOMME = os.environ.get("SOMME", f"{BASE}/curva_somme_pezzo_*.json.gz")
FUORI = os.environ.get("FUORI", f"{BASE}/storie_complete.json")
SOGLIE = [float(x) for x in os.environ.get("SOGLIE", "2,5,10").split(",")]
# LA TAGLIA E' UN FILTRO, NON UN PUNTEGGIO (direttiva di Nicolo', 6/10/2026 sera).
#
# «Quello che entra con 100.000 ed esce con 105.000 non e' bravo quanto quello che entra con 50
# e se ne esce con 600.»
#
# Ha ragione, e la ragione e' meccanica: piu' grande entri, meno multiplo puoi fare, perche' sei
# TU che muovi il prezzo. La balena che fa +5% non e' meno brava: fa un mestiere che a noi non
# serve. Quindi la taglia non va messa nel punteggio (confronterebbe mele e pere) ma nel
# RECINTO: si guarda solo chi entra con cifre come le nostre, e fra quelli si cerca chi
# moltiplica di piu' e lo rifa'.
#
# E c'e' un rovescio da ricordare: la taglia piccola e' anche dove vivono quasi tutti gli
# artefatti. Su 50 euro un multiplo enorme si crea con niente. Percio' il controllo di coerenza
# dei gettoni sta PRIMA di questo filtro, non dopo.
TAGLIA_MIN = float(os.environ.get("TAGLIA_MIN", "0"))
TAGLIA_MAX = float(os.environ.get("TAGLIA_MAX", "0"))   # 0 = nessun tetto
NATIVO = "0x" + "0" * 40


def main():
    pl = f"{BASE}/curva_lanci.json.gz"
    if not os.path.exists(pl):
        raise SystemExit(f"STORIE | manca {pl}: senza l'elenco dei lanci non so chi ha lanciato "
                         f"cosa, e il lanciatore NON va contato come compratore bravo")
    dl = json.load(gzip.open(pl, "rt"))
    curva_asset, lanciatori = {}, set()
    for t, v in dl["da"].items():
        cu = v["curva"].lower()
        curva_asset[cu] = (v.get("quote") or "").lower() or None
        c = (v.get("creatore") or "").lower()
        if c:
            lanciatori.add(c)
    print(f"STORIE | {len(curva_asset):,} curve, {len(lanciatori):,} indirizzi che hanno "
          f"lanciato almeno una moneta (esclusi dal conteggio)", flush=True)

    # per portafoglio: tentativi, capitale, successi per ogni soglia
    W = collections.defaultdict(lambda: {"n": 0, "dentro": 0.0, "fuori": 0.0,
                                         "succ": [0] * len(SOGLIE), "chiuse": 0, "aperte": 0})
    letti = saltati_asset = saltati_grezzi = 0
    squilibrate = [0]
    fuori_taglia = [0]
    for p in sorted(glob.glob(SOMME, recursive=True)):
        try:
            d = json.load(gzip.open(p, "rt")).get("da", {})
        except Exception as e:
            print(f"   {os.path.basename(p)} illeggibile ({str(e)[:50]}): lo salto e lo dico")
            continue
        for k, v in d.items():
            w, cu = k.split("|")
            if curva_asset.get(cu) != NATIVO:     # mai mescolare asset diversi
                saltati_asset += 1
                continue
            if v.get("grezzo"):
                saltati_grezzi += 1
                continue
            if v["compra_valuta"] <= 0:
                continue
            # I GETTONI DEVONO TORNARE. Senza questo controllo il rapporto fra due cifre di
            # DENARO non si riferisce alla stessa merce: un portafoglio che riceve gettoni
            # altrove e li scarica sulla curva mostra un multiplo enorme che non e' uno scambio.
            #
            # Misurato il 6/10, ed e' la correzione piu' importante della giornata: in generale
            # il 90,4% delle posizioni chiuse ha i gettoni bilanciati, ma i primi dieci della
            # classifica per eccesso stavano a 0/20, 3/38, 0/36, 0/7, 0/3. **La classifica
            # selezionava esattamente gli artefatti.** Il «portafoglio che fa 157x» non era
            # bravo: vendeva cento volte i gettoni che aveva comprato.
            #
            # Avevo costruito questo stesso controllo la mattina per il lato pool e non l'avevo
            # portato qui: una lezione applicata a un posto solo vale una volta.
            if v["n_vende"] > 0:
                if v["compra_gettoni"] <= 0:
                    squilibrate[0] += 1
                    continue
                r = v["vende_gettoni"] / v["compra_gettoni"]
                if not (0.9 <= r <= 1.1):
                    squilibrate[0] += 1
                    continue
            if TAGLIA_MIN and v["compra_valuta"] < TAGLIA_MIN:
                fuori_taglia[0] += 1
                continue
            if TAGLIA_MAX and v["compra_valuta"] > TAGLIA_MAX:
                fuori_taglia[0] += 1
                continue
            letti += 1
            x = W[w]
            x["n"] += 1
            x["dentro"] += v["compra_valuta"]
            x["fuori"] += v["vende_valuta"]
            if v["n_vende"] > 0:
                x["chiuse"] += 1
                m = v["vende_valuta"] / v["compra_valuta"]
                for j, s in enumerate(SOGLIE):
                    if m >= s:
                        x["succ"][j] += 1
            else:
                x["aperte"] += 1
        del d
    print(f"STORIE | {letti:,} posizioni usate, {len(W):,} portafogli  "
          f"({saltati_asset:,} saltate per asset diverso dal nativo, "
          f"{saltati_grezzi:,} per importo grezzo, "
          f"{squilibrate[0]:,} perche' i gettoni venduti non sono quelli comprati, "
          f"{fuori_taglia[0]:,} fuori dalla taglia {TAGLIA_MIN:g}-{TAGLIA_MAX:g})", flush=True)
    if not W:
        print("STORIE | nessun portafoglio: non scrivo un file che direbbe «nessuno compra».")
        return 0

    # tolgo i lanciatori: sono dall'altra parte del banco
    tolti = [w for w in W if w in lanciatori]
    for w in tolti:
        del W[w]
    print(f"STORIE | tolti {len(tolti):,} portafogli che hanno anche lanciato monete", flush=True)

    # L'ECCESSO: quanto fa in piu' rispetto a CHI HA LO STESSO NUMERO DI TENTATIVI.
    # I tentativi si raggruppano a scaglioni logaritmici: confrontare chi ne ha 20 con chi ne ha
    # 21 e' rumore, con chi ne ha 2.000 e' un confronto fra cose diverse.
    def scaglione(n):
        return int(math.log10(max(1, n)) * 3)       # ~3 scaglioni per decade

    gruppi = collections.defaultdict(list)
    for w, x in W.items():
        gruppi[scaglione(x["n"])].append(w)
    atteso = {}
    for g, lista in gruppi.items():
        for j, s in enumerate(SOGLIE):
            tassi = [W[w]["succ"][j] / W[w]["n"] for w in lista]
            atteso[(g, j)] = statistics.mean(tassi) if tassi else 0.0

    righe = []
    for w, x in W.items():
        g = scaglione(x["n"])
        ecc = []
        for j, s in enumerate(SOGLIE):
            att = atteso[(g, j)] * x["n"]
            # eccesso in deviazioni, col modello piu' gentile possibile (binomiale)
            p = atteso[(g, j)]
            sd = math.sqrt(max(1e-9, x["n"] * p * (1 - p)))
            ecc.append((x["succ"][j] - att) / sd if sd > 0 else 0.0)
        righe.append({"portafoglio": w, "tentativi": x["n"],
                      "capitale_messo": x["dentro"], "capitale_tornato": x["fuori"],
                      "ritorno": x["fuori"] / x["dentro"] if x["dentro"] > 0 else None,
                      "chiuse": x["chiuse"], "mai_vendute": x["aperte"],
                      "successi": x["succ"], "eccesso_in_sigma": [round(e, 2) for e in ecc],
                      "scaglione_tentativi": g})

    print(f"\nSTORIE | distribuzione dei tentativi:")
    nn = sorted(x["tentativi"] for x in righe)
    for q, n in ((0.5, "mediana"), (0.9, "90%"), (0.99, "99%"), (1.0, "massimo")):
        print(f"   {n:8s}: {nn[min(len(nn)-1, int(q*(len(nn)-1)))]:,} tentativi")

    for j, s in enumerate(SOGLIE):
        print(f"\nSTORIE | soglia {s:g}x — i 5 col maggiore ECCESSO (non col maggior conteggio):")
        top = sorted(righe, key=lambda r: -r["eccesso_in_sigma"][j])[:5]
        for r in top:
            print(f"   {r['portafoglio'][:16]}…  tentativi {r['tentativi']:5,}  "
                  f"successi {r['successi'][j]:4,}  eccesso {r['eccesso_in_sigma'][j]:+6.2f} sigma  "
                  f"ritorno {r['ritorno']:.3f}x" if r["ritorno"] else "")
        print(f"   per confronto, i 5 col maggior CONTEGGIO:")
        for r in sorted(righe, key=lambda r: -r["successi"][j])[:5]:
            print(f"   {r['portafoglio'][:16]}…  tentativi {r['tentativi']:5,}  "
                  f"successi {r['successi'][j]:4,}  eccesso {r['eccesso_in_sigma'][j]:+6.2f} sigma  "
                  f"ritorno {r['ritorno']:.3f}x" if r["ritorno"] else "")

    righe.sort(key=lambda r: -max(r["eccesso_in_sigma"]))
    json.dump({"acq": int(time.time()), "chain": CHAIN, "soglie": SOGLIE,
               "portafogli": len(righe), "lanciatori_tolti": len(tolti),
               "MANCA": ("gli indirizzi esentati dalla tassa dei primi 5 secondi (fino a 32 per "
                         "lancio, nella transazione di creazione) NON sono ancora esclusi: "
                         "sono privilegio, non abilita'"),
               "nota": ("l'eccesso e' rispetto ai portafogli con lo STESSO numero di tentativi. "
                        "Il conteggio nudo e' la classifica di chi ha provato di piu'."),
               "primi_200": righe[:200]}, open(FUORI, "w"), indent=1)
    print(f"\nSTORIE | scritto {FUORI}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
