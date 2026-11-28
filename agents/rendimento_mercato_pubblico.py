"""CHI GUADAGNA NEL MERCATO PUBBLICO — la strada dove la velocita' non e' il vantaggio.

== PERCHE' QUI E NON SULLA CURVA ==

Sulla curva il verdetto e' chiuso: il vantaggio esiste (181 operatori battono il caso) ma e' di
ESECUZIONE, non di analisi — il margine mediano per entrare dopo qualcuno e' **0,3 secondi** e il
31% degli acquisti consecutivi cade nello stesso blocco. Appena si chiede mezzo secondo di
margine, 1,09x diventa 0,96x.

Nel mercato pubblico la tenuta mediana e' **5,5 ore**. Li' la velocita' conta molto meno, quindi
e' l'unico posto dove un vantaggio puo' essere di testa invece che di macchina.

== LE REGOLE, TUTTE QUELLE CHE IERI HANNO UCCISO SEI RISULTATI SU SETTE ==

 1. **i gettoni devono tornare**: venduti fra il 90% e il 110% di quelli comprati. Senza, il
    rapporto fra due cifre di denaro non riguarda la stessa merce (il falso «157x» cadeva qui);
 2. **mai sommare valute diverse**: ogni contenitore nasce con la chiave dell'asset;
 3. **conto onesto**: chi e' entrato e non e' mai uscito vale −100%, non «non misurabile»
    (applicare questo ha ribaltato il «+20,6% per chi entra primo» in −14,6%);
 4. **vendere non e' travasare**: un gettone mandato a un altro portafoglio non e' un incasso;
 5. **il gas dentro**, misurato e non stimato;
 6. **la taglia e' un filtro, non un punteggio**: si guarda chi mette cifre come le nostre;
 7. **i lanciatori fuori**: chi crea la moneta sta dall'altra parte del banco.

E il criterio che vale piu' di tutti, dichiarato PRIMA di guardare i risultati: un metro vuoto
vale solo se i portafogli finti partono dalla stessa mediana dei veri (scarto < 0,03). Ieri ne ho
buttati sei su sette per questo.

== COSTO ==

ZERO: legge i file gia' prodotti.
"""
import collections
import glob
import gzip
import json
import math
import os
import random
import statistics
import sys
import time


# UNA SOLA LIBRERIA DI LETTURA (11/10, prescrizione di Astra). `curva_lanci` e `coppie` erano
# oggetti unici da 52 e 16,6 MB: per aggiungere un dato si riscriveva tutto, e ogni riscrittura
# entrava INTERA nella storia di git. Ora stanno a righe, e queste due funzioni nascondono quale
# forma c'e' sul disco: se cambia di nuovo, cambia in agents/archivio.py e non in dodici file.
def _lanci_interi():
    import archivio as _AR
    _t, _v = _AR.leggi("curva_lanci")
    _d = dict(_t)
    _d["da"] = _v
    return _d


def _coppie():
    import archivio as _AR
    return _AR.leggi("coppie", "coppie")[1]


CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
TENUTE = os.environ.get("TENUTE", f"{BASE}/tenute_pezzo_*.jsonl.gz")
SOMME = os.environ.get("SOMME", f"{BASE}/curva_somme_pezzo_*.json.gz")
FUORI = os.environ.get("FUORI", f"{BASE}/rendimento_mercato_pubblico.json")
TAGLIA = (float(os.environ.get("TAGLIA_MIN", "0.01")), float(os.environ.get("TAGLIA_MAX", "0.2")))
GAS = float(os.environ.get("GAS_GIRO", "0.000008135"))
MIN_OP = int(os.environ.get("MIN_OPERAZIONI", "20"))
GIRI = int(os.environ.get("GIRI", "10"))
SCARTO_MAX = 0.03
NAT = "0x" + "0" * 40


