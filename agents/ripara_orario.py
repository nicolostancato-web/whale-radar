"""RIPARA ORARIO — rimette l'istante vero nei record scritti col riferimento che invecchiava.

PERCHE' (16/09, secondo rilievo della revisione esterna). Stamattina ho riparato CHI produce
l'orario e ho scritto un documento sul difetto. Il revisore ha fatto notare la cosa ovvia che non
avevo visto: **documentare un difetto non e' ripararlo**. I record gia' scritti hanno ancora il
`ts` sbagliato fino a 32 minuti, e con quel `ts` hanno gia' deciso la propria `classe`, sono gia'
entrati in unioni e hanno gia' superato o mancato l'embargo.
«Errore 0 secondi» vale solo da stamattina in avanti. Il passato resta sporco finche' non lo si
pulisce o non lo si butta.

PERCHE' SI PUO' FARE. Il campo `blocco` e' esatto — viene dalla catena, non da un calcolo — quindi
l'istante vero e' sempre recuperabile. E il nodo accetta le chiamate in LOTTO: 25 blocchi in 0,4
secondi, sessanta volte piu' veloce che uno per volta. Una bonifica che sarebbe stata impraticabile
costa ore invece di settimane.

COSA FA, esattamente:
  - per ogni pool, legge i record e raccoglie i blocchi distinti;
  - chiede alla catena gli istanti veri, in lotti;
  - riscrive `ts` con quello vero, e RICALCOLA `ritardo` e `classe` di conseguenza;
  - lascia intatti blocco, tx, li, bh, acq e le quantita', che erano gia' giusti;
  - scrive quanti record ha corretto e di quanto, cosi' la bonifica stessa e' verificabile.

I record di cui la catena non sa dire l'istante NON vengono indovinati: restano com'erano e vengono
contati a parte. Un dato che non si riesce a ripristinare va dichiarato, non inventato una seconda
volta.
"""
import gzip
import hashlib
import json
import os
import time
import urllib.request

# QUANTI BLOCCHI PER LOTTO, MISURATO (16/09, seconda misura). Stamattina base aveva
# rifiutato un lotto da 25 e ne avevo concluso «base non fa i lotti»: una conclusione
# affrettata da UN solo tentativo, che e' costata dieci volte la velocita'.
# Riprovato per gradi: 2 -> ok, 5 -> ok, 10 -> ok in 2,1s, 25 -> rifiuta (-32014).
# Il limite non e' «niente lotti», e' «lotti fino a dieci». Una domanda fatta una volta
# sola da una risposta sola, non una regola.
RPC = {"base": ("https://mainnet.base.org", 10),
       "robinhood": ("https://rpc.mainnet.chain.robinhood.com", 100)}
CHAIN = os.environ.get("CHAIN", "robinhood")
BUDGET = int(os.environ.get("BUDGET_SEC", 400))
MARCHIO_SOSPETTO = 1789986813   # 21/09 10:33 UTC: prima di qui il marchio della coda viva mentiva
# LA GUARDIA DEI CALDI SI RESTRINGE, PERCHE' ORA LA SCRITTURA E' SICURA (22/09).
# Era a due ore per non calpestare i raccoglitori. Ma i pool piu' attivi non sono mai freddi due
# ore di fila, quindi non potevano piu' essere riparati: 463 marchi sbagliati su 464 di base e
# 1.430 su 1.441 di robinhood erano bloccati li' dentro, e l'esame non sarebbe mai potuto passare.
# Adesso la scrittura rilegge e riunisce cio' che e' comparso nel frattempo (vedi
# `scrivi_unendo`), quindi la finestra di rischio non e' piu' l'intera lavorazione ma solo
# l'istante fra la rilettura e la sostituzione. Due minuti bastano a non litigare sul medesimo
# file, senza vietare il lavoro.
FREDDO = int(os.environ.get("FREDDO_SEC", 120))   # due minuti: il tempo di non litigare sul file
SOGLIA_PIT = int(os.environ.get("SOGLIA_PIT", 900))
# IL LAVORO SI DIVIDE, MA IL SEGNALIBRO NO (21/09). Con un solo operaio robinhood avanzava di
# mezzo punto ogni giro da mezz'ora: giorni per finire, e la verifica degli istanti e' la
# condizione che tiene fermo il loop 1.
# Ogni scheggia prende i file il cui nome le tocca per resto: insiemi DISGIUNTI, nessuno tocca il
# file di un altro. La divisione sta nel NOME, non nella posizione nell'elenco, perche' l'elenco
# cambia mentre i raccoglitori scrivono e le schegge si sovrapporrebbero.
# Il segnalibro invece: si LEGGE quello comune (cosi' nessuna scheggia riapre il lavoro gia' fatto
# dalle corse di prima) e si SCRIVE solo il proprio. Due schegge che scrivono lo stesso segnalibro
# se lo cancellano a vicenda — con «-X ours» vince l'ultimo che spinge, e il lavoro dell'altro
# sparisce. E' lo stesso difetto che il 20/09 ha fatto tornare indietro il conto da 9.153 a 2.000.
SCHEGGIA = int(os.environ.get("SCHEGGIA", 0))
QUANTE = max(1, int(os.environ.get("QUANTE", 1)))
CK_COMUNE = f"data/multichain/{CHAIN}/riparazione_ckpt.json"
CK = (CK_COMUNE if QUANTE == 1
      else f"data/multichain/{CHAIN}/riparazione_ckpt_{SCHEGGIA}.json")


