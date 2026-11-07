# -*- coding: utf-8 -*-
"""I TETTI, MISURATI invece che scritti a mano.

Perche' esiste (4/11 mattina). Con l'aggregatore bloccato ci costruiamo le
vendite su Uniswap, e il controllo sulla resa ha rifiutato 50 ordini perche'
"la rotta migliore rende solo il 71%". Ma quel 71% e' la resa A QUELLA
TAGLIA: la stessa rotta a un quarto della taglia puo' rendere il 99%.

E la leva ce l'abbiamo gia': il tetto per coppia decide quanto debito si
chiude, quindi quanta garanzia si incassa e si vende. Prendere il 30% di
una posizione a buon prezzo batte prendere il 100% a un prezzo che annulla
la liquidazione -- il premio scala con la taglia, l'annullamento no.

Quello che cambia qui e' COME si trova il tetto: prima erano numeri
misurati a mano una volta e invecchiati (71 ore, il 3/11), ora si cercano
per dimezzamenti con il Quoter, che e' una lettura e costa zero.
"""
import json, os, sys, time
sys.path.insert(0, "agents")
import vendita_uniswap as VU
from pescatore import CONTRATTO as CONTR
D = "data/liquidazioni"
FUORI = f"{D}/tetti_coppia.json"
RESA_MINIMA = VU.RESA_MINIMA
# IL PAVIMENTO DELLA GRIGLIA DECIDEVA IL VERDETTO (riparato il 5/11).
# La griglia si fermava a 25.000 $: tutte le coppie che si vendono solo PIU'
# IN PICCOLO venivano marchiate "senza strada", e quel no parlava della
# nostra griglia, non del mercato. Misurato stasera: USDC->GHO passa a
# 5.000 $ e si rompe fra 5.000 e 10.000 -- cioe' le posizioni con debito
# GHO ($45.000 di premio, due terzi di tutto il "senza strada") non erano
# invendibili: erano solo piu' piccole del nostro gradino piu' basso.
# E una liquidazione PARZIALE va benissimo: 5.000 $ coperti al 4,5% di
# premio fanno ~225 $, che e' esattamente la fascia 150-600 $ dove abbiamo
# misurato che un nuovo arrivato puo' vincere.
TAGLIE = (2_000_000, 1_000_000, 500_000, 250_000, 100_000, 50_000, 25_000,
          10_000, 5_000, 2_000, 1_000)
def resa_curve(src, dst, dollari, PR, cache_c, cache_u):
    """La resa della strada CURVE, a una taglia. Aggiunta il 4/11: la
    ricerca per dimezzamenti guardava solo Uniswap, quindi dichiarava
    "nessuna taglia buona" per le monete che su Uniswap non hanno
    compratore -- sUSDe, osETH, rsETH -- quando la strada c'era su Curve.
    Un tetto misurato su una piazza sola e' un tetto misurato a meta'."""
    import vendita_curve as VC
    ps, pd = PR.get(src), PR.get(dst)
    if not ps or not pd: return None
    q = int(dollari/ps["prezzo_usd"]*10**ps["decimali"])
    # prima la strada diretta verso il debito
    v, d, pos, app, uscita, out = VC.preventivo(src, dst, q, cache_c)
    if v:
        return (out/10**pd["decimali"]*pd["prezzo_usd"]) / dollari
    # poi Curve per un salto e Uniswap per arrivare al debito
    v, d, pos, app, uscita, out = VC.primo_passo(src, q, cache_c)
    if not v: return None
    pu = PR.get(uscita)
    if not pu: return None
    r1 = (out/10**pu["decimali"]*pu["prezzo_usd"]) / dollari
    sede, d2, p2, a2 = VU.preventivo(uscita, dst, out, CONTR, cache_u)
    if not sede: return None
    r2 = VU._ULTIMA_RESA.get("resa")
    return (r1*r2) if r2 else None
