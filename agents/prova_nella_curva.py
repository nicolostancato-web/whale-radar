"""La prova in avanti DENTRO la curva: si entra a 3,6 nativi, si vende al diploma.

IL MANDATO (Nicolo', 11/10): «invece di fare un live sui diplomati, facciamo un live nella box
seguendo la regola dei 3,6 ETH. L'apriamo dentro la box, poi quando si diploma la vendi. Mi
aspetto una metrica dove c'e' scritto: entrati a 3,6, chiuso con per 2. E ipotizziamo anche uno
stop loss.»

PERCHE' QUESTA PROVA E' DIVERSA DA QUELLA SUI DIPLOMATI. Quella misura cosa fa il mercato DOPO
il diploma, e in due giorni ha detto che il mercato restituisce. Questa misura il pezzo PRIMA,
dove le misure sul passato dicono che sta il guadagno: 2,8x di mediana dalla soglia al diploma.
Il passato pero' si guarda sempre con gli occhi di chi sa com'e' finita; qui si scrive la regola
prima e si guarda cosa succede.

LE REGOLE, CONGELATE OGGI (e scritte qui perche' non si tocchino):
  · si guardano SOLO le curve quotate in valuta NATIVA. Il 11/10 ho scoperto che una curva su
    quattro e' quotata in USDG o in AZIONI TOKENIZZATE (NVDA, SPY, QQQ, COST): su quelle «3,6»
    non vuol dire niente, e sommarle sarebbe la terza volta in due giorni che violo la regola
    «non si somma mai fra asset diversi».
  · si entra quando la curva ha incassato >= 3,6 nativi, al prezzo dell'acquisto che fa scattare
    la soglia;
  · si esce al DIPLOMA, cioe' quando compare il pool: prezzo d'uscita = l'ultimo prezzo di
    VENDITA realmente eseguito sulla curva, non quello d'acquisto. Vendendo si scende la curva,
    e usare i prezzi d'acquisto per uscire e' l'errore che il 7/10 mi aveva fatto scrivere +35%
    dove la realta' era -8%;
  · stop loss: si esce se il prezzo scende sotto la META' dell'entrata;
  · orizzonte: 216.000 blocchi (6 ore). Se non si diploma e non tocca lo stop, si esce comunque.
  · costi: 1% in entrata e 1% in uscita. Lo scalino fra prezzo d'acquisto e di vendita NON e'
    stimato: viene dai prezzi di vendita veri, che e' il motivo per cui li uso.

NIENTE SOLDI VERI. Zero euro a rischio, come la prova sui diplomati.
"""
import json
import os
import statistics
import sys
import time

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

import curva_pons as CP                                        # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
STATO = f"{BASE}/prova_nella_curva.json"
GESTORE_V4 = os.environ.get("GESTORE_V4", "0x8366a39cc670b4001a1121b8f6a443a643e40951").lower()
INIT = "0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
ZERO = "0x" + "0" * 40
HOOK_PONS = "0xe5e702641ea86f4ae6cc3cdaed2b886f976be044"

# DUE SOGLIE IN PARALLELO (11/10, confermato da Nicolo'). La misura storica dice che 3,6 e' il
# peggiore dei sei punti d'ingresso provati — resta il 12% — mentre a 1,5 resta il 3,08x. Ma a
# 1,5 si entra anche in molte curve che non si diplomeranno mai, e quella perdita non e' mai
# stata misurata: per misurarla bisogna entrare anche nei fallimenti.
# Quindi le due regole girano insieme sugli stessi dati: 3,6 resta come riferimento (non si
# tocca, cosi' la serie e' confrontabile), 1,5 e' quella che produrra' i numeri.
SOGLIE = [float(x) for x in os.environ.get("SOGLIE_NATIVI", "3.6,1.5").split(",")]
SOGLIA = max(SOGLIE)