# UN TIMBRO MESSO CON IL METODO SBAGLIATO NON VALE (22/09).
# Fino alle 02:35 UTC del 22/09 il riparatore abbinava le risposte del nodo ai blocchi per
# POSIZIONE invece che per numero. Su base, il cui nodo tronca i gruppi, questo produceva orari
# scambiati fra blocchi diversi — e il record risultava «verificato» lo stesso.
# Quindi i timbri messi prima di quel momento non provano niente, e vanno rifatti.
#
# MA SOLO DOVE IL DIFETTO SI E' MANIFESTATO, e questo l'ho MISURATO invece di deciderlo:
#   base:      1 record sbagliato su 45 col timbro (errore di 3.176 secondi)
#   robinhood: 120 record su 120 CORRETTI, controllati uno per uno contro la catena
# Il nodo di robinhood non tronca, quindi l'abbinamento per posizione dava comunque il risultato
# giusto. Invalidare anche li' costerebbe ore di lavoro per correggere un errore che le misure
# dicono non esistere. Se un giorno emergesse un controesempio su robinhood, questa riga cambia.
VERIFICA_VALIDA_DA = {"base": 1790041500}.get(CHAIN, 0)   # 22/09 02:35 UTC


def timbrato(r):
    """Il record porta un timbro di verifica ANCORA VALIDO?"""
    v = r.get("ver")
    return bool(v) and v >= VERIFICA_VALIDA_DA


def misura_file(p):
    """La dimensione del file quando lo dichiariamo finito.

    UN FILE FINITO PUO' CRESCERE (21/09, notte). La riparazione marcava un file come completo, e
    subito dopo i raccoglitori ci aggiungevano righe nuove — non verificate. Quel file non veniva
    piu' riaperto, perche' il segnalibro diceva che era a posto, e il controllo che avrebbe dovuto
    riaprirlo leggeva SOLO LA PRIMA RIGA: vecchia e verificata.
    Non e' una corsa sfortunata, e' cosi' per costruzione: piu' raccogliamo, piu' si accumula
    lavoro invisibile. Misurato stanotte: 3.562 record su base e 20.224 su robinhood, tutti
    riparabili, tutti dentro file dichiarati a posto.
    La dimensione e' un testimone economico: se il file e' cresciuto, dentro c'e' roba nuova."""
    try:
        return os.path.getsize(p)
    except Exception:
        return -1


def scrivi_unendo(p, righe):
    """Scrive il file riunendo cio' che nel frattempo e' stato aggiunto da altri.

    LA GUARDIA DEI FILE CALDI ERA DIVENTATA UN MURO (22/09). La riparazione non toccava i file
    scritti nelle ultime due ore, per non cancellare il lavoro dei raccoglitori. Giusto come
    intenzione — ma i pool piu' attivi ricevono scambi in continuazione, quindi restano caldi per
    sempre e NON POTEVANO PIU' ESSERE RIPARATI.
    Misurato: dei marchi sbagliati rimasti, 463 su 464 di base e 1.430 su 1.441 di robinhood erano
    li' dentro. Quella condizione dell'esame non sarebbe mai potuta scendere sotto lo 0,9%, non
    perche' il lavoro mancasse, ma perche' il lavoro era vietato.
    La risposta giusta non e' allentare la soglia — e' togliere la ragione per cui esiste.
    Qui si rilegge il file un istante prima di sostituirlo e si tengono le righe che nel frattempo
    sono comparse: se un raccoglitore ha scritto mentre riparavamo, il suo lavoro resta.
    La finestra di rischio passa da due ore al tempo fra questa rilettura e la sostituzione."""
    def _chiave(r):
        return (r.get("tx"), r.get("li"), r.get("blocco"))
    mie = {_chiave(r) for r in righe}
    aggiunte = 0
    try:
        for l in gzip.open(p, "rt"):
            if not l.strip():
                continue
            d = json.loads(l)
            if _chiave(d) not in mie:
                righe.append(d)
                mie.add(_chiave(d))
                aggiunte += 1
    except Exception:
        # NON SI SCRIVE SU CIO' CHE NON SI RIESCE A RILEGGERE. Sostituire un file che non sappiamo
        # leggere significa poter cancellare righe che non abbiamo visto.
        return False, 0
    tmp = p + ".tmp"
    try:
        with gzip.open(tmp, "wt") as fo:
            for r in sorted(righe, key=lambda x: (x.get("blocco", 0), x.get("li", 0))):
                fo.write(json.dumps(r) + "\n")
        os.replace(tmp, p)
    except Exception:
        return False, 0
    return True, aggiunte