def resa_a(src, dst, dollari, PR, cache):
    ps, pd = PR.get(src), PR.get(dst)
    if not ps or not pd: return None
    q = int(dollari/ps["prezzo_usd"]*10**ps["decimali"])
    migliore = 0
    for fee in VU.LIVELLI:
        if VU.vasca_a_livello(src, dst, fee, cache) is None: continue
        o = VU._quanto_torna_diretta(src, dst, q, fee)
        if o: migliore = max(migliore, o)
    for ponte in VU.PONTI:
        if ponte in (src, dst): continue
        f1 = VU.vasca(src, ponte, cache); f2 = VU.vasca(ponte, dst, cache)
        if not (f1 and f2): continue
        o = VU._quanto_torna_percorso(VU._percorso([src, f1, ponte, f2, dst]), q)
        if o: migliore = max(migliore, o)
    # E SI CHIEDE ANCHE A UNISWAP V4 (aggiunto il 5/11).
    # Senza questo, il verdetto "senza strada" veniva emesso QUI e la coppia
    # non arrivava mai al pianificatore, quindi il ripiego su v4 non avrebbe
    # mai visto proprio le coppie per cui esiste. Un verdetto va corretto
    # dove viene EMESSO, non dove si subisce.
    # NIENTE EXCEPT MUTO, nemmeno qui: un mio errore di codice ingoiato in
    # silenzio ha gia' trasformato una rotta al 99,62% in un verdetto
    # "senza strada" con 1,77 milioni di premio attaccati. Si tace solo
    # sulla rete.
    import vendita_univ4 as V4
    try:
        m4 = V4.quota(src, dst, q,
                      dst_e_weth=(dst.lower() ==
                                  "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"))
    except (OSError, TimeoutError):
        m4 = None
    if m4 and m4[0] > migliore:
        print(f"      v4 batte v3/Curve su {src[:8]}->{dst[:8]}: "
              f"{m4[0]} contro {migliore}")
        migliore = m4[0]
    # E IL PONTE MISTO: src ->(v3/ponti)-> USDC ->(v4)-> dst.
    #
    # PERCHE' SERVE, misurato il 5/11: su GHO la rotta DIRETTA non esiste da
    # nessuna parte, ma USDC->GHO su v4 rende il 100,08% fino a 100.000 $ --
    # venti volte meglio di v3 (100.079 GHO contro 7.561). Cercando solo la
    # strada diretta, nove coppie con debito GHO restavano "senza strada"
    # mentre la strada c'era in DUE pezzi, uno per piazza.
    # La regola: se due piazze hanno ciascuna metà del percorso, il
    # percorso esiste -- e il nostro contratto accetta una catena di
    # passaggi proprio per questo.
    PONTE_V4 = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"   # USDC
    if dst != PONTE_V4 and src != PONTE_V4:
        pp = PR.get(PONTE_V4)
        if pp:
            uno = 0
            for fee in VU.LIVELLI:
                if VU.vasca_a_livello(src, PONTE_V4, fee, cache) is None:
                    continue
                o = VU._quanto_torna_diretta(src, PONTE_V4, q, fee)
                if o:
                    uno = max(uno, o)
            for ponte in VU.PONTI:
                if ponte in (src, PONTE_V4):
                    continue
                f1 = VU.vasca(src, ponte, cache)
                f2 = VU.vasca(ponte, PONTE_V4, cache)
                if not (f1 and f2):
                    continue
                o = VU._quanto_torna_percorso(
                    VU._percorso([src, f1, ponte, f2, PONTE_V4]), q)
                if o:
                    uno = max(uno, o)
            if uno:
                try:
                    due = V4.quota(PONTE_V4, dst, uno,
                                   dst_e_weth=(dst.lower() == "0xc02aaa39b223"
                                               "fe8d0a0e5c4f27ead9083c756cc2"))
                except (OSError, TimeoutError):
                    due = None
                if due and due[0] > migliore:
                    print(f"      ponte misto v3+v4 su {src[:8]}->{dst[:8]}: "
                          f"{due[0]} contro {migliore}")
                    migliore = due[0]
    # ATTENZIONE A LEGGERE QUESTA RESA (nota del 5/11): e' l'uscita del
    # mercato valutata ai prezzi dell'ORACOLO, divisa per l'ingresso
    # valutato agli stessi prezzi. Quando esce sopra il 100% -- es.
    # WBTC->WETH al 100,28% -- NON abbiamo trovato soldi gratis: l'oracolo
    # e' un filo piu' basso del mercato. Serve per CONFRONTARE rotte, non
    # come profitto assoluto. Il profitto vero lo dice solo la guardia nel
    # contratto, che misura cio' che resta davvero.
    if not migliore: return None
    return (migliore/10**pd["decimali"]*pd["prezzo_usd"]) / dollari
def eti_corta(g, de, U):
    return f"{U.get(g,g[:8])}->{U.get(de,de[:8])}"