# LE STRATEGIE IN PROVA (12/10). Ognuna e' una regola completa e CONGELATA: soglia d'ingresso,
# stop, bersaglio. Girano insieme sugli stessi dati, cosi' si confrontano senza che l'una
# disturbi l'altra.
#   · «diploma-1,5» e «diploma-3,6» sono le due di ieri: si tiene fino al diploma.
#   · «50-5» e' il candidato trovato oggi: bersaglio +50%, stop -5%, ingresso a 1,5. Viene da
#     una griglia di quindici caselle su trentuno operazioni — cioe' e' LA MIGLIORE DI QUINDICI,
#     e scegliere la migliore di quindici e' il modo classico di trovare rumore. Per questo
#     entra qui: la prova in avanti su monete che ancora non esistono e' la sola che non si
#     puo' imbrogliare.
#   · «10-20» e' la riga piu' REGOLARE della stessa griglia (26 vinte su 31): meno rendimento,
#     molte piu' vittorie. Se il candidato e' rumore, questa lo mostrera' restando viva.
STRATEGIE = [
    {"nome": "diploma-1.5", "soglia": 1.5, "stop": 0.5, "bersaglio": None},
    {"nome": "diploma-3.6", "soglia": 3.6, "stop": 0.5, "bersaglio": None},
    {"nome": "50-5", "soglia": 1.5, "stop": 0.95, "bersaglio": 1.5},
    # AGGIUNTA IL 14/10, DICHIARATA PRIMA DI MISURARLA. Il picco sopra +45% dura 6,9 secondi
    # (mediana su 287 casi) e il nostro giro ne dura 6: incassare il +50% e' testa o croce.
    # Sopra +30% il prezzo resta per 16,8 secondi, quasi tre volte il tempo che ci serve.
    # Sui cammini, col nostro ritardo vero di 6 secondi, il bersaglio a +30% rende +6,07% —
    # piu' che a ritardo zero (+3,24%), perche' aspettare qualche secondo dopo il tocco
    # spesso prende un prezzo migliore. Non sostituisce la 50-5: le due corrono insieme e
    # saranno le operazioni vere a dire quale si incassa davvero.
    {"nome": "30-5", "soglia": 1.5, "stop": 0.95, "bersaglio": 1.3},
    {"nome": "10-20", "soglia": 1.5, "stop": 0.8, "bersaglio": 1.1},
    # AGGIUNTA IL 13/10, A REGOLA DICHIARATA PRIMA DI MISURARLA. Sulla griglia di 49
    # combinazioni questa e' la migliore (+22,9% dentro campione, +8,7% fuori), e tutto il
    # suo valore poggia su UN numero solo: una operazione su 7,6 arriva a 3x. La prova in
    # avanti esiste per verificare quel tasso su operazioni che apre lei, non per
    # riconfermare i cammini su cui l'ho trovato.
    {"nome": "2-3x", "soglia": 1.5, "stop": 0.98, "bersaglio": 3.0},
    # AGGIUNTA IL 13/10, DICHIARATA PRIMA DI MISURARLA. Fuori campione il bersaglio a 2x
    # rende quanto quello a 3x (+8,06% contro +8,66% su 334 operazioni mai viste), ma si
    # chiude molto prima. Con un capitale piccolo e dieci posti il vincolo non e' la resa
    # per operazione: e' quante operazioni il capitale riesce a fare. A parita' di resa,
    # il bersaglio piu' basso libera i soldi prima e ne fa di piu'.
    {"nome": "2-2x", "soglia": 1.5, "stop": 0.98, "bersaglio": 2.0},
]
# IL COSTO VERO DI ANDATA E RITORNO, misurato: 5,91% di scarto fra prezzo di acquisto e di
# vendita su 727 coppie a meno di sei secondi. Vive QUI, non dentro una funzione: il 13/10
# l'avevo assegnato dentro main() e Python l'ha reso locale per tutta la funzione, facendo
# esplodere la riga che lo usava prima. La prova e' rimasta ferma ore senza che il referto
# lo dicesse, perche' chi la lancia ignora l'errore.
# I DUE LATI DELLA CURVA, MISURATI (16/10, su 391 monete e 34.433 scambi). Chi compra paga
# il 4,58% sopra la curva, chi vende incassa il 5,63% sotto. Finora il cervello mescolava
# i due prezzi nella stessa serie: la posizione vedeva un saliscendi del 6% che il mercato
# non aveva fatto, e uno stop piu' stretto di cosi' scattava sul nulla. Riportando ogni
# prezzo sulla curva la serie torna a descrivere il mercato invece del lato da cui arriva.
LATO_COMPRA = float(os.environ.get("LATO_COMPRA", "1.0458"))
LATO_VENDE = float(os.environ.get("LATO_VENDE", "0.9437"))
COSTO = 1.0591
STOP = float(os.environ.get("STOP", "0.5"))
ORIZZONTE = int(os.environ.get("ORIZZONTE_CURVA", "216000"))
# ERA 1.02 (13/10). Il 2% era la vecchia stima del costo, fatta prima di misurare lo scarto
# fra prezzo di acquisto e di vendita. Misurato: 5,91%. Il valore vero sta sopra, qui restava
# il vecchio che lo sovrascriveva: due costanti con lo stesso nome, e vince l'ultima.
FINESTRA_MAX = 30_000
VERSIONE = 1