def main():
    pl = f"{BASE}/curva_lanci.json.gz"
    if not os.path.exists(pl):
        raise SystemExit(f"MERCATO | manca {pl}: senza l'elenco dei lanci non so la valuta "
                         f"di ogni curva ne' chi ha lanciato cosa")
    dl = json.load(gzip.open(pl, "rt"))
    cu2t, c2a, lanciatori = {}, {}, set()
    for t, v in dl["da"].items():
        cu = v["curva"].lower()
        cu2t[cu] = t.lower()
        c2a[cu] = (v.get("quote") or "").lower() or None
        c = (v.get("creatore") or "").lower()
        if c:
            lanciatori.add(c)

    # il lato MERCATO PUBBLICO: per (portafoglio, moneta), gettoni e denaro, solo gli scambi
    pub = {}
    righe = scartati_travaso = senza_prezzo = duplicati = 0
    versioni = collections.Counter()
    visti = set()
    prove_per_pos = {}
    VERSIONE_ATTESA = 8
    for p in sorted(glob.glob(TENUTE, recursive=True)):
        try:
            for ln in gzip.open(p, "rt"):
                if not ln.strip():
                    continue
                x = json.loads(ln)
                righe += 1
                # VERSIONE DI OGNI RIGA (7/10). Non si SCEGLIE cosa fare delle righe vecchie:
                # si rifiuta tutto. «Uso solo le nuove» sembra prudente e non lo e': se meta'
                # del file e' vecchia, il sottoinsieme nuovo e' una fetta storta della realta'.
                versioni[x.get("v", "senza versione")] += 1
                if x.get("v") != VERSIONE_ATTESA:
                    continue
                # UN SOLO CONTEGGIO PER (portafoglio, moneta). Le fette per posizione
                # scrivevano la stessa coppia due volte (30.016 misurate il 7/10) e sommarle
                # raddoppiava guadagni e capitali.
                kk = (x["chi"], x["moneta"])
                if kk in visti:
                    duplicati += 1
                    continue
                visti.add(kk)
                si = x.get("scambio_in", 0.0)
                so = x.get("scambio_out", 0.0)
                if si <= 0 and so <= 0:
                    scartati_travaso += 1
                    continue
                vi, vo = x.get("valuta_in", 0.0), x.get("valuta_out", 0.0)
                if vi <= 0 and vo <= 0:
                    senza_prezzo += 1
                    continue
                k = (x["chi"], x["moneta"])
                d = pub.setdefault(k, {"gin": 0.0, "gout": 0.0, "vin": 0.0, "vout": 0.0,
                                       "valuta": x.get("valuta")})
                d["gin"] += si
                d["gout"] += so
                d["vin"] += vi
                d["vout"] += vo
                if x.get("prove"):
                    prove_per_pos[k] = x["prove"]
        except Exception as e:
            print(f"   {os.path.basename(p)} illeggibile ({str(e)[:50]}): lo salto e lo dico")
    print(f"MERCATO | {righe:,} righe lette: {len(pub):,} posizioni nel mercato pubblico "
          f"({scartati_travaso:,} solo travaso, {senza_prezzo:,} senza prezzo)", flush=True)
    sole = {v for v, n in versioni.items() if n}
    if sole and sole != {VERSIONE_ATTESA}:
        print(f"MERCATO | RIFIUTO: righe di versioni diverse nello stesso insieme "
              f"{dict(versioni)}, attesa {VERSIONE_ATTESA}. Sommarle mescola due significati: "
              f"e' la causa del guadagno di 7.740 dollari dove la chain diceva 3,36. "
              f"Non misuro e non scrivo niente finche' i dati non sono rifatti.")
        return 0
    if duplicati:
        print(f"MERCATO | {duplicati:,} righe duplicate scartate (una sola per coppia)")
    if len(pub) < 200:
        print(f"MERCATO | solo {len(pub)} posizioni col prezzo: troppo poche per misurare. "
              f"Non scrivo un verdetto su niente — serve piu' copertura.")
        return 0

    # il lato CURVA: quanto aveva pagato per entrare
    curva = collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])   # vin, vout, gin, gout
    for p in sorted(glob.glob(SOMME, recursive=True)):
        try:
            d = json.load(gzip.open(p, "rt")).get("da", {})
        except Exception:
            continue
        for k, v in d.items():
            w, cu = k.split("|")
            t = cu2t.get(cu)
            if not t or c2a.get(cu) != NAT or v.get("grezzo"):
                continue
            a = curva[(w, t)]
            a[0] += v["compra_valuta"]; a[1] += v["vende_valuta"]
            a[2] += v["compra_gettoni"]; a[3] += v["vende_gettoni"]
        del d

    # il giro completo: paga sulla curva (o nel pool), esce nel pool
    W = collections.defaultdict(list)
    fuori_taglia = squilibrate = 0
    for (w, t), d in pub.items():
        if w in lanciatori:
            continue
        if (d.get("valuta") or "").lower() != NAT:
            continue                      # mai sommare valute diverse
        c = curva.get((w, t), [0.0, 0.0, 0.0, 0.0])
        dentro = c[0] + d["vin"] + GAS
        fuori_ = c[1] + d["vout"]
        gin = c[2] + d["gin"]
        gout = c[3] + d["gout"]
        if dentro <= 0 or gin <= 0:
            continue
        if not (TAGLIA[0] <= dentro <= TAGLIA[1]):
            fuori_taglia += 1
            continue
        # i gettoni devono tornare, altrimenti non e' un giro ma due fatti scollegati
        if fuori_ > 0 and not (0.9 <= gout / gin <= 1.1):
            squilibrate += 1
            continue
        W[w].append((dentro, fuori_))
    print(f"MERCATO | {sum(len(v) for v in W.values()):,} giri su {len(W):,} portafogli "
          f"({fuori_taglia:,} fuori taglia, {squilibrate:,} coi gettoni che non tornano)",
          flush=True)

    tutti = [x for v in W.values() for x in v]
    if len(tutti) < 100:
        print("MERCATO | meno di 100 giri: non pubblico un numero su cosi' poco.")
        return 0
    cap = sum(f for _, f in tutti) / sum(d for d, _ in tutti)
    chiusi = [f / d for d, f in tutti if f > 0]
    mai = sum(1 for _, f in tutti if f <= 0)
    print(f"\nMERCATO | ritorno sul capitale, CONTO ONESTO (chi non esce vale zero): {cap:.4f}x")
    print(f"   giri che non sono mai usciti: {mai:,} su {len(tutti):,} "
          f"({100*mai/len(tutti):.1f}%)")
    if chiusi:
        print(f"   fra chi e' uscito: mediana {statistics.median(chiusi):.3f}x, "
              f"sopra 2x {100*sum(1 for x in chiusi if x>=2)/len(chiusi):.1f}%, "
              f"sopra 10x {100*sum(1 for x in chiusi if x>=10)/len(chiusi):.1f}%")

    # il metro: esiste qualcuno sistematicamente migliore?
    grandi = {w: v for w, v in W.items() if len(v) >= MIN_OP}
    esito = None
    if len(grandi) >= 50:
        mazzo = [f / d for d, f in tutti if d > 0]
        rit = lambda L: sum(f for _, f in L) / sum(d for d, _ in L)
        def regge(L, mm):
            h = len(L) // 2
            g = lambda S, M: sum(a[0] * b for a, b in zip(S, M)) / sum(a[0] for a in S)
            return g(L[:h], mm[:h]) > 1 and g(L[h:], mm[h:]) > 1
        lista = list(grandi.values())
        oss = sum(1 for L in lista if regge(L, [f / d for d, f in L]))
        veri = [rit(L) for L in lista]
        esiti, med = [], []
        for s in range(GIRI):
            random.seed(500 + s)
            n, rr = 0, []
            for L in lista:
                mm = [random.choice(mazzo) for _ in L]
                rr.append(sum(a[0] * b for a, b in zip(L, mm)) / sum(a[0] for a in L))
                if regge(L, mm):
                    n += 1
            esiti.append(n); med.append(statistics.median(rr))
        mv, mf = statistics.median(veri), statistics.median(med)
        valido = abs(mv - mf) < SCARTO_MAX
        print(f"\nMERCATO | metro: mediana veri {mv:.3f}x, finti {mf:.3f}x, "
              f"scarto {abs(mv-mf):.3f} -> {'VALIDO' if valido else 'NON VALIDO'}")
        if valido:
            esiti.sort()
            esito = {"osservati": oss, "caso_min": esiti[0], "caso_max": esiti[-1],
                     "caso_mediana": statistics.median(esiti), "operatori": len(lista)}
            print(f"MERCATO | OSSERVATI {oss} su {len(lista):,}  |  caso: "
                  f"mediana {statistics.median(esiti):.0f}, massimo {esiti[-1]}")
        else:
            print("MERCATO | il metro non passa il criterio: il verdetto non si scrive. "
                  "Un metro che parte piu' in basso dichiara bravo chiunque.")

    # ====== IL CANCELLO: PRIMA LA PROVA, POI IL VERDETTO (7/10/2026) ======
    # Per tre giorni ho prodotto numeri, li ho comunicati, e li ho verificati dopo — quando li
    # contestava Nicolo'. Il 7/10 ha aperto un portafoglio su un sito: 11 euro, dove io avevo
    # detto 7.740 dollari. Sbagliato di 2.300 volte, e la verifica costava due minuti.
    # Quindi l'ordine si inverte, e non per buona volonta': se un campione a caso delle
    # posizioni che sto per riportare non combacia con la chain, QUESTO FILE NON SI SCRIVE.
    import prima_la_prova as PP
    quanti = int(os.environ.get("CAMPIONE_PROVA", "12"))
    cand = [k for k in pub if prove_per_pos.get(k)]
    if not cand:
        print("MERCATO | nessuna riga porta la propria prova: non posso verificare niente, "
              "quindi non scrivo un verdetto. (Le prove le aggiunge chi_tiene_i_graduati v8.)")
        return 0
    # IL CAMPIONE DEVE CONTENERE GLI ESTREMI (7/10 sera). Un campione CASUALE ha passato
    # 19 casi su 19 e il verdetto e' uscito; poi ho guardato i primi otto per moltiplicatore e
    # SETTE erano falsi — uno dichiarava 9,95 incassati dove la chain dice 9,95e-12, mille
    # miliardi di differenza. Gli artefatti non stanno in mezzo alla distribuzione: stanno in
    # CIMA, perche' ordinare per rapporto li seleziona per costruzione. Un controllo che guarda
    # a caso e' un controllo che guarda dove gli artefatti non sono.
    # Quindi: prima i piu' alti, poi qualcuno a caso.
    random.seed(99)
    def _x(k):
        d = pub[k]
        return (d["vout"] / d["vin"]) if d["vin"] > 0 else 0.0
    alti = sorted(cand, key=lambda k: -_x(k))[:max(6, quanti // 2)]
    resto = [k for k in cand if k not in set(alti)]
    scelte = alti + random.sample(resto, min(max(0, quanti - len(alti)), len(resto)))
    print(f"MERCATO | provo {len(alti)} casi in CIMA per moltiplicatore + "
          f"{len(scelte)-len(alti)} a caso", flush=True)
    # I DECIMALI DELL'ASSET, PER OGNI CASO (7/10 sera). La prova non puo' indovinare la scala:
    # con 18 di default ha bocciato un dato GIUSTO pagato in un asset a 6 decimali (121,70698
    # letto come 0,0498) e ha fermato la misura per colpa del controllo, non del dato.
    # I decimali si prendono dalla riga stessa quando ci sono (versione 9+), altrimenti
    # dall'elenco degli asset, altrimenti dal contratto. Se non si sanno, il caso si dichiara
    # illeggibile: non si tira a indovinare e non si accusa.
    dec_di = {}
    try:
        _as = _lanci_interi().get("assets", {})
        for _a, _v in _as.items():
            if _v.get("decimali") is not None:
                dec_di[_a.lower()] = int(_v["decimali"])
    except Exception as e:
        print(f"MERCATO | elenco asset non letto ({str(e)[:40]}): chiedero' al contratto")

    def _dec(asset):
        a = (asset or "").lower()
        if a in dec_di:
            return dec_di[a]
        try:
            import curva_pons as CP
            r = CP.chiama("eth_call", [{"to": a, "data": "0x313ce567"}, "latest"])
            dec_di[a] = int(r, 16) if r else None
        except Exception:
            dec_di[a] = None
        return dec_di[a]

    casi = []
    for k in scelte:
        for pr in prove_per_pos[k][:2]:
            h, imp = pr[0], pr[1]
            d = pr[3] if len(pr) > 3 else _dec(pub[k].get("valuta"))
            casi.append({"tx": h, "valuta_attesa": imp, "decimali": d})
    passa, ref = PP.prova(casi)
    PP.stampa(passa, ref)
    if not passa:
        json.dump({"acq": int(time.time()), "chain": CHAIN, "esito": "PROVA FALLITA",
                   "casi": ref, "perche": ("i miei importi non combaciano con la chain: il "
                   "verdetto non si scrive. Si scrive il referto della prova, perche' un "
                   "fallimento che non lascia traccia si ripete.")},
                  open(FUORI.replace(".json", "_prova_fallita.json"), "w"), indent=1)
        return 0

    json.dump({"acq": int(time.time()), "chain": CHAIN, "taglia": TAGLIA, "gas": GAS,
               "prova_sulla_chain": {"casi": len(casi), "tutti_combaciano": True},
               "posizioni_col_prezzo": len(pub), "giri": len(tutti),
               "portafogli": len(W),
               "ritorno_capitale_onesto": cap,
               "mai_usciti": mai,
               "mediana_fra_chi_esce": statistics.median(chiusi) if chiusi else None,
               "metro": esito,
               "nota": ("conto onesto: chi non esce vale zero. Gettoni che tornano, una sola "
                        "valuta, gas incluso, lanciatori esclusi, taglia come filtro.")},
              open(FUORI, "w"), indent=1)
    print(f"MERCATO | scritto {FUORI}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