def finito(righe):
    """Vero solo se non resta un solo record verificabile senza verifica.

    SI MARCA FINITO CIO' CHE E' FINITO (21/09). Il file veniva aggiunto all'elenco dei fatti in
    QUATTRO punti diversi, e nessuno dei quattro controllava che dentro non fosse rimasto niente.
    Misurato: il 37% dei file di robinhood DICHIARATI FATTI aveva ancora record non verificati —
    43.125 record nel solo campione. Un esempio: 100 record scoperti su 300, file marcato a posto.
    Una dichiarazione di completamento che nessuno verifica e' la forma piu' pura del difetto che
    ci perseguita da una settimana: «non ho finito» diventa indistinguibile da «ho finito».
    Adesso la domanda si fa al DATO, non al percorso di codice che ci ha portati fin qui."""
    # VERIFICATO VUOL DIRE CHE PORTA LA DATA DELLA VERIFICA (22/09).
    # Finora bastava l'etichetta «orario: catena». Ma quell'etichetta la scriveva anche il codice
    # vecchio che interpolava, quindi non distingue «chiesto alla catena» da «etichettato e
    # basta». Misurato con codice indipendente: il 17% dei record di base era sbagliato PUR
    # portando l'etichetta, e il 73% dei record porta un'etichetta che non possiamo verificare.
    # Da qui la regola: fa fede solo `ver`, che viene scritto nel momento in cui l'orario e' stato
    # davvero chiesto al nodo. Questo fara' crollare le percentuali — ed e' giusto cosi': e' la
    # prima volta che dicono una cosa dimostrabile invece di una cosa dichiarata.
    if any(not timbrato(r) and r.get("blocco") for r in righe):
        return False
    # UN MARCHIO SOSPETTO E' LAVORO RIMASTO, NON LAVORO FATTO (21/09, notte).
    # I record marchiati per errore il 20/09 HANNO il marchio «catena» — sbagliato, ma ce l'hanno.
    # Quindi il file risultava completo e non veniva mai riaperto, e quella condizione dell'esame
    # (marchi sospetti sotto lo 0,5%) non sarebbe MAI potuta scendere: misurata ferma al 3,9% su
    # base e al 6,0% su robinhood mentre tutto il resto correva.
    # Il sospetto si riconosce cosi': marchiato «catena», classificato point-in-time, raccolto
    # PRIMA che la correzione esistesse, e senza la data della verifica. Non poteva essere stato
    # verificato da un codice che ancora non c'era.
    return not any(r.get("orario") == "catena" and r.get("classe") == "point-in-time"
                   and not r.get("ver") and (r.get("acq") or 0) < MARCHIO_SOSPETTO
                   for r in righe)
def mia(nome):
    """Vero se questo file tocca a me. Dal nome, non dalla posizione: stabile fra un giro e l'altro."""
    if QUANTE == 1:
        return True
    return int(hashlib.md5(nome.encode()).hexdigest()[:8], 16) % QUANTE == SCHEGGIA
t0 = time.time()