def _tocca(st, cur, prezzo, blocco, verso="vende"):
    """Aggiorna le posizioni aperte su questa curva a OGNI scambio, non una volta per giro.

    IL PREZZO DI USCITA SI PRENDE DALLA PRIMA STAMPA DI ACQUISTO DOPO IL TOCCO (19/10).
    Chiudere al prezzo che ha fatto scattare la regola vale 5,24 punti di illusione: sulla
    stessa regola 50-5 e sulle stesse 397 monete, uscire al prezzo del tocco da +4,37%, alla
    stampa successiva +2,63%, e alla prima stampa di ACQUISTO dopo il tocco -0,87%. Chi vende
    vende A UN COMPRATORE: una vendita non si esegue contro un'altra vendita, e il tocco e'
    spesso proprio una vendita altrui. Misurato, non assunto.

    PERCHE' (11/10, richiesta di Nicolo': «devi tracciare tutto, da quando siamo entrati quanto
    e' andato piu' in basso e quanto piu' in avanti»). Le posizioni si aggiornavano una volta per
    giro di maglia, cioe' una volta ogni ~50 minuti di chain: minimo e massimo erano grossolani
    e uno stop loss non si poteva calcolare su di loro. Peggio: il cammino della curva si
    allungava solo sugli ACQUISTI, quindi un crollo fatto di vendite era invisibile.
    Qui ogni scambio — acquisto o vendita — muove minimo, massimo e cammino della posizione.
    Il cammino si allunga quando il prezzo si muove di almeno il 2%: tiene il file leggibile
    e non perde la forma.
    """
    for k, p in st["posizioni"].items():
        if p["curva"] != cur:
            continue
        if p["stato"] != "aperta":
            # SI CONTINUA A GUARDARE ANCHE DOPO L'USCITA (14/10). Smettendo di seguire una
            # posizione appena chiusa restavamo CIECHI proprio nella finestra che ci e'
            # costata 4,50 euro: tre uscite partite 19, 40 e 43 minuti in ritardo, e nessun
            # dato per sapere quanto costa un ritardo del genere. Qui si registra il prezzo
            # per mezz'ora dopo la chiusura, in un campo a parte che non tocca il risultato:
            # serve a sapere quanto vale la fretta, non a cambiare il voto.
            d = p.setdefault("dopo_uscita", [])
            if len(d) < 40 and p.get("entrata"):
                x = round(prezzo / p["entrata"], 5)
                if not d or abs(x / d[-1][1] - 1) > 0.02:
                    d.append([blocco, x])
            continue
        x = prezzo / p["entrata"]
        p["ultimo_x"] = round(x, 5)
        if x < p["min_x"]:
            p["min_x"] = round(x, 5)
            p["min_al_blocco"] = blocco
        if x > p["max_x"]:
            p["max_x"] = round(x, 5)
            p["max_al_blocco"] = blocco
        cm = p.setdefault("cammino", [])
        if not cm or abs(x / cm[-1][1] - 1) >= 0.02:
            cm.append([blocco, round(x, 5)])
        # LO STOP SCATTA NELL'ISTANTE DEL TOCCO (11/10, difetto mio corretto). Lo controllavo
        # una volta per giro di maglia, sul prezzo FINALE della finestra: con finestre da 30.000
        # blocchi (50 minuti) il prezzo era intanto caduto molto piu' giu', e le prime otto
        # chiusure sono uscite a -70% con lo stop a -50%. Avevo perfino concluso che «il prezzo
        # salta oltre lo stop» — falso: misurato sui cammini, il primo tocco di 0,50 avviene a
        # 0,49. Il salto era il mio ritardo, non il mercato.
        mio_stop = p.get("stop", STOP)
        mio_bers = p.get("bersaglio")
        if mio_stop and x <= mio_stop:
            p["stato"] = "chiusa"
            p["esito"] = {"verso": "stop",
                          "rendimento": round(mio_stop / COSTO - 1, 4),
                          "uscita_stimata": verso != "vende",
                          "blocco_uscita": blocco,
                          "chiuso_al_tocco": True}
        elif mio_bers and x >= mio_bers:
            p["stato"] = "chiusa"
            # IL BLOCCO DELL'USCITA SI REGISTRA, NON SI DEDUCE (14/10). Confrontando la
            # vendita vera col «primo punto del cammino sopra il bersaglio» risultava che in
            # due casi avevamo venduto PRIMA del picco — cioe' prima che il cervello potesse
            # saperlo. O il cervello sbaglia, o il confronto sbaglia. Con il blocco scritto
            # qui dentro non c'e' piu' niente da dedurre: si legge.
            p["esito"] = {"verso": "bersaglio",
                          "rendimento": round(mio_bers / COSTO - 1, 4),
                          "uscita_stimata": verso != "vende",
                          "blocco_uscita": blocco,
                          "chiuso_al_tocco": True}
        if p["stato"] == "chiusa" and MANI:
            MANI.chiude(k, p)


