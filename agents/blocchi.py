# -*- coding: utf-8 -*-
"""I CINQUE BLOCCHI, con la percentuale CALCOLATA e non stimata.

Perche' esiste (4/11, chiesto da Nicolo'). Vuole a ogni giro una tabella
dei blocchi con quanto sono completi. Se quella percentuale la scrivessi a
sentimento sarebbe una mia opinione, e stanotte ho imparato a mie spese
cosa vale un indicatore che non misura: il numero di copertura contava gli
ordini "costruiti bene" invece di quelli che il pescatore accetta, e gli ho
dato numeri falsi per ore.

Quindi ogni blocco e' un INSIEME DI VERIFICHE del C-check, e la
percentuale e' quante di quelle sono verdi. Due conseguenze buone:
  - non posso gonfiarla;
  - un blocco che TORNA indietro si vede da solo, perche' una verifica
    nuova o un rosso nuovo abbassano la frazione senza che io intervenga.
Ed e' proprio quello che Nicolo' ha chiesto: arrivati al 100% non si
smette, si continua a guardare se un blocco scende.
"""
import json, os, sys, time
D = "data/liquidazioni"
# ogni blocco: (nome, [pezzi di testo che identificano le sue verifiche])
BLOCCHI = [
 ("1. Siamo vivi e armati", [
   "processo vivo", "ogni agente compila",
   # UNA PORTA MUTA NON E' UNA PORTA: sta nel blocco che dice se vediamo.
   "ogni porta dell'occhio consegna davvero",
   "piu' di un occhio arriva in tempo per la gara",
   "l'occhio sulla gara sta leggendo",
   "il secondo occhio e' acceso",
   "piu' di un fornitore ci serve il mempool",
   # UN CHECK TRONCATO NON E' UN CHECK AL 25%: MENTE SUL 75% RESTANTE.
   # Il 7/11 e' morto a meta' per un exit(1) di una dipendenza e per 1,6 ore
   # le ultime decine di verifiche non sono girate, con tutto verde. Se non
   # sappiamo se il check e' arrivato in fondo, non sappiamo se siamo armati:
   # questa chiave sta qui, nel blocco che risponde «siamo pronti».
   "il check e' arrivato alla fine",
   # "X: battito" esiste SOLO quando il file del battito manca: e' un nome
   # che nasce al fallimento. Senza questa chiave quella rottura non
   # appartiene a nessun blocco e non comparirebbe nella tabella -- un
   # guasto invisibile proprio nel pezzo che tiene in piedi tutto.
   "battito", "ha scritto da meno", "guardia di", "guardie attese", "guardie periodiche rispettano",
   "portafoglio operativo ha ETH", "basta per un colpo", "c'e' spazio per la base fee",
   "il contratto esiste", "chi comanda", "la cassa e'",
   # "ARMATI" VUOL DIRE POTER SPARARE, non avere i processi vivi: il 4/11
   # eravamo "armati" con tutti i verdi mentre la funzione che chiamavamo
   # non esisteva nel contratto distribuito.
   "il contratto in catena ha la funzione che chiamiamo",
   "la calldata usa un selettore che il contratto espone",
   "nessun ordine col selettore vecchio",
   "nessun ordine su una sede non provata",
   "dal prezzo che scende ai soldi in cassa",
   "nessun ordine cuce un indirizzo che non e' il nostro",
   "ARMATO", "ARMATA", "gettoni ammessi", "tutti i dati presenti", "la lista corta copre la popolazione in banda"]),
 ("2. Consegna: i pacchetti arrivano", [
   "relay Flashbots raggiungibile", "chiave di identita'",
   "il relay accetta la nostra firma", "pacchetti accettati", "i costruttori ci includono",
   "la nostra offerta sta sopra chi vince",
   # il controllo dei selettori ammessi appartiene qui: e' lo stadio in cui
   # la calldata deve corrispondere a cio' che il contratto espone.
   "nessun ordine con un selettore che il contratto non ha",
   "la sentinella compone", "la transazione si firma",
   "dentro c'e' l'offerta", "il pacchetto porta un'offerta",
   "portano l'offerta al costruttore",
   "la mancia e' una frazione sana", "la firma chi comanda", "va al nostro contratto"]),
 # BLOCCO RIDEFINITO il 7/11. Misurava «l'email parte», cioe' il canale piu'
 # fragile: dipende da Google e da una chiave in una cartella temporanea che
 # il sistema ripulisce. Ora misura la cosa che conta -- che una presa non
 # possa passare inosservata -- e l'email resta dentro come informativa.
 ("3. Avviso: Nicolo' lo sa", [
   "una presa non puo' passare inosservata",
   "chiave email", "Gmail accetta", "legge l'accredito",
   "non inventa accrediti", "chi scrive il flag della presa avvisa",
   "il messaggio si costruisce", "dice il premio", "non sembra una prova",
   "se la cifra e' il saldo", "nessuna presa bloccante",
   "tutti guardano lo stesso file"]),
 ("4. Dati in entrata: freschi e veri", [
   # LE TRE GUARDIE SULL'ETA' DEI FILE, aggiunte al blocco 4 il 6/11.
   # blocchi.py le segnalava come ORFANE, ed e' esattamente il segnale che
   # dice la regola: tre o piu' verifiche orfane sulla stessa cosa sono un
   # blocco che chiede di essere nominato. Qui il blocco esisteva gia' --
   # «dati in entrata: freschi e veri» -- e la freschezza dei file E' quel
   # blocco: la lista corta ferma 15 ore ci e' costata due liquidazioni.
   "lista_corta.json fresca", "vendite_pronte.json fresca",
   "composizione.json fresca",
   "prezzi freschi", "il giro dei prezzi batte", "li ha davvero rigenerati",
   "controllo sui valori dei prezzi", "nessun prezzo salta",
   "le coppie sono state rilette", "nessuna coppia letta male",
   "le letture della catena rispondono", "fuori-recinto",
   "scivolato dentro", "le letture vive rispondono",
   "finestra della testa", "senza salute nota",
   "in pericolo e' nella lista", "resta fuori lista",
   "le letture mute"]),
 ("5. Vendita: sappiamo liquidare", [
   "margine delle vendite inerte", "guardia in dollari attiva",
   "il percorso arriva a PRONTA", "usa l'ordine pronto",
   "la salute vera e' tornata", "i tetti distinguono",
   "i tetti sono stati rimisurati", "nessun tetto oltre", "sconfitta costosa",
   "le rotte sono misurate di recente",
   "esecuzione su copia della catena", "provata di recente",
   "rinviato, non fallito", "rinnovato nelle ultime due ore",
   "ordini che ci servono sono freschi", "le vendite si producono",
   "tetti sono misurati", "premio senza strada",
   "non spreca passate", "le rotte sono state misurate",
   "rotte cattive vengono rifiutate",
   "dump 5%", "dump 6%", "dump 9%", "ordini in cassetto",
   "il cassetto non e' crollato",
   # il premio vero: sta nel blocco della vendita perche' e' quello che
   # decide se una vendita conviene (4/11)
   "i premi sono letti dal protocollo", "i premi sono freschi",
   "il premio non e' lo stesso per tutti",
   "la soglia della resa dipende dalla garanzia", "sappiamo leggere Uniswap v4", "sappiamo comporre lo scambio su Uniswap v4", "il piano a due passaggi per v4 si costruisce", "il percorso v4 incassa", "il ponte v3+v4 verso GHO si costruisce", "nessuna coppia ha un tetto E il marchio", "il piano a tre passaggi e' provato"]),
 # BLOCCO 6, indicato dai revisori esterni il 4/11 e confermato dalla
 # misura: Flashbots non ha costruito NESSUNO dei 42 blocchi dove sono
 # avvenute le liquidazioni sopra i $500 in 30 giorni, e noi mandavamo
 # tutto solo a lui. Copertura di mercato prima: zero. Ora 93,2%.
 ("6. Spazio nel blocco: arriviamo a chi costruisce", [
   "eravamo pronti sulle occasioni che contano",
   "il contatore delle liquidazioni e' certificato",
   "le consulenze di oggi sono state lette",
   "sappiamo chi costruisce", "consegniamo a piu' di una porta",
   "la simulazione gira", "la simulazione vede quasi tutti", "porta solo chi e' alla portata",
   "sa di quale prezzo parla", "ogni sconfitta chiusa nomina la sua riparazione",
 "scarta gli aggiornamenti di altri asset",
   "usa la salute VIVA",
   "copriamo la gran parte del mercato", "le porte rispondono"]),
 # IL TABELLONE NON E' UN BLOCCO. Direttiva di Nicolo' (4/11 sera): i
 # blocchi sono CINQUE, e sono la macchina che incassa. Il tabellone e' il
 # GIUDICE: non gioca, guarda chi ha vinto e dice quale dei cinque non era
 # davvero al 100%. L'avevo messo come sesto blocco e competeva con gli
 # altri invece di giudicarli.
 # ------------------------------------------------------------------------
 # BLOCCO 6, NOMINATO IL 7/11. Nicolo' aveva detto che poteva esistere un
 # blocco non ancora considerato, e che il segnale sarebbero state le
 # verifiche orfane. Sono arrivate: due, entrambe sulla stessa cosa, e la
 # cosa non era coperta da nessuno dei cinque.
 # Il guasto che lo ha fatto nascere: la guardia che decide se sparare non
 # conosceva il prezzo del gas. Col gas di oggi un colpo costa 0,15 $ e non
 # si vedeva; ma i premi grossi arrivano in grappoli a 8-10 gwei, dove lo
 # stesso colpo costa 24,60 $, e una posizione da 2 $ di premio PASSAVA la
 # guardia perdendo 23 $. Con tutti e cinque i blocchi al 100%.
 # Cioe': si puo' essere vivi, armati, veloci, con i dati freschi e la
 # vendita pronta -- e perdere soldi a ogni colpo. Vincere non e' incassare.
 ("7. Conti: sappiamo se conviene sparare", [
   "la guardia conosce il costo del colpo",
   "il filtro per destinatario c'e'",
   "il consumo Alchemy e' sotto meta' del gratuito",
   "il conteggio distingue le occasioni dal traffico",
   "i due contatori concordano sulle transazioni",
   "sorvegliamo piu' largo di quanto spariamo",
   "guardia in dollari attiva",
   "margine delle vendite",
 ]),
]
# LE VERIFICHE DEL GIUDICE. Non appartengono a nessun blocco perche' il
# tabellone non e' un blocco: non gioca, giudica. Si dichiarano qui cosi'
# non vengono segnalate come "blocco non considerato".
COSTOSA = 1_000          # sopra questa cifra una sconfitta entra nel registro
# COLPA, in tabellone.py, e' un ELENCO di (motivo, blocco, perche'), non un
# dizionario. Lo interrogavo con .get e andava in errore -- e l'errore si e'
# rivelato solo il 5/11, alla PRIMA sconfitta costosa che e' entrata nel
# tabellone (quella da 1.005 $). Cioe': il meccanismo che assegna le colpe
# si rompeva esattamente nel momento in cui serviva, e fino a quel momento
# sembrava sano perche' non c'era niente da assegnare.
# Un ramo che gira una volta sola va provato con un caso finto, non
# aspettando il caso vero.
def _colpa_di(motivo):
    try:
        from tabellone import COLPA as _C
    except Exception:
        return 0
    m = (motivo or "")
    if isinstance(_C, dict):
        return _C.get(m, 0)
    for voce in _C:
        try:
            chiave, blocco = voce[0], voce[1]
        except Exception:
            continue
        if chiave and chiave in m:
            return blocco
    return 0


