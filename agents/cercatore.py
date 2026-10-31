"""CERCATORE — cerca la successione di pattern che precede un rendimento in eccesso.

E' il cuore del loop 1: tutto il resto e' impalcatura, questo e' il pezzo che cerca.

COSA CERCA. Combinazioni di condizioni osservabili al momento della decisione — liquidita', numero
di compratori distinti, ritmo degli scambi, vendibilita' dimostrata — che precedano un rendimento
migliore degli altri token dello stesso momento.

COSA NON CERCA: il rendimento ASSOLUTO. Misurato il 22/09: la quota di token in rialzo oscilla fra
il 22% e il 67% a seconda dell'ora. In un'ora buona sale quasi tutto, e una regola provata li'
sembra geniale senza aver selezionato niente. Quindi il metro e' l'ECCESSO rispetto ai token
contemporanei della stessa chain.

LE DIFESE, TUTTE NATE DA UN ERRORE GIA' FATTO:

  1. PROFONDITA' MASSIMA DUE CONDIZIONI. Con tre, il numero di casi per cella crolla e ogni cella
     diventa rumore travestito da scoperta.

  2. MINIMO DI POOL PER CELLA. Sotto la soglia non si riporta un numero: si scrive «campione
     insufficiente». Un numero su venti pool sembra un risultato e non lo e'.

  3. SI CONTANO LE DOMANDE FATTE. Il numero di combinazioni provate esce insieme al risultato: e'
     il denominatore della fortuna. Con abbastanza domande una risposta buona si trova sempre.

  4. IL VINCITORE NON E' UNA SCOPERTA. Quello che esce di qui e' un CANDIDATO, da scrivere in
     IPOTESI.md con la sua condizione di morte e poi confermare in avanti. La revisione esterna e'
     stata esplicita: «BH non protegge il vincitore di una ricerca adattiva».

  5. TUTTO PASSA DAL MOTORE A VUOTO. Prima di credere a un candidato si guarda quanto spesso questa
     stessa ricerca promuove qualcosa su dati costruiti senza alcun vantaggio.

IL COSTO E' DENTRO, NON SOTTRATTO ALLA FINE. Impatto misurato (0,45% mediano) raddoppiato per
prudenza, andata e ritorno. Il token tipico tocca un massimo del 2%: senza il costo dentro, ogni
risultato di questa ricerca sarebbe una fantasia da mezzo punto.
"""
import gzip
import json
import math
import os
import random
import zlib
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verso as V                                             # noqa: E402

CHAIN = os.environ.get("CHAIN", "base")
ORIZZONTE_ORE = float(os.environ.get("ORIZZONTE_ORE", 6))
MIN_CELLA = int(os.environ.get("MIN_CELLA", 100))
COSTO_GIRO = float(os.environ.get("COSTO_GIRO", 0.018))     # 0,45% x2 prudenza x2 lati
FUORI = f"data/loop1/candidati_{CHAIN}.json"
CAMPIONE = int(os.environ.get("CAMPIONE", 3))
ORE_ATTESA = float(os.environ.get("ORE_ATTESA", 2))               # 1 file su N, per girare in fretta


# QUI C'ERA `a1/a0` FISSO, l'esatto INVERSO di quello che usava `insieme.py` (`a0/a1`) sugli stessi
# dati (25/09). Uno dei due doveva essere sbagliato, e in realta' lo erano tutti e due: il verso
# dipende da quale token e' il memecoin, e cambia da pool a pool. Vedi `agents/verso.py`.
# Che due pezzi dello stesso sistema calcolassero il prezzo al contrario l'uno dell'altro per
# giorni, senza che nessuno se ne accorgesse, e' il difetto piu' istruttivo della settimana:
# nessuno dei due era palesemente assurdo da solo.