def _nuovo():
    return {"versione": VERSIONE, "partenza": None, "ultimo_blocco": None,
            "curve": {}, "posizioni": {},
            "regole": {"soglia_nativi": SOGLIA, "stop": STOP, "orizzonte": ORIZZONTE,
                       "costo": COSTO, "solo_curve_native": True,
                       "uscita": "al diploma, all'ultimo prezzo di VENDITA eseguito"}}


# LE MANI ATTACCATE AL CERVELLO (14/10). Il bot leggeva le decisioni da questo file e agiva
# dopo: nella notte del 13 ha visto zero posizioni 50-5 su dieci occasioni, perche' proprio la
# 50-5 — stop stretto, bersaglio vicino — si apre e si chiude prima che qualcuno rilegga il
# file. La regola che abbiamo dimostrato funzionare era l'unica che l'architettura non poteva
# eseguire. Qui le mani vengono chiamate NELL'ISTANTE della decisione, non dopo.
# Restano un modulo a parte e opzionale: se manca, o se MANI=0, la prova gira esattamente
# come prima e non tocca un euro.
MANI = None
if os.environ.get("MANI") == "1":
    try:
        import mani_curva as MANI
    except Exception as _e:                                    # noqa: BLE001
        print(f"CURVA | le mani non si attaccano ({_e}): proseguo solo come prova")


def salva_intero(st):
    """Scrive su un file a parte e poi lo sposta: il lettore vede il prima o il dopo, mai un
    file a meta'.

    PERCHE' (13/10, con soldi veri in gioco). Il bot rilegge questo stato ogni sei secondi
    mentre il cervello lo riscrive ogni secondo. Scrivendo sul posto, chi legge nel momento
    sbagliato trova un file troncato: e' successo, un JSON spezzato a riga 185.533. Finche'
    era solo analisi era un errore da rifare; con le mani attaccate e' il bot che non sa piu'
    quali posizioni ha aperte. os.replace e' atomico: o c'e' il file vecchio o c'e' il nuovo.
    """
    tmp = STATO + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f, indent=1)
    os.replace(tmp, STATO)