def ripara(chiave, verifica):
    """Dichiara riparata una sconfitta, NOMINANDO la verifica che la ripara.

    Si chiama a mano quando la riparazione e' fatta: e' il cancello della
    regola del 101% chiesta da Nicolo'. Senza nome di verifica la colpa
    resta, e il blocco resta basso.
    """
    f = f"{D}/sconfitte_aperte.json"
    reg = json.load(open(f))
    k = [x for x in reg if x.startswith(chiave[:20])]
    if not k:
        raise SystemExit(f"nessuna sconfitta che inizia per {chiave[:20]}")
    reg[k[0]]["riparato_da"] = verifica
    json.dump(reg, open(f, "w"), indent=1)
    print(f"{k[0]} riparata da: {verifica}")


DEL_GIUDICE = ["il tabellone e' stato letto", "ogni liquidazione ha il suo motivo",
               "ogni motivo da' la colpa a un blocco", "abbiamo studiato chi ha vinto",
               "motivo di sconfitta SCONOSCIUTO", "sconfitta costosa"]
def colpe_dal_tabellone():
    """Quanto premio ha perso ogni blocco, secondo il tabellone.

    E' il cuore dell'architettura chiesta da Nicolo' (4/11): il blocco 6
    non compete con gli altri cinque, DA' LA COLPA agli altri cinque. Una
    colpa scritta e non contata e' un appunto; una colpa che ABBASSA il
    blocco e' un sistema che si corregge.
    Quanto pesa: una sconfitta attribuita a un blocco gli toglie un punto
    di percentuale ogni 50.000 dollari persi, fino a 25 punti. Non di piu',
    perche' un blocco non deve andare a zero per una sola partita persa --
    deve diventare il piu' basso della tabella, cioe' il primo da guardare.
    """
    # LA COLPA NON SCADE COL TEMPO (riparato il 4/11 sera).
    # Difetto trovato da solo: la colpa veniva riletta ogni volta dalla
    # finestra corrente del tabellone, quindi il blocco 4 e' risalito da
    # 82% a 100% non perche' l'avessimo riparato, ma perche' la sconfitta
    # da $947.639 era uscita dalla finestra. Una colpa che evapora col
    # tempo e' una colpa che non insegna niente -- ed e' l'opposto della
    # regola di Nicolo': il blocco scende quando perdiamo e risale SOLO
    # quando si aggiunge la verifica che impedisce di riperderlo.
    # Qui le sconfitte costose si scrivono in un registro permanente e
    # pesano finche' qualcuno non le dichiara riparate NOMINANDO la verifica
    # che le ripara.
    try: tb = json.load(open(f"{D}/tabellone.json"))
    except Exception: tb = {}
    try: reg = json.load(open(f"{D}/sconfitte_aperte.json"))
    except Exception: reg = {}
    nuove = False
    for r in (tb.get("liquidazioni") or []):
        premio = r.get("premio_vero_usd") or 0
        if premio < COSTOSA or (r.get("nostra") or r.get("presa_da_noi")):
            continue
        k = (r.get("tx") or "")[:20]
        if not k or k in reg:
            continue
        reg[k] = {"quando": tb.get("quando"), "premio": premio,
                  "blocco": _colpa_di(r.get("motivo", "")),
                  "motivo": r.get("motivo", ""), "riparato_da": None}
        nuove = True
    if nuove:
        try:
            _t = f"{D}/sconfitte_aperte.json.tmp"
            json.dump(reg, open(_t, "w"), indent=1)
            os.replace(_t, f"{D}/sconfitte_aperte.json")
        except Exception: pass
    out = {}
    aperte = {}
    for k, c in reg.items():
        if c.get("riparato_da"):
            continue
        b = c.get("blocco") or 0
        if not b: continue
        aperte.setdefault(b, []).append(c)
    for b, cs in aperte.items():
        persi = sum(c.get("premio", 0) for c in cs)
        out[b] = {"premio_perso": persi,
                  "punti": min(25, int(persi//50_000)),
                  "perche": "; ".join(sorted({c.get("motivo","") for c in cs}))}
    return out
def calcola():
    ch = json.load(open(f"{D}/check_finale.json"))
    esiti = ch["esiti"]
    usate, righe = set(), []
    colpe = colpe_dal_tabellone()
    for nome, chiavi in BLOCCHI:
        miei = [e for e in esiti if any(k in e["che"] for k in chiavi)]
        for e in miei: usate.add(e["che"])
        n = len(miei); ok = sum(1 for e in miei if e["ok"])
        pct = (100*ok//n) if n else 0
        rossi = [e["che"] for e in miei if not e["ok"]]
        # la colpa dal tabellone abbassa il blocco
        numero = int(nome.split(".")[0])
        colpa = colpe.get(numero)
        pct_finale = pct
        if colpa and colpa["punti"]:
            pct_finale = max(0, pct - colpa["punti"])
        righe.append({"blocco": nome, "verifiche": n, "verdi": ok,
                      "percento": pct_finale, "percento_verifiche": pct,
                      "colpa_dal_tabellone": colpa, "rossi": rossi})
    fuori = [e["che"] for e in esiti if e["che"] not in usate
             and not any(k in e["che"] for k in DEL_GIUDICE)]
    return righe, fuori, ch.get("quando")
def main():
    righe, fuori, quando = calcola()
    prima = {}
    try:
        prima = {r["blocco"]: r["percento"]
                 for r in json.load(open(f"{D}/blocchi.json"))["righe"]}
    except Exception: pass
    print(f"\n   {'blocco':38s} {'completo':>9s}  {'verifiche':>10s}  andamento")
    for r in righe:
        p0 = prima.get(r["blocco"])
        freccia = ""
        if p0 is not None:
            if r["percento"] > p0: freccia = f"su da {p0}%"
            elif r["percento"] < p0: freccia = f"GIU' da {p0}%  <<< tornato indietro"
            else: freccia = "stabile"
        print(f"   {r['blocco']:38s} {r['percento']:8d}%  "
              f"{r['verdi']:4d}/{r['verifiche']:<5d}  {freccia}")
        for x in r["rossi"]: print(f"      rosso: {x}")
        c = r.get("colpa_dal_tabellone")
        if c and c["punti"]:
            print(f"      COLPA DAL TABELLONE: -{c['punti']} punti "
                  f"(${c['premio_perso']:,.0f} persi) — {c['perche']}")
    # LE VERIFICHE SENZA BLOCCO SONO IL SEGNALE DI UN BLOCCO CHE NON
    # ABBIAMO CONSIDERATO. Direttiva di Nicolo' (4/11): i cinque blocchi
    # non sono una lista da finire, sono la macchina da tenere in piedi, e
    # puo' esistere un sesto blocco che non abbiamo ancora nominato --
    # anche senza aver mai preso una posizione.
    # Il modo di accorgersene senza sperarci: ogni verifica nuova che il
    # C-check aggiunge DEVE entrare in un blocco. Se non entra, o il blocco
    # va allargato, o ne manca uno. Tre o piu' verifiche orfane sulla
    # stessa cosa sono un blocco nuovo che chiede di essere nominato.
    if fuori:
        print(f"\n   !!! {len(fuori)} verifiche non appartengono a nessun blocco.")
        print(f"   Questo e' il segnale di un BLOCCO NON CONSIDERATO:")
        for x in fuori: print(f"      - {x}")
        print(f"   Da decidere: allargare un blocco esistente, o nominarne uno nuovo.")
    tutti100 = all(r["percento"] == 100 for r in righe)
    scesi = [r["blocco"] for r in righe
             if prima.get(r["blocco"]) is not None
             and r["percento"] < prima[r["blocco"]]]
    print()
    if tutti100 and not fuori:
        print("   LA MACCHINA E' AL 100% SU TUTTI I BLOCCHI. "
              "Non si smette: si continua a guardare se scende.")
    elif scesi:
        print(f"   UN BLOCCO E' TORNATO INDIETRO: {', '.join(scesi)}")
    else:
        aperti = [f"{r['blocco'].split('.')[0]} al {r['percento']}%"
                  for r in righe if r["percento"] < 100]
        print(f"   ancora da chiudere: {', '.join(aperti)}")
    # LA STORIA DELLE PERCENTUALI. Serve per rispondere alla domanda che
    # Nicolo' ha messo al centro (4/11 sera): "quando abbiamo perso, i
    # cinque blocchi erano al 100%?" Senza la storia la risposta e' una
    # ricostruzione a memoria; con la storia e' un fatto.
    try: storia = json.load(open(f"{D}/storia_blocchi.json"))
    except Exception: storia = {"punti": []}
    storia["punti"] = (storia.get("punti") or [])[-400:] + [{
        "quando": time.time(),
        "percentuali": {r["blocco"].split(".")[0]: r["percento"] for r in righe}}]
    json.dump(storia, open(f"{D}/storia_blocchi.json", "w"))
    json.dump({"quando": time.time(), "righe": righe, "non_assegnate": fuori,
               "tutti_al_100": tutti100, "tornati_indietro": scesi},
              open(f"{D}/blocchi.json", "w"), indent=1)
    return 0
if __name__ == "__main__":
    sys.exit(main())