def osservazioni():
    """Una riga per pool: le condizioni al momento della decisione, e cosa e' successo dopo.

    Il momento della decisione e' fissato a un quarto della vita osservata del pool: e' arbitrario
    ma DICHIARATO, e uguale per tutti. Sceglierlo caso per caso sarebbe gia' una selezione."""
    fuori = []
    verso = V.carica(CHAIN)
    senza_verso = [0]
    non_giudicabili = [0]   # quanti pool escono perche' nati troppo tardi per essere giudicati
    for sub in ("storico", "vivo"):
        d = f"data/multichain/{CHAIN}/{sub}"
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            # NON `hash(fn)`: in Python l'hash delle stringhe e' randomizzato a ogni processo
            # (PYTHONHASHSEED), quindi ogni esecuzione pescava un sottoinsieme DIVERSO. Trovato il
            # 23/09 da Astra, che ha notato un'impossibilita' aritmetica: la quota aggregata (9,5%)
            # era maggiore di entrambe le meta' (8,8% e 5,8%). Non era un errore di calcolo: erano
            # campioni diversi confrontati come se fossero lo stesso. Tutti i numeri della notte
            # sono stati prodotti su universi differenti.
            if zlib.crc32(fn.encode()) % CAMPIONE:
                continue
            try:
                rr = [json.loads(l) for l in gzip.open(os.path.join(d, fn), "rt") if l.strip()]
            except Exception:
                continue
            rr = [r for r in rr if r.get("ts") and r.get("a0") and r.get("a1") and r.get("w")]
            if len(rr) < 40:
                continue
            rr.sort(key=lambda x: x["ts"])
            meme_t0 = verso.get(fn.split(".")[0].lower())
            if meme_t0 is None:
                senza_verso[0] += 1
                continue
            prezzo = lambda x: V.prezzo(x, meme_t0)
            # IL MOMENTO DELLA DECISIONE NON PUO' SAPERE QUANDO IL POOL MORIRA' (23/09, rilievo
            # della revisione esterna — indicato da Astra come «il singolo controllo che ha
            # maggiore probabilita' di far crollare il risultato». Aveva ragione).
            # Prima era «un quarto della vita OSSERVATA», ma la vita osservata finisce con l'ultimo
            # scambio, che e' un evento futuro: un pool vissuto 24 ore aveva la decisione all'ora
            # 6, uno morto in un'ora a 15 minuti. Per sapere dove cade un quarto bisogna gia'
            # sapere quando morira' — e la longevita' e' correlata con tutto il resto.
            # Misurato: i candidati si dimezzavano correggendolo (robinhood 71 -> 31, base 52 ->
            # 23), e su base il walk-forward passava da 66% a ZERO regole che reggono.
            # Adesso: due ore dal primo scambio osservato. Uguale per tutti, e noto in quel
            # momento. Chi a due ore non scambia piu' non si sarebbe potuto comprare comunque.
            _lim = rr[0]["ts"] + ORE_ATTESA * 3600
            i = None
            for _k, _x in enumerate(rr):
                if _x["ts"] >= _lim:
                    i = _k
                    break
            if i is None or i < 5:
                continue
            p0 = prezzo(rr[i])
            if not p0:
                continue
            t0 = rr[i]["ts"]
            prima = rr[:i + 1]
            # --- condizioni, tutte note a t0 ---
            compratori = len({x["w"].lower() for x in prima})
            scambi = len(prima)
            versi = set()
            for x in prima:
                try:
                    versi.add(1 if float(x["a0"]) > 0 else -1)
                except Exception:
                    pass
            durata = max(1.0, (t0 - prima[0]["ts"]) / 3600)
            cond = {"compratori": compratori,
                    "scambi": scambi,
                    "ritmo": scambi / durata,
                    "indici_per_scambio": compratori / max(1, scambi),
                    "vendibile": 1 if len(versi) > 1 else 0,
                    "eta_ore": durata}
            # --- esito ---
            # SI MISURA SOLO DOVE LA RACCOLTA E' ARRIVATA FINO IN FONDO (25/09, seconda stesura).
            # La prima stesura, stamattina, guardava l'ultimo scambio DI QUESTO POOL: se non
            # arrivava all'orizzonte, il pool usciva. Sembrava prudenza ed era sopravvivenza —
            # un pool muore smettendo di scambiare, quindi quel criterio scartava i morti, cioe'
            # proprio le perdite totali che il 23/09 avevamo faticato ad AGGIUNGERE.
            # Avrebbe riportato base al suo +16% illusorio per la seconda volta.
            # Il confronto vero si fa contro la FINE DELLA RACCOLTA, che e' una data e non sa
            # niente di come e' andata: si conosce solo dopo aver letto tutto, quindi il taglio
            # e' rimandato a fine giro (vedi in fondo a questa funzione).
            dopo = [x for x in rr[i + 1:] if x["ts"] <= t0 + ORIZZONTE_ORE * 3600]
            pp = [prezzo(x) for x in dopo]
            pp = [x for x in pp if x]
            if not pp:
                # CHI ENTRA E NON PUO' PIU' USCIRE HA PERSO TUTTO — MA SOLO SE ABBIAMO GUARDATO
                # (23/09 la prima meta', 25/09 la seconda).
                #
                # 23/09: scartavo i pool che dopo l'entrata non scambiano piu'. Sono pochi (1,4% su
                # robinhood, 3,5% su base) ma sono la perdita massima possibile, e toglierli e' una
                # selezione che premia i casi migliori. Contandoli, base passava da +16,0% a -1,1%:
                # TUTTO il guadagno apparente di quella chain era l'esclusione di 27 pool.
                #
                # 25/09, la meta' che mancava: «non ci sono scambi dopo» ha DUE cause diverse, e le
                # trattavo come una sola. O il pool e' morto davvero, o **l'osservazione finisce
                # prima dell'orizzonte** e gli scambi ci sono ma non li abbiamo raccolti. Il secondo
                # caso non e' una perdita totale: e' un pool che non possiamo ancora giudicare.
                # Misurato lo stesso giorno sull'insieme ricco: le trappole scendono dal 35,0% al
                # 19,0% e il fondale da -32,4% a -17,0% quando si guardano solo i pool osservati
                # per intero. Ogni numero era gonfio di circa il doppio.
                #
                # IN POSITIVO: **dichiara quanto hai osservato, e conta come esito solo cio' che
                # cade dentro la finestra che hai davvero guardato.** Qui: la perdita totale si
                # registra solo se l'osservazione arriva oltre l'orizzonte e comunque non c'e'
                # nessuno scambio; altrimenti il pool esce dal campione, non dalla parte sbagliata.
                # (qui si arriva solo se l'osservazione copre l'orizzonte: la guardia sopra ha
                # gia' tolto i pool non giudicabili, quindi questo silenzio e' silenzio VERO.)
                fuori.append({"ora": int(t0 // 3600), "_t": t0, "_fine": rr[-1]["ts"],
                              "rend": -0.98 - COSTO_GIRO, **cond})
                continue
            rend = pp[-1] / p0 - 1
            if not (-0.99 < rend < 20):
                continue                    # scarti assurdi gia' noti: si tolgono, e si dichiara
            fuori.append({"ora": int(t0 // 3600), "_t": t0, "_fine": rr[-1]["ts"],
                          "rend": rend - COSTO_GIRO, **cond})
    if senza_verso[0]:
        print(f"   {senza_verso[0]} pool saltati: non si capisce quale token e' il memecoin",
              flush=True)
    frontiera = max((o["_fine"] for o in fuori), default=0)
    maturi = [o for o in fuori if frontiera - o["_t"] >= ORIZZONTE_ORE * 3600]
    non_giudicabili[0] = len(fuori) - len(maturi)
    for o in maturi:
        o.pop("_t", None); o.pop("_fine", None)
    fuori = maturi
    # SI DICE SEMPRE QUANTI NE ABBIAMO TOLTI (25/09). Un campione che si restringe in silenzio e'
    # il modo piu' comodo di mentire: se domani i pool giudicabili fossero il 5%, questa riga lo
    # farebbe vedere subito invece di lasciarmi leggere percentuali su un pugno di casi.
    print(f"CERCATORE | {CHAIN}: {len(fuori)} giudicabili, "
          f"{non_giudicabili[0]} nati da meno di {ORIZZONTE_ORE}h prima della fine raccolta "
          f"({100*non_giudicabili[0]/max(1, len(fuori)+non_giudicabili[0]):.0f}% del totale)",
          flush=True)
    return fuori


def eccessi(oss):
    """Il rendimento di ognuno MENO la mediana dei token della stessa ora.

    E' il cuore della misura: «e' salito» non basta, perche' in un'ora buona sale quasi tutto."""
    per_ora = defaultdict(list)
    for o in oss:
        per_ora[o["ora"]].append(o["rend"])
    mediana = {}
    for h, v in per_ora.items():
        v2 = sorted(v)
        mediana[h] = v2[len(v2) // 2]
    fuori = []
    for o in oss:
        if len(per_ora[o["ora"]]) < 5:
            continue                        # senza abbastanza compagni, «in eccesso» non ha senso
        fuori.append({**o, "ecc": o["rend"] - mediana[o["ora"]]})
    return fuori


def media_pf(v):
    return sum(1 + x for x in v) / len(v) - 1 if v else 0.0


def batte_il_caso(gruppo, tutte, rnd, giri=300):
    """Il gruppo scelto batte un gruppo A CASO della stessa dimensione, nelle stesse ore?

    IL CONFRONTO MEDIA-CONTRO-MEDIANA E' ROTTO (23/09, trovato dal primo giro di questo cercatore).
    Misuravo l'eccesso come «media del gruppo meno mediana dell'ora». Su una distribuzione con la
    coda a destra la media sta quasi sempre sopra la mediana, quindi QUASI QUALUNQUE gruppo risulta
    in eccesso per costruzione: 67 combinazioni su 111 «passavano», con eccessi del 10-20%.
    Un risultato del genere non e' una scoperta, e' un allarme — e per fortuna era troppo bello per
    essere creduto.

    La prova onesta e' il confronto con il caso: si rimescolano le appartenenze DENTRO ciascuna ora
    (cosi' l'umore del momento resta uguale) e si guarda quante volte un gruppo casuale della stessa
    dimensione fa meglio di quello scelto. Se la regola non seleziona niente, lo batte spesso.
    Tornano: il quantile del gruppo vero nella distribuzione casuale, e la differenza mediana."""
    per_ora = defaultdict(list)
    for o in tutte:
        per_ora[o["ora"]].append(o["rend"])
    quante_per_ora = defaultdict(int)
    for o in gruppo:
        quante_per_ora[o["ora"]] += 1
    vero = media_pf([o["rend"] for o in gruppo])
    finti = []
    for _ in range(giri):
        pescati = []
        for h, k in quante_per_ora.items():
            disponibili = per_ora.get(h) or []
            if len(disponibili) <= k:
                pescati += disponibili
            else:
                pescati += rnd.sample(disponibili, k)
        if pescati:
            finti.append(media_pf(pescati))
    if len(finti) < 50:
        return None
    finti.sort()
    battuto_da = sum(1 for x in finti if x >= vero)
    quota = battuto_da / len(finti)          # quanto spesso il caso fa meglio o uguale
    mediano_caso = finti[len(finti) // 2]
    return {"vero": vero, "caso_mediano": mediano_caso, "quota_caso_meglio": quota}


def intervallo(v, rnd, giri=200):
    """Intervallo al 95%, ricampionando le ORE e non le righe: i token contemporanei non sono
    osservazioni indipendenti."""
    per_ora = defaultdict(list)
    for o in v:
        per_ora[o["ora"]].append(o["ecc"])
    blocchi = list(per_ora.values())
    if len(blocchi) < 8:
        return None
    medie = []
    for _ in range(giri):
        sc = [rnd.choice(blocchi) for _ in range(len(blocchi))]
        medie.append(media_pf([x for b in sc for x in b]))
    medie.sort()
    return medie[int(0.025 * giri)], medie[int(0.975 * giri)]


def main():
    rnd = random.Random(20260923)
    oss = eccessi(osservazioni())
    if len(oss) < 300:
        print(f"CERCATORE | {CHAIN}: solo {len(oss)} osservazioni utili: campione insufficiente, "
              f"non cerco. Meglio niente che un numero su pochi casi.", flush=True)
        return
    print(f"CERCATORE | {CHAIN}: {len(oss)} osservazioni, orizzonte {ORIZZONTE_ORE}h, "
          f"costo applicato {100*COSTO_GIRO:.1f}%", flush=True)

    CAMPI = ["compratori", "scambi", "ritmo", "indici_per_scambio", "eta_ore"]
    tagli = {}
    for c in CAMPI:
        v = sorted(o[c] for o in oss)
        tagli[c] = [v[int(len(v) * q)] for q in (0.25, 0.5, 0.75)]

    regole = []
    for c in CAMPI:
        for s in tagli[c]:
            regole.append([(c, s, True)])
            regole.append([(c, s, False)])
    regole.append([("vendibile", 0.5, True)])
    for i, a in enumerate(CAMPI):
        for b in CAMPI[i + 1:]:
            for sa in tagli[a]:
                for sb in tagli[b]:
                    regole.append([(a, sa, True), (b, sb, True)])

    tentate = 0
    trovati = []
    for reg in regole:
        g = [o for o in oss
             if all((o[c] >= s) if verso else (o[c] < s) for c, s, verso in reg)]
        if len(g) < MIN_CELLA:
            continue
        tentate += 1
        p = batte_il_caso(g, oss, rnd)
        if not p:
            continue
        # il gruppo scelto deve battere il caso quasi sempre: sotto il 5% delle volte in cui il
        # caso fa meglio. E' la stessa soglia del motore a vuoto, per coerenza.
        # DUE CONDIZIONI INSIEME, NON UNA (23/09). Con la sola «batte il caso» passavano 73
        # combinazioni su 111 — ma i primi classificati rendevano −9,78% contro il −14,48% del
        # caso: sceglievano i MENO PEGGIO. Battere il caso in un mercato che perde vuol dire
        # perdere meno, e perdere meno non e' guadagnare.
        # Serve anche che il gruppo scelto sia in guadagno DOPO i costi. Altrimenti il cercatore
        # premia l'abilita' di annegare piu' lentamente.
        if p["quota_caso_meglio"] < 0.05 and p["vero"] > 0:
            trovati.append({"regola": [[c, round(s, 4), v] for c, s, v in reg],
                            "n": len(g),
                            "rend_vero": round(p["vero"], 4),
                            "rend_caso": round(p["caso_mediano"], 4),
                            "quota_caso_meglio": round(p["quota_caso_meglio"], 4)})

    trovati.sort(key=lambda x: -x["rend_vero"])
    os.makedirs(os.path.dirname(FUORI), exist_ok=True)
    json.dump({"tentate": tentate, "candidati": trovati[:20],
               "osservazioni": len(oss), "costo": COSTO_GIRO},
              open(FUORI, "w"), indent=1)

    print(f"   combinazioni provate: {tentate}")
    print(f"   candidati che battono il caso E guadagnano dopo i costi: {len(trovati)}")
    if trovati:
        print(f"\n   i primi, e sono CANDIDATI non scoperte:")
        for t in trovati[:5]:
            reg = " e ".join(f"{c} {'>=' if v else '<'} {s:.3g}" for c, s, v in
                             [(x[0], x[1], x[2]) for x in t["regola"]])
            print(f"      {reg}")
            print(f"         {t['n']} pool | scelto {100*t['rend_vero']:+.2f}% | "
                  f"a caso {100*t['rend_caso']:+.2f}% | il caso fa meglio nel "
                  f"{100*t['quota_caso_meglio']:.1f}% dei rimescolamenti")
        print(f"\n   Su {tentate} combinazioni provate, {len(trovati)} superano il limite.")
        print(f"   Questo NON dice che siano vere: dice quante ne sono uscite. Il passo successivo")
        print(f"   e' il motore a vuoto — quante ne uscirebbero da dati senza alcun vantaggio.")
    else:
        print(f"\n   Nessun candidato. Su questo campione, nessuna combinazione di due condizioni")
        print(f"   batte i token contemporanei dopo i costi. E' un risultato, non un fallimento.")


if __name__ == "__main__":
    main()