def main():
    PR = json.load(open(f"{D}/prezzi_oracolo.json"))
    U = {x["gettone"]: x["simbolo"] for x in json.load(open(f"{D}/unita_gettoni.json"))}
    co = {k.lower(): v for k, v in json.load(open(f"{D}/composizione.json")).items()}
    s = json.load(open(f"{D}/salute_note.json"))
    # le coppie che useremmo: delle posizioni dentro la banda, per premio
    coppie, visti = [], set()
    for a, c in co.items():
        d = s.get(a)
        if not d or d.get("salute", 9) >= 1.25 or d.get("debito", 0) < 2000: continue
        g = c["garanzia_principale"].lower(); de = c["debito_principale"].lower()
        if g == de or (g, de) in visti: continue
        visti.add((g, de)); coppie.append((g, de, d["debito"]*0.5*0.07))
    coppie.sort(key=lambda t: -t[2])
    import vendita_curve as VC
    cache = VU._carica(); cache_curve = VC._carica()
    try: vecchio = json.load(open(FUORI))
    except Exception: vecchio = {"tetti": {}}
    tetti = dict(vecchio.get("tetti") or {})
    print(f"   {len(coppie)} coppie da tarare (per premio)")
    print(f"   {'coppia':24s} {'tetto trovato':>14s} {'resa li':>9s}")
    nuovi, senza = 0, 0
    senza_strada = dict(vecchio.get("senza_strada") or {})
    for g, de, prem in coppie[:int(os.environ.get("QUANTE", "25"))]:
        trovato = None
        for t in TAGLIE:
            r = resa_a(g, de, t, PR, cache)
            # NIENTE EXCEPT MUTO. Difetto trovato il 4/11: qui c'era
            # `except Exception: rc = None`, e dentro resa_curve avevo un
            # NameError (usavo una variabile che non esisteva). L'except
            # l'ha inghiottito, la funzione ha risposto "nessuna resa", e
            # la coppia osETH->WETH e' stata scritta nei dati come "senza
            # strada" con $1.770.236 di premio attaccati.
            # Cioe': un mio errore di CODICE e' diventato una CONCLUSIONE
            # DI MERCATO sbagliata. E la strada c'era: 99,64% su Curve piu'
            # 99,98% su Uniswap, e l'avevo anche gia' provata sulla copia
            # della catena (568 GHO in cassa).
            # Un ripiego silenzioso su un calcolo e' una bugia: se il
            # calcolo si rompe lo si deve SAPERE.
            try:
                rc = resa_curve(g, de, t, PR, cache_curve, cache)
            except (NameError, TypeError, AttributeError, KeyError) as _bug:
                print(f"   !!! ERRORE DI CODICE in resa_curve: "
                      f"{type(_bug).__name__}: {_bug}")
                raise
            except Exception as _rete:
                # la rete che non risponde non e' un errore nostro
                print(f"   (curve muta per {eti_corta(g,de,U)}: {str(_rete)[:40]})")
                rc = None
            if rc is not None and (r is None or rc > r): r = rc
            if r is None: continue
            if r >= RESA_MINIMA: trovato = (t, r); break
        eti = f"{U.get(g,g[:8])}->{U.get(de,de[:8])}"
        if trovato:
            t, r = trovato
            senza_strada.pop(f"{g}|{de}", None)   # se una strada e' tornata, si toglie
            tetti[f"{g}->FAM"] = tetti.get(f"{g}->FAM")   # non si tocca la vecchia forma
            tetti[f"{g}|{de}"] = t
            nuovi += 1
            print(f"   {eti:24s} {t:14,} {100*r:8.2f}%")
        else:
            senza += 1
            # SI REGISTRA ANCHE IL NO. Il 4/11 qui non si scriveva niente
            # quando nessuna taglia andava bene: il sistema ricadeva sul
            # tetto generico e ritentava la stessa coppia a ogni passata,
            # per sempre, bruciando il giro su vendite impossibili. E
            # dall'esterno sembrava un guasto transitorio invece di un
            # fatto: "questa coppia su Uniswap non si vende".
            # Un no misurato e' informazione quanto un si'.
            senza_strada[f"{g}|{de}"] = {"premio_in_gioco": round(prem, 2),
                                         "quando": time.time()}
            print(f"   {eti:24s} {'nessuna taglia':>14s} {'—':>9s}  "
                  f"(${prem:,.0f} di premio senza strada)")
        VU._salva(cache); VC._salva(cache_curve)
    tetti = {k: v for k, v in tetti.items() if v}
    # UNA COPPIA NON PUO' STARE IN ENTRAMBI GLI ELENCHI (riparato il 5/11).
    # Difetto trovato: quattro coppie avevano un tetto MISURATO e restavano
    # marchiate "senza strada" -- fra cui WETH->GHO, WBTC->GHO e cbBTC->GHO
    # a 5.000 $, cioe' proprio quelle appena aperte dal ponte v3+v4. Il
    # pianificatore legge "senza strada" e le scartava per sempre, quindi il
    # lavoro di misura non arrivava mai a produrre un ordine.
    # Causa: il "no" resta scritto da una passata precedente se la passata
    # nuova non rimisura quella coppia, e nessuno confrontava i due elenchi.
    # Qui si fa valere la regola: se c'e' un tetto, il "no" cade.
    _tolte = [k for k in list(senza_strada) if k in tetti]
    for k in _tolte:
        senza_strada.pop(k, None)
    if _tolte:
        print(f"   {len(_tolte)} coppie avevano un tetto E il marchio "
              f"'senza strada': il marchio cade")
    vecchio["tetti"] = tetti
    vecchio["senza_strada"] = senza_strada
    vecchio["misurato_il"] = time.strftime("%Y-%m-%d %H:%M", time.gmtime())
    vecchio["come"] = ("per dimezzamenti con il Quoter di Uniswap: il tetto e' la "
                       "taglia piu' grande la cui resa resta sopra la soglia")
    json.dump(vecchio, open(FUORI, "w"), indent=1)
    tot = sum(v["premio_in_gioco"] for v in senza_strada.values())
    print(f"   {nuovi} coppie con un tetto, {senza} senza nessuna taglia buona")
    print(f"   premio che oggi NON sappiamo vendere: ${tot:,.0f} "
          f"su {len(senza_strada)} coppie")
    return 0
if __name__ == "__main__":
    sys.exit(main())