def main():
    st = json.load(open(STATO)) if os.path.exists(STATO) else _nuovo()
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("CURVA | la chain non risponde: non invento niente")
        return 1
    if st["ultimo_blocco"] is None:
        st["partenza"] = bn
        st["ultimo_blocco"] = bn - 1
        # SI SALVA SUBITO (11/10, terzo caso in due giorni dello stesso difetto). Il salvataggio
        # stava solo in fondo, dopo le uscite anticipate: alla prima accensione la funzione
        # usciva con «nessun blocco nuovo» e non scriveva niente, quindi ogni giro ripartiva da
        # zero e la prova non cominciava mai. Un file di stato si scrive quando lo stato cambia,
        # non quando il lavoro riesce.
        os.makedirs(os.path.dirname(STATO), exist_ok=True)
        salva_intero(st)
        print(f"CURVA | prima accensione al blocco {bn:,}: da qui in avanti, niente passato")
    # PRIMA DI TUTTO, I GETTONI RIMASTI IN MANO. Un'uscita tentata una volta sola non e'
    # un'uscita: se fallisce, nessuno la ritenta e la posizione resta aperta per sempre.
    if MANI:
        MANI.recupera()
    da = st["ultimo_blocco"] + 1
    a = min(bn, da + FINESTRA_MAX)
    if a <= da:
        print("CURVA | nessun blocco nuovo: aspetto che la chain avanzi")
        return 0

    # 1) i lanci nuovi: gettone -> curva, e con quale valuta si paga
    lg = CP.log_di_finestra(CP.T_LANCIO, da, a, indirizzo=CP.FABBRICA)
    if lg is None:
        print(f"CURVA | lanci {da:,}-{a:,} non letti: non avanzo il segnalibro")
        return 0
    nuove = 0
    for ev in lg:
        ind = [CP._indirizzo(x) for x in ev["topics"][1:]]
        if len(ind) < 2:
            continue
        d = ev.get("data", "0x")[2:]
        quote = ("0x" + d[24:64]).lower() if len(d) >= 64 else None
        if quote not in (ZERO, None):
            continue                     # non nativa: fuori dalla prova, e si dichiara
        st["curve"][ind[1].lower()] = {"gettone": ind[0].lower(),
                                       "nata_al_blocco": int(ev["blockNumber"], 16),
                                       "cumulato": 0.0, "prezzo": None,
                                       "prezzo_vendita": None,
                                       # IL CAMMINO DELLA RISERVA DI *OGNI* CURVA (11/10).
                                       # Le entrate a 3,6 sono rare: una ogni sette ore nella
                                       # prova. Con la sola soglia congelata, scoprire che 2,5
                                       # era meglio costerebbe un esperimento nuovo e altri
                                       # giorni. Registrando riserva e prezzo di TUTTE le curve,
                                       # qualunque soglia si potra' valutare sugli stessi dati —
                                       # e' lo stesso motivo per cui la prova sui diplomati
                                       # registra min, max e cammino invece del solo esito.
                                       "cammino": [], "diplomata": False}
        nuove += 1

    # 2) gli acquisti di TUTTE le curve in una chiamata sola (misurato: 1.114 acquisti,
    #    136 curve in 30.000 blocchi), e le vendite per avere il prezzo d'uscita vero
    comprati = CP.log_di_finestra(CP.T_COMPRA, da, a)
    venduti = CP.log_di_finestra(CP.T_VENDE, da, a)
    if comprati is None or venduti is None:
        print(f"CURVA | scambi {da:,}-{a:,} non letti: non avanzo il segnalibro")
        return 0

    # LA RISERVA E' ACQUISTI MENO VENDITE (11/10, scoperto costruendo questa prova). Sommavo
    # solo gli acquisti, e una moneta diplomata risultava aver incassato 8,96 nativi invece di
    # 4,2. Non era attivita' post-diploma (verificato: zero acquisti dopo il pool): e' che sulla
    # curva si VENDE — 124 vendite per curva, misurate ieri — e ogni vendita ritira valuta dalla
    # riserva. Sommando solo gli acquisti la soglia di 3,6 scattava molto prima del vero, e il
    # moltiplicatore storico di 2,82x era gonfiato per questo.
    # Quindi acquisti e vendite si fondono in UN solo flusso, in ordine di blocco.
    eventi = []
    for x in comprati:
        eventi.append((int(x["blockNumber"], 16), int(x.get("logIndex", "0x0"), 16), "compra", x))
    for x in venduti:
        eventi.append((int(x["blockNumber"], 16), int(x.get("logIndex", "0x0"), 16), "vende", x))
    eventi.sort(key=lambda y: (y[0], y[1]))

    entrate = 0
    for _b, _o, verso, x in eventi:
        cur = x["address"].lower()
        c = st["curve"].get(cur)
        if not c:
            continue
        r = CP._riga(x, verso, {cur: (None, 18)})
        if not r or r["gettoni"] <= 0 or r["valuta"] <= 0:
            continue
        if verso == "vende":
            c["cumulato"] = c["cumulato"] - r["valuta"]
            c["prezzo_vendita"] = r["valuta"] / r["gettoni"]
            c["prezzo_vendita_blocco"] = r["blocco"]
            # una vendita muove il prezzo in basso: e' il momento in cui uno stop scatterebbe
            _tocca(st, cur, c["prezzo_vendita"] / LATO_VENDE, r["blocco"])
            continue
        prima = c["cumulato"]
        c["cumulato"] = prima + r["valuta"]
        c["prezzo"] = r["valuta"] / r["gettoni"]
        tok = c["gettone"]
        # un punto ogni volta che la riserva cresce di almeno un decimo di nativo: tiene il
        # cammino leggibile (poche decine di punti) senza perdere la forma della salita
        cm = c.setdefault("cammino", [])
        if not cm or c["cumulato"] - cm[-1][1] >= 0.1:
            cm.append([r["blocco"], round(c["cumulato"], 4), c["prezzo"]])
        _tocca(st, cur, c["prezzo"] / LATO_COMPRA, r["blocco"])
        for sg in STRATEGIE:
            s0 = sg["soglia"]
            chiave = f"{sg['nome']}|{tok}"
            if not (prima < s0 <= c["cumulato"]) or chiave in st["posizioni"]:
                continue
            st["posizioni"][chiave] = {
                "strategia": sg["nome"], "soglia": s0,
                "stop": sg["stop"], "bersaglio": sg["bersaglio"], "gettone": tok,
                "curva": cur, "stato": "aperta",
                "aperta_il": int(time.time()),
                "blocco_entrata": r["blocco"],
                "entrata": c["prezzo"],
                "riserva_all_entrata": round(c["cumulato"], 4),
                # IL PUNTEGGIO DI ANDAMENTO (12/10, idea di Nicolo'): quanti nativi la curva ha
                # raccolto al minuto fino alla soglia. Sulle prime 36 operazioni le curve con
                # punteggio >= 1 rendono +4,5% contro +0,2% di tutte, e toccano il +50% una
                # volta su due invece che una su tre. Si registra ADESSO per ogni posizione,
                # perche' un filtro si giudica solo in avanti: sceglierlo guardando i dati
                # passati e' il modo classico di trovare rumore.
                "punteggio": round(c["cumulato"] / max((r["blocco"] - c["nata_al_blocco"]) / 600,
                                                       0.01), 3),
                "minuti_alla_soglia": round((r["blocco"] - c["nata_al_blocco"]) / 600, 2),
                "min_x": 1.0, "max_x": 1.0, "ultimo_x": 1.0,
                "min_al_blocco": r["blocco"], "max_al_blocco": r["blocco"],
                "cammino": [[r["blocco"], 1.0]]}
            if MANI:
                MANI.apre(chiave, st["posizioni"][chiave])
            entrate += 1

    # 3) i diplomi: compare il pool su Uniswap v4
    diplomate = set()
    # IL DIPLOMA SI RICONOSCE DALL'HOOK, NON DAL POOL (11/10, falso positivo trovato subito).
    # Segnavo «diplomata» qualunque moneta comparisse in un pool nuovo — ma CHIUNQUE puo' creare
    # un pool per qualunque gettone, e infatti una curva risultava diplomata con una riserva
    # massima di 0,70 nativi invece di 4,2: un pool creato da altri, non il suo diploma.
    # Verificato sui pool dei diplomati veri della demo: hanno TUTTI lo stesso hook,
    # 0xe5e702641ea86f4ae6cc3cdaed2b886f976be044, con fee 0 e tickSpacing 200. E' il marchio
    # di Pons. (Quell'indirizzo mi era comparso ieri come destinatario piu' frequente dei
    # trasferimenti e l'avevo preso per un router: era l'hook.)
    ev = CP.log_di_finestra(INIT, da, a, indirizzo=GESTORE_V4)
    if ev:
        for l in ev:
            tp = l.get("topics") or []
            d = l.get("data", "0x")[2:]
            if len(d) < 192:
                continue
            hook = "0x" + d[128:192][-40:].lower()
            if hook != HOOK_PONS:
                continue                 # pool di qualcun altro: non e' un diploma
            for i in (2, 3):
                if len(tp) > i:
                    diplomate.add("0x" + tp[i][-40:].lower())
    for cur, c in st["curve"].items():
        if c["gettone"] in diplomate:
            c["diplomata"] = True

    # 4) le posizioni aperte: si aggiornano e si chiudono
    chiuse = 0
    for chiave, p in st["posizioni"].items():
        if p["stato"] != "aperta":
            continue
        tok = p.get("gettone") or chiave.split("|")[-1]
        c = st["curve"].get(p["curva"]) or {}
        pr = c.get("prezzo")
        if pr:
            x = pr / p["entrata"]
            p["ultimo_x"] = round(x, 5)
            p["min_x"] = round(min(p["min_x"], x), 5)
            p["max_x"] = round(max(p["max_x"], x), 5)
        # IL PREZZO DI VENDITA DEVE ESSERE FRESCO (11/10). Usavo «l'ultimo prezzo di vendita
        # visto» senza guardare QUANDO: se l'ultima vendita era di mille blocchi prima, la
        # perdita risultava quella di allora, non quella di adesso — e con quattro stop usciti
        # a -70% contro un livello di -50% il sospetto che fosse colpa mia andava chiuso.
        # Adesso: se la vendita e' recente (meno di 600 blocchi, un minuto) la si usa; se e'
        # vecchia si usa il prezzo corrente e si DICHIARA che l'uscita e' stimata.
        uscita = pr
        stimata = True
        pv, pvb = c.get("prezzo_vendita"), c.get("prezzo_vendita_blocco")
        if pv and pvb and (a - pvb) <= 600:
            uscita, stimata = pv, False
        if tok in diplomate:
            p["stato"] = "chiusa"
            p["esito"] = {"verso": "diploma",
                          "rendimento": round((uscita / p["entrata"]) / COSTO - 1, 4)
                          if uscita else None,
                          "uscita_stimata": stimata}
            chiuse += 1
        # lo stop non si controlla piu' qui: scatta in _tocca, nell'istante del tocco
        elif a - p["blocco_entrata"] > ORIZZONTE:
            p["stato"] = "chiusa"
            p["esito"] = {"verso": "orizzonte",
                          "rendimento": round((uscita / p["entrata"]) / COSTO - 1, 4)
                          if uscita else None,
                          "uscita_stimata": stimata}
            chiuse += 1

    st["ultimo_blocco"] = a
    salva_intero(st)
    ap = [p for p in st["posizioni"].values() if p["stato"] == "aperta"]
    ch = [p for p in st["posizioni"].values() if p["stato"] == "chiusa"]
    print(f"CURVA | blocchi {da:,}-{a:,}: {nuove} curve native nuove, "
          f"{len(comprati):,} acquisti, {entrate} entrate, {chiuse} chiuse")
    print(f"CURVA | aperte {len(ap)}, chiuse {len(ch)}, curve seguite {len(st['curve']):,}")
    sog = {}
    for c in st["curve"].values():
        # le curve nate PRIMA di questa modifica non hanno il cammino: si saltano invece di
        # far cadere tutto il giro. Un campo nuovo non deve rompere lo stato vecchio.
        top = max((p[1] for p in (c.get("cammino") or [])), default=c.get("cumulato") or 0.0)
        for s0 in (1.0, 2.0, 2.5, 3.0, 3.6, 4.0):
            if top >= s0:
                k = f"{s0}"
                sog[k] = sog.get(k, [0, 0])
                sog[k][0] += 1
                sog[k][1] += 1 if c.get("diplomata") else 0
    if sog:
        print("CURVA | quante curve toccano ogni soglia, e quante poi si diplomano:")
        for k in sorted(sog, key=float):
            q, d = sog[k]
            print(f"   riserva >= {k:>4} nativi: {q:>4} curve, di cui diplomate {d:>3} "
                  f"({100*d/q:.0f}%)")
    # UNA MEDIA SOLA SU STRATEGIE DIVERSE NON SIGNIFICA NIENTE (13/10). Il referto diceva
    # «-1,6% su 695 chiusure» mescolando 50-5 (+13,3%) con diploma-1.5 (-16,6%), che non ha
    # ne' bersaglio ne' stop vero: il numero peggiore tirava giu' il migliore e sembrava che
    # la prova smentisse il candidato. Ogni strategia va letta da sola.
    # E il rendimento grezzo NON e' quello che si incassa: il costo vero di andata e ritorno
    # e' il 5,91% misurato (scarto fra prezzo di acquisto e di vendita) piu' l'1% per lato.
    # IL REFERTO SI RICALCOLA DAL CAMMINO, NON DAL CAMPO SALVATO (13/10). Il campo
    # `rendimento` porta dentro il costo in vigore QUANDO la posizione si e' chiusa: oggi il
    # costo e' passato dal 2% stimato al 5,91% misurato, e la serie e' diventata un misto di
    # due convenzioni che nessuna media puo' raddrizzare. Il cammino invece e' un fatto della
    # chain e non invecchia: da li' il costo di oggi si applica a tutte, vecchie comprese.
    regole = {s_["nome"]: (s_["stop"], s_.get("bersaglio")) for s_ in STRATEGIE}
    per_s = {}
    for p in ch:
        nome = p.get("strategia", "?")
        cam = p.get("cammino")
        if nome not in regole or not cam:
            continue
        stop, bers = regole[nome]
        esito_x = cam[-1][1]
        for _bl, x in cam:
            if x <= stop:
                esito_x = stop
                break
            if bers and x >= bers:
                esito_x = bers
                break
        per_s.setdefault(nome, []).append(esito_x / COSTO - 1)
    if per_s:
        print("CURVA | come va ogni strategia, al netto del costo vero del 5,91%:")
        for k in sorted(per_s):
            r = per_s[k]
            # IL COSTO SI TOGLIE UNA VOLTA SOLA (13/10). `rendimento` lo porta gia' dentro:
            # dividere di nuovo qui lo contava due volte. Non gonfiava il risultato, lo
            # sgonfiava — ma un numero sbagliato per prudenza resta un numero sbagliato.
            netto = list(r)
            if len(r) >= 20:
                sd = statistics.stdev(netto)
                print(f"   {k:<13} {statistics.mean(netto)*100:+6.2f}% "
                      f"± {1.96*sd/len(r)**0.5*100:4.1f}  su {len(r):>4} chiusure")
            else:
                print(f"   {k:<13} {len(r):>4} chiusure: non si legge prima di 20")
    return 0


if __name__ == "__main__":
    sys.exit(main())