def istanti(url, blocchi, per_lotto):
    """Gli istanti veri, a lotti se il nodo li accetta."""
    _LOTTO_PIENO = per_lotto
    out = {}
    falliti = set()
    i = 0
    while i < len(blocchi):
        if time.time() - t0 > BUDGET:
            break          # l'orologio comanda anche qui dentro (21/09)
        gruppo = blocchi[i:i + per_lotto]
        if per_lotto > 1:
            req = [{"jsonrpc": "2.0", "method": "eth_getBlockByNumber",
                    "params": [hex(b), False], "id": k} for k, b in enumerate(gruppo)]
        else:
            req = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber",
                   "params": [hex(gruppo[0]), False], "id": 0}
        try:
            r = urllib.request.Request(url, data=json.dumps(req).encode(),
                                       headers={"Content-Type": "application/json",
                                                "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=90) as x:
                d = json.load(x)
        except Exception:
            # NON PROVATO NON E' IRRECUPERABILE (16/09). Un lotto che fallisce — timeout, 429,
            # nodo occupato — faceva saltare i suoi blocchi, e i record relativi finivano contati
            # come «irrecuperabili»: 3.162 su un giro solo, un numero che dice «questi dati sono
            # perduti» quando la verita' e' «non ho insistito».
            # E' lo stesso errore che avevo gia' corretto nel controllo di canonicita' stamattina.
            # Farlo due volte in un giorno vuol dire che non era una disattenzione: e' un riflesso,
            # e va tolto ovunque. Qui si riprova, si stringe il lotto, e si rinuncia solo dopo.
            if per_lotto > 1:
                per_lotto = max(1, per_lotto // 4)
                time.sleep(4)
                continue                      # stesso gruppo, lotti piu' piccoli
            tentato_uno = out.get(gruppo[0])
            if tentato_uno is None and gruppo[0] not in falliti:
                falliti.add(gruppo[0])
                time.sleep(4)
                continue                      # una seconda possibilita', poi basta
            i += per_lotto
            continue
        # SI ABBINA AL FATTO, NON ALL'ETICHETTA CHE ABBIAMO ATTACCATO NOI (22/09).
        # Qui la risposta veniva assegnata al blocco in base alla POSIZIONE nella richiesta (`id`),
        # un numero che scriviamo noi. Ma il nodo di base tronca e riordina: chiesti venti blocchi,
        # ne torna tre. Quando le posizioni non corrispondono piu', ogni blocco riceve l'orario di
        # un ALTRO blocco — e il record risulta «verificato», perche' formalmente l'orario l'abbiamo
        # chiesto davvero.
        # Misurato con codice indipendente: su base il 17% dei record aveva l'istante sbagliato di
        # decine di minuti, e l'errore sopravviveva alla verifica. Su robinhood, che non tronca,
        # zero. Lo scavo storico faceva gia' la cosa giusta — abbinava al numero di blocco dentro
        # la risposta — ed e' il motivo per cui li' il difetto non si vedeva.
        # La risposta dice DA SOLA a quale blocco appartiene. Fidarsi di quello e non della nostra
        # numerazione e' la stessa disciplina di tutta la giornata: guardare il dato, non
        # l'etichetta che gli abbiamo messo sopra.
        items = d if isinstance(d, list) else [d]
        chiesti = set(gruppo)
        for item in items:
            if not isinstance(item, dict):
                continue
            res = item.get("result")
            if not (res and res.get("timestamp") and res.get("number")):
                continue
            b_vero = int(res["number"], 16)
            if b_vero in chiesti:               # e solo se e' uno di quelli che avevamo chiesto
                out[b_vero] = int(res["timestamp"], 16)
        # IL LOTTO TORNA A CRESCERE (22/09). Dopo un rifiuto il gruppo veniva ridotto a un quarto
        # e restava piccolo per TUTTO il resto del giro: un intoppo di un istante costava ore di
        # lentezza. Misurato su base: 18.867 record dichiarati irrecuperabili in un giro, mentre il
        # nodo — riprovato subito dopo — serviva benissimo gruppi da dieci.
        # Un rallentamento deve durare quanto il motivo che l'ha causato, non fino a fine giornata.
        if per_lotto < _LOTTO_PIENO:
            per_lotto = min(_LOTTO_PIENO, per_lotto * 2)
        i += per_lotto
        time.sleep(0.2)
    return out


# MEMORIA DEI BLOCCHI GIA' CHIESTI (21/09). Il nodo di robinhood e' saturo con cinque operai —
# misurati 42 segnali di limite in un giro solo — quindi la spinta non puo' venire da piu' operai:
# aggiungerne rallenta, perche' il limite e' GLOBALE e non per operaio (gia' misurato: tre
# schegge rendevano piu' di sei).
# La spinta viene dal non chiedere due volte la stessa cosa. Pool diversi condividono blocchi: il
# 19% delle richieste su robinhood e il 29% su base sono ripetizioni. E conta ancora di piu' ora
# che il segnalibro e' stato buttato e i quindicimila file verranno risondati tutti.
#
# LA MEMORIA NON STA NEL REPO. Un file riscritto ogni mezz'ora sarebbe un blob nuovo ogni volta —
# i .gz non hanno delta — e gonfierebbe la cronologia di decine di mega al giorno. E' il problema
# che il 20/09 ha portato il repo a 3.162 MB. Sta nella cache di GitHub, che serve a questo.
MEMORIA = os.environ.get("MEMORIA_ORARI", f".cache_orari/{CHAIN}.json")
_memoria = {}
try:
    with open(MEMORIA) as _mf:
        _memoria = {int(k): v for k, v in json.load(_mf).items()}
except Exception:
    _memoria = {}
_da_memoria = 0


def istanti_con_memoria(url, blocchi, per_lotto):
    """Come istanti(), ma chiede al nodo solo i blocchi che non conosce gia'."""
    global _da_memoria
    noti = {b: _memoria[b] for b in blocchi if b in _memoria}
    _da_memoria += len(noti)
    restanti = [b for b in blocchi if b not in _memoria]
    if restanti:
        freschi = istanti(url, restanti, per_lotto)
        for b, v in (freschi or {}).items():
            if v is not None:
                _memoria[b] = v
        noti.update(freschi or {})
    return noti


def salva_memoria():
    try:
        os.makedirs(os.path.dirname(MEMORIA) or ".", exist_ok=True)
        with open(MEMORIA, "w") as mf:
            json.dump({str(k): v for k, v in _memoria.items()}, mf)
    except Exception as e:
        print(f"RIPARA | memoria dei blocchi non salvata ({type(e).__name__}): "
              f"il prossimo giro rifara' le stesse domande.", flush=True)


def main():
    url, per_lotto = RPC.get(CHAIN, (None, None))
    if not url:
        print(f"RIPARA | {CHAIN}: nessun nodo", flush=True)
        return
    # SI GUARDANO TUTTE E DUE LE CARTELLE (20/09). Questa riparazione era nata il 16/09 per il
    # difetto della CODA VIVA, che scrive in `vivo`, e guardava solo li'. Oggi ho trovato lo stesso
    # difetto — istanti interpolati invece che chiesti — nello SCAVO STORICO, che scrive in
    # `storico`: una cartella che questo agente non ha mai aperto.
    # Il sintomo era perfetto nel suo inganno: l'agente riapriva undicimila file, ne processava
    # ZERO e usciva in 68 secondi dichiarando «tutto a posto». Non mentiva sul suo lavoro — in
    # `vivo` non c'era davvero niente da fare, perche' la coda viva e' corretta dal 16/09. Stava
    # solo guardando dalla parte sbagliata, e nessuno dei suoi numeri poteva dirlo.
    # Misurato in `storico`: righe vecchie sbagliate di 7.510 secondi mediani.
    cartelle = [f"data/multichain/{CHAIN}/storico", f"data/multichain/{CHAIN}/vivo"]
    d = cartelle[0]
    if not os.path.isdir(d):
        print(f"RIPARA | {CHAIN}: niente da riparare", flush=True)
        return
    ck = {}
    if os.path.exists(CK):
        try:
            ck = json.load(open(CK))
        except Exception:
            ck = {}
    # UN SEGNALIBRO COSTRUITO CON LA REGOLA SBAGLIATA NON VALE (21/09). Fino ad ora «fatto»
    # voleva dire «ha `ritardo`», che non e' cio' che misuriamo. Tenerlo significherebbe non
    # riaprire mai i file gia' archiviati con quella regola — e sono quindicimila.
    # Il controllo che riapriva i file guardava SOLO LA PRIMA RIGA: se la prima e' a posto e la
    # duecentesima no, il file restava marcato fatto per sempre. Riesaminarli costa poco, perche'
    # la sonda a tre campioni scarta in fretta quelli gia' sani.
    # VERSIONE 3: la 2 svuotava il segnalibro, ma i file venivano RIMARCATI finiti senza che
    # nessuno guardasse dentro. Svuotarlo di nuovo da solo servirebbe a poco: quello che conta e'
    # l'invariante in `finito()`, che impedisce di rifare lo stesso errore.
    # VERSIONE 4: il segnalibro non e' piu' un elenco di nomi ma una mappa nome -> dimensione del
    # file quando l'abbiamo dichiarato finito. Serve perche' un file finito PUO' CRESCERE: i
    # raccoglitori ci aggiungono righe nuove non verificate, e col vecchio formato quel file non
    # tornava mai in coda.
    # VERSIONE 5: «finito» adesso comprende anche «non ha marchi sospetti da riverificare».
    # VERSIONE 6: la 5 era corretta ma non entrava mai in vigore, perche' al salvataggio il
    # segnalibro vecchio veniva riletto dal disco e rimesso dentro. Serve un giro di invalidazione
    # che questa volta regge.
    # VERSIONE 7: la chiave del segnalibro comprende la cartella. Le chiavi vecchie, fatte col
    # solo nome, non possono distinguere le due copie e vanno buttate.
    # VERSIONE 8: via la sonda a campione. Tutto cio' che era stato marcato da lei va riesaminato.
    # VERSIONE 9: verificato = porta `ver`. Tutto cio' che era solo etichettato torna in coda.
    # VERSIONE 10: su base i timbri anteriori alla correzione dell'abbinamento non valgono piu'.
    VERSIONE_LOGICA = 10
    if ck.get("versione") != VERSIONE_LOGICA:
        print(f"RIPARA | {CHAIN}: il segnalibro e' della regola vecchia "
              f"({len(ck.get('fatti', []))} file): LO BUTTO e riesamino tutto.", flush=True)
        ck["fatti"] = {}
        ck["versione"] = VERSIONE_LOGICA
    _f = ck.get("fatti") or {}
    fatti = dict(_f) if isinstance(_f, dict) else {}
    # ANCHE IL SEGNALIBRO COMUNE HA UNA VERSIONE (21/09, notte). Invalidavo solo quello della
    # scheggia; il comune veniva riunito SENZA controllare la versione, e cosi' 26.618 file
    # dichiarati finiti dalla logica vecchia rientravano intatti a ogni giro.
    # Effetto misurato: la riparazione riparava 0-1 pool per operaio per giro e il numero degli
    # istanti stava fermo, mentre il 24% dei record freddi era ancora da verificare — tutti dentro
    # file che il comune continuava a dichiarare a posto.
    # Base non aveva il problema perche' lavora con un operaio solo: li' il comune E' il proprio,
    # e si era invalidato da se'. Un difetto che colpisce una chain sola e' il piu' difficile da
    # vedere, perche' l'altra continua a dire che il codice funziona.
    if QUANTE > 1 and os.path.exists(CK_COMUNE):
        try:
            _com = json.load(open(CK_COMUNE))
            if _com.get("versione") == VERSIONE_LOGICA:
                _cf = _com.get("fatti") or {}
                if isinstance(_cf, dict):
                    for _k, _v in _cf.items():
                        fatti.setdefault(_k, _v)
            else:
                print(f"RIPARA | {CHAIN}: il segnalibro COMUNE e' della regola vecchia "
                      f"(versione {_com.get('versione')}, {len(_com.get('fatti', []))} file): "
                      f"lo IGNORO.", flush=True)
        except Exception:
            pass
    # UN FILE FINITO CHE E' CRESCIUTO NON E' PIU' FINITO (21/09, notte).
    # Prima qui si leggeva SOLO LA PRIMA RIGA di ogni file archiviato, per vedere se portava il
    # marchio. Ma la prima riga e' la piu' vecchia: se la riparazione ha completato il file e poi
    # un raccoglitore ci ha aggiunto righe nuove, la prima riga resta a posto e il file non torna
    # mai in coda. Misurato stanotte: 3.562 record su base e 20.224 su robinhood, tutti
    # riparabili, tutti dentro file che il segnalibro dichiarava completi.
    # Adesso si confronta la dimensione con quella registrata quando l'abbiamo dichiarato finito:
    # se e' cambiata, dentro c'e' roba che non abbiamo guardato. Costa una `stat` per file, non
    # una lettura.
    _riaperti = 0
    for _k, _dim in list(fatti.items()):
        if "/" not in _k:
            fatti.pop(_k, None)        # chiave del vecchio formato: si riapre
            _riaperti += 1
            continue
        _sub, _nome = _k.split("/", 1)
        _p = f"data/multichain/{CHAIN}/{_sub}/{_nome}"
        if not os.path.exists(_p):
            continue
        if misura_file(_p) != _dim:
            fatti.pop(_k, None)
            _riaperti += 1
    if _riaperti:
        print(f"RIPARA | {CHAIN}: {_riaperti} file riaperti (cresciuti o con chiave vecchia)",
              flush=True)

    corretti = invariati = irrecuperabili = pool_fatti = 0
    non_chiesti = 0
    _uniti = 0
    illeggibili = 0
    scarti = []
    elenco = []
    for _c in cartelle:
        if os.path.isdir(_c):
            elenco += [(_c, x) for x in sorted(os.listdir(_c)) if mia(x)]
    # LA CHIAVE DEL SEGNALIBRO COMPRENDE LA CARTELLA (22/09).
    # Lo stesso nome di file esiste in `storico` E in `vivo` — sono due archivi dello stesso pool,
    # con contenuti diversi. Il segnalibro pero' li registrava con la sola chiave del NOME: quando
    # la copia in `storico` veniva dichiarata finita, quella in `vivo` risultava finita anche lei.
    # E il controllo sulla dimensione non se ne accorgeva, perche' risolveva il percorso prendendo
    # la PRIMA cartella in cui il nome esisteva: trovava la dimensione di `storico`, che
    # combaciava.
    # Misurato: un file con 300 record puliti in `storico` e 13 record di cui 2 sbagliati in
    # `vivo`; la seconda copia era invisibile per costruzione. In tutto 1.389 marchi sbagliati su
    # base e 3.665 su robinhood, tutti in file freddi che nessuno avrebbe mai riaperto.
    for _cart, fn in elenco:
        if time.time() - t0 > BUDGET:
            break
        chiave = f"{os.path.basename(_cart)}/{fn}"
        if chiave in fatti:
            continue
        p = os.path.join(_cart, fn)
        # SOLO FILE FREDDI, MA IL FREDDO SI LEGGE DAI DATI (21/09, correzione entro l'ora).
        # La riparazione deve toccare solo file che nessun raccoglitore sta scrivendo, altrimenti
        # i due si cancellano il lavoro a vicenda (misurato ieri: zero marchi sopravvissuti su
        # tremila file). Ma avevo usato la DATA DI MODIFICA del file, e su un runner di GitHub il
        # repository viene clonato da zero a ogni giro: tutti i file risultano scritti «adesso».
        # Risultato: sulla mia macchina funzionava, sul cloud saltava TUTTO — zero pool riparati su
        # entrambe le chain, mentre il segnalibro diceva che ce n'erano diciassettemila da fare.
        # L'eta' vera sta dentro il dato: ogni record porta «acq», l'istante in cui l'abbiamo
        # raccolto. Quella sopravvive al clone perche' e' un fatto, non una proprieta' del disco.
        try:
            righe = [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]
        except Exception:
            # UN FILE CHE NON SI RIESCE A LEGGERE NON E' UN FILE RIPARATO (20/09).
            # Qui veniva aggiunto ai «fatti» e non veniva piu' ritentato MAI: un fallimento di
            # lettura — un file scritto a meta' mentre un'altra corsia lo toccava, un gzip
            # troncato — diventava per sempre «gia' a posto».
            # Misurato: file dichiarati riparati con istanti ancora sbagliati di 6.875 secondi e
            # nessuna traccia del campo «orario» che la riparazione scrive. Non erano stati
            # riparati: erano stati saltati e archiviati.
            # E' la stessa forma di errore del 429 letto come finestra troppo larga e del pool
            # illeggibile scambiato per pool vuoto: registrare un tentativo fallito come un esito.
            illeggibili += 1
            continue
        if not righe:
            if finito(righe):
                fatti[chiave] = misura_file(p)
            continue
        _ultimo_acq = max((r.get("acq") or 0) for r in righe)
        if time.time() - _ultimo_acq < FREDDO:
            continue          # raccolto di recente: potrebbe essere in mano a un raccoglitore
        # IL MARCHIO DELLA CODA VIVA, PRIMA DELLE 10:33 DEL 21/09, E' FALSO (21/09).
        # Il 20/09 sera ho aggiunto «orario: catena» alle righe della coda viva dando per scontato
        # che usasse istanti veri. Non li usava: interpolava fra i due estremi del lotto, e quando
        # il secondo estremo mancava dava a TUTTE le righe lo stesso istante. Misurato contro la
        # catena: errori di 278 e 482 secondi su righe che si dichiaravano verificate, con lo stesso
        # ts su blocchi diversi.
        # Il danno vero non e' l'errore: e' che quel marchio le rendeva INVISIBILI a questa
        # riparazione. Una stima etichettata come verifica e' peggio di una stima dichiarata.
        # Qui si toglie il marchio a quelle righe, cosi' tornano in coda e vengono controllate
        # davvero. Il costo e' ricontrollare anche qualche riga che era gia' a posto: accettabile,
        # perche' l'alternativa e' fidarsi di un'etichetta che so essere stata sbagliata.
        for r in righe:
            if (r.get("orario") == "catena" and r.get("classe") == "point-in-time"
                    and (r.get("acq") or 0) < MARCHIO_SOSPETTO):
                r.pop("orario", None)
                r["ritardo"] = None
        # solo i record del vecchio produttore: quelli nuovi portano gia' il ritardo scritto
        # LA RIPARAZIONE E IL METRO DEVONO PARLARE DELLA STESSA COSA (21/09). «Da fare» si
        # decideva sull'assenza di `ritardo`, mentre il metro misura la presenza di
        # `orario == catena`. Esistono record con `ritardo` scritto e `orario` vuoto: la
        # riparazione NON li vedeva e il metro li contava come mancanti.
        # Misurato su base: 4.913 record freddi non verificati, con 97 file che il segnalibro
        # dichiarava gia' fatti — e i giri finivano in un minuto dicendo «non c'e' lavoro».
        # Due definizioni diverse della stessa cosa producono lavoro invisibile a chi dovrebbe
        # farlo: e' la stessa famiglia che la revisione esterna ha chiamato «non ho completato
        # diventa indistinguibile da ho verificato e non c'era niente».
        da_fare = [r for r in righe if not timbrato(r) and r.get("blocco")]
        if not da_fare:
            if finito(righe):
                fatti[chiave] = misura_file(p)
            continue
        # LA SONDA A TRE CAMPIONI E' STATA TOLTA (22/09), E L'AVEVO GIA' SAPUTO.
        # Serviva a risparmiare: si chiedevano gli istanti di TRE blocchi sparsi nel file e, se
        # coincidevano, si marcavano «verificati» tutti e trecento i record senza chiederli.
        # La revisione esterna me l'aveva contestato. Avevo misurato che non stava contaminando
        # nulla — vero in quel momento, falso dopo — e l'avevo lasciata in piedi.
        # Misurato stanotte contro la catena, con codice indipendente: il 6,7% dei record di base
        # aveva l'istante SBAGLIATO (errori da 28 minuti a 2,4 ore) pur portando l'etichetta
        # «verificato», e meta' di quelli portava anche la data della verifica — cioe' erano stati
        # certificati da questa sonda senza essere stati guardati.
        # Tre campioni giusti non dimostrano che i trecento lo siano: un file misto passa la sonda.
        # E' esattamente il difetto che inseguo da un giorno — un controllo che assolve invece di
        # verificare — e me l'ero rimesso in casa da solo per risparmiare chiamate.
        # Il risparmio adesso viene dalla memoria dei blocchi, che non inventa niente.
        blocchi = sorted({r["blocco"] for r in da_fare})
        veri = istanti_con_memoria(url, blocchi, per_lotto)
        cambiato = False
        rimasti = 0
        for r in righe:
            if timbrato(r) or not r.get("blocco"):
                continue
            v = veri.get(r["blocco"])
            if v is None:
                # NON CHIESTO NON E' IRRECUPERABILE (22/09). Quando il budget scade, `istanti`
                # esce dal ciclo e i blocchi rimasti tornano senza valore: finivano contati come
                # «irrecuperabili», 106.826 in un giro solo su base. Ho passato un'ora a cercare
                # il guasto nel nodo — che invece serviva sei gruppi in parallelo senza un errore,
                # anche sui blocchi vecchi.
                # E' l'ennesima forma dello stesso difetto: un tempo scaduto registrato come un
                # verdetto. Qui i due casi si contano separati, cosi' il numero dice quale dei due
                # e' successo.
                if time.time() - t0 > BUDGET:
                    non_chiesti += 1
                else:
                    irrecuperabili += 1
                rimasti += 1
                continue
            vecchio = r.get("ts")
            if vecchio and abs(vecchio - v) > 2:
                scarti.append(abs(vecchio - v))
                corretti += 1
            else:
                invariati += 1
            r["ts"] = v
            acq = r.get("acq") or v
            r["ritardo"] = max(0, acq - v)
            r["classe"] = "point-in-time" if r["ritardo"] <= SOGLIA_PIT else "ricostruzione-storica"
            r["orario"] = "catena"        # da dove viene l'istante, scritto nel record
            # LA DATA DELLA VERIFICA E' UNA COSA, QUELLA DELLA RACCOLTA UN'ALTRA (21/09).
            # Il controllo dei marchi falsi usava `acq` — quando il record e' stato RACCOLTO — come
            # se dicesse quando il marchio era stato scritto. Ma la riparazione riscrive il marchio
            # OGGI lasciando `acq` al suo valore vecchio: cosi' ogni record appena verificato
            # risultava sospetto, e la percentuale SALIVA mentre il lavoro procedeva.
            # Misurato: 3.113 sospetti su base, il 100% dei quali gia' verificati per davvero.
            # Quella condizione dell'esame non avrebbe MAI potuto passare.
            r["ver"] = int(time.time())

            cambiato = True
        if cambiato:
            _ok, _agg = scrivi_unendo(p, righe)
            if not _ok:
                continue
            _uniti += _agg
        # UN FILE CON RECORD ANCORA SENZA ISTANTE NON E' FINITO (20/09). Qui veniva archiviato
        # lo stesso, se almeno UN record era stato sistemato: gli altri restavano sbagliati per
        # sempre. Misurato su base in un giro solo: 56.623 record contati «irrecuperabili» — e
        # verificato a mano che quei blocchi il nodo li serve benissimo, 12 su 12 e 10 su 10 a
        # gruppi. Non erano irrecuperabili: erano chiamate fallite sul momento, promosse a verdetto.
        # E' l'ottava volta in ventiquattro ore che trovo questa forma: un fallimento transitorio
        # registrato come un esito definitivo. Qui il file resta aperto e ci si torna.
        if rimasti:
            pool_fatti += 1
            continue
        if finito(righe):
            fatti[chiave] = misura_file(p)
        pool_fatti += 1

    # IL SEGNALIBRO SI UNISCE, NON SI SOSTITUISCE (20/09). Trovato perche' il conto dei pool
    # riparati e' ANDATO INDIETRO: da 9.153 a 2.000. Un segnalibro che torna indietro vuol dire
    # lavoro rifatto da capo.
    # La causa: due corse della stessa corsia possono sovrapporsi, ognuna con la propria copia del
    # file, e chi spinge per ultimo vince — anche se il suo stato e' piu' vecchio. Con «-X ours»
    # nel pull, la copia del runner batte sempre quella del repo.
    # Qui non serve coordinarsi: l'informazione e' un INSIEME di cose gia' fatte, e due insiemi si
    # uniscono senza conflitto. Si rilegge il file appena prima di scrivere e si fa l'unione, cosi'
    # nessuna corsa puo' cancellare il lavoro di un'altra.
    try:
        # ANCHE QUI SI CONTROLLA LA VERSIONE (22/09, terza volta che questo difetto morde).
        # All'inizio del giro il segnalibro vecchio viene buttato. Ma qui, al momento di salvare,
        # si rilegge il file DAL DISCO e si rimettono dentro le sue voci — annullando
        # l'invalidazione a ogni giro. Il dato vecchio rientrava da un'altra porta, esattamente
        # come faceva attraverso il segnalibro comune.
        # Effetto misurato: 1.885 record sospetti su base e 4.907 su robinhood restavano dentro
        # file dichiarati finiti, e la condizione dell'esame non scendeva mai. La funzione che
        # decide era corretta — provata su file veri, rispondeva «non finito». Non veniva mai
        # interpellata, perche' quei file erano gia' archiviati da una regola che non esiste piu'.
        _d = json.load(open(CK))
        _v = (_d.get("fatti") or {}) if _d.get("versione") == VERSIONE_LOGICA else {}
        _vecchio = dict(_v) if isinstance(_v, dict) else {}
        if QUANTE > 1:
            _vecchio = {k: v for k, v in _vecchio.items() if mia(k)}
    except Exception:
        _vecchio = {}
    _prima = len(fatti)
    for _k, _v2 in _vecchio.items():
        fatti.setdefault(_k, _v2)
    if len(fatti) > _prima:
        print(f"RIPARA | {CHAIN}: uniti {len(fatti) - _prima} pool gia' riparati da un'altra corsa",
              flush=True)
    salva_memoria()
    print(f"RIPARA | {CHAIN}: {_da_memoria} istanti presi dalla memoria invece che dal nodo "
          f"({len(_memoria)} blocchi conosciuti)", flush=True)
    ck["fatti"] = fatti
    try:
        json.dump(ck, open(CK, "w"))
    except Exception:
        pass
    tot = sum(len(os.listdir(_c)) for _c in cartelle if os.path.isdir(_c))
    med = sorted(scarti)[len(scarti) // 2] / 60 if scarti else 0
    # ZERO LAVORO CON LAVORO RIMASTO E' UN'ANOMALIA, NON UN RIPOSO (21/09).
    # Stamattina questo agente ha riportato «0 pool in questo giro» su entrambe le chain mentre il
    # segnalibro ne dichiarava diciassettemila da fare. Il giro finiva in pochi secondi, e la
    # guardia del riarmo — giustamente — non lo rilanciava: una corsia che non trova lavoro non
    # deve girare a vuoto. Cosi' pero' il difetto e' rimasto invisibile per ore.
    # La guardia resta. Quello che cambia e' che questo caso adesso URLA: se non ho fatto niente ma
    # c'era da fare, il problema sono io, non la mancanza di lavoro.
    if pool_fatti == 0 and len(fatti) < tot:
        print(f"RIPARA | {CHAIN}: ATTENZIONE — zero pool riparati ma ne mancano {tot - len(fatti)}. "
              f"Non e' che non c'era lavoro: e' che non sono riuscito a farlo.", flush=True)
    print(f"RIPARA | {CHAIN}: {pool_fatti} pool in questo giro, {len(fatti)}/{tot} in tutto | "
          f"corretti {corretti} record (scarto mediano {med:.1f} min), gia' giusti {invariati}, "
          f"irrecuperabili {irrecuperabili}, illeggibili {illeggibili}, "
          f"righe altrui riunite {_uniti}", flush=True)


if __name__ == "__main__":
    main()
