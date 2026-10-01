"""Le decisioni permanenti, come DATI con un controllo che puo' fallire.

PERCHE' ESISTE (30/09, dopo un rilievo di Nicolo' che va scritto per intero).

Nicolo': «il sistema regredisce... e' come se si scordasse delle robe. Tipo Astra, dovevamo
chiamarlo massimo tre volte al giorno, e' un pezzo fondamentale... non lo chiami da tre giorni.
Secondo me si scorda la roba. Bisogna settare delle robe affinche' lui non faccia questi errori,
non si scordi.»

Aveva ragione, e la prova e' peggiore dell'accusa: `compliance_check.py` e `strategy.yaml` —
il sistema che avevamo costruito ESATTAMENTE per non dimenticare le decisioni — **non esistono
piu'**. Abbiamo costruito la difesa contro l'oblio e ci siamo dimenticati la difesa.

`DECISIONS.md` esiste ancora, 27 KB scritti bene. Ma e' PROSA: nessuna corsia lo legge, quindi
non vincola niente. **Un archivio non e' un vincolo.**

LA DIFFERENZA CHE QUESTO FILE INTRODUCE. Ogni decisione permanente ha:
  · il testo, con le parole di chi l'ha presa;
  · un CONTROLLO che gira da solo e che PUO' FALLIRE;
  · una gravita': «grave» ferma la pubblicazione, «avviso» la lascia passare gridando.

Una decisione senza controllo resta dichiarata ma non protetta, e il conto lo dice: se il numero
delle non protette cresce, stiamo tornando alla prosa.
"""
import datetime as dt
import json
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)


def _esiste(percorso, testo=None):
    p = os.path.join(RADICE, percorso)
    if not os.path.exists(p):
        return False, f"manca {percorso}"
    if testo:
        if testo not in open(p, encoding="utf-8", errors="replace").read():
            return False, f"{percorso} non contiene piu' «{testo[:40]}»"
    return True, ""


def _ore_da_ultimo(prefisso):
    """Quante ore dall'ultimo file che comincia per <prefisso>. None se non ce n'e' nessuno."""
    piu_nuovo = None
    for nome in os.listdir(RADICE):
        if nome.startswith(prefisso):
            q = nome.replace(prefisso, "")[:10]
            try:
                d = dt.datetime.strptime(q, "%Y-%m-%d")
            except ValueError:
                continue
            piu_nuovo = max(piu_nuovo or d, d)
    if not piu_nuovo:
        return None
    return (dt.datetime.now(dt.timezone.utc).replace(tzinfo=None) - piu_nuovo).total_seconds() / 3600


# ---------------------------------------------------------------- i controlli

def c_astra_gira():
    """Decisione di Nicolo' del 23/09: il consulente si chiama fino a 3 volte al giorno."""
    ok, perche = _esiste(".github/workflows/astra.yml")
    if not ok:
        return False, "non esiste nessuna corsia che chiami il consulente: dipende dalla memoria"
    ore = _ore_da_ultimo("CONSULENZA_")
    if ore is None:
        return False, "non trovo nessuna consulenza pubblicata"
    if ore > 36:
        return False, f"l'ultima consulenza ha {ore:.0f} ore: il consulente e' muto"
    return True, f"ultima consulenza {ore:.0f} ore fa"


def c_secondo_revisore():
    """Due revisori esterni, non uno: Astra toglie le illusioni, Grok guarda altrove."""
    ore = _ore_da_ultimo("REVISIONE_GROK_")
    if ore is None:
        return False, "non trovo nessuna revisione del secondo revisore"
    if ore > 96:
        return False, f"il secondo revisore tace da {ore/24:.0f} giorni"
    return True, f"ultima revisione {ore/24:.1f} giorni fa"


def c_prova_non_toccata():
    """Il contratto della prova in avanti non si modifica dopo averne visto un esito."""
    ok, perche = _esiste("PROVA_IN_AVANTI.md", "Si guarda una volta sola")
    return ok, perche or "il contratto c'e' e la clausola del guardare una volta sola pure"


def c_modello_congelato():
    """Il modello di selezione si applica, non si riaddestra."""
    ok, perche = _esiste("data/loop1/modello_congelato.json")
    if not ok:
        return False, "il modello congelato non c'e' piu': la prova sulla selezione e' impossibile"
    m = json.load(open(os.path.join(RADICE, "data/loop1/modello_congelato.json")))
    n = sum(v.get("pool_di_addestramento", 0) for v in m.values() if isinstance(v, dict))
    return True, f"congelato su {n:,} pool"


def c_niente_soldi_veri():
    """Nessun euro rischiato prima che la prova in avanti sia chiusa."""
    sospetti = []
    for base, _, nomi in os.walk(os.path.join(RADICE, "agents")):
        for nome in nomi:
            if not nome.endswith(".py"):
                continue
            if nome == "decisioni.py":
                continue     # IL CONTROLLO NON PUO' ACCUSARE SE STESSO (30/09): cerca le parole
                             # che firmano transazioni, e quelle parole stanno scritte qui dentro.
                             # Al primo giro si e' denunciato da solo.
            t = open(os.path.join(base, nome), encoding="utf-8", errors="replace").read()
            if "private_key" in t or "PRIVATE_KEY" in t or "sendTransaction" in t:
                sospetti.append(nome)
    if sospetti:
        return False, f"codice che puo' firmare transazioni: {', '.join(sospetti[:3])}"
    return True, "nessun codice che possa muovere soldi"


def c_memoria_fuori_da_github():
    """Quello che conta non vive in un posto solo — e «quello che conta» include la MEMORIA.

    Fino al 30/09 il deposito portava fuori solo i DATI. Decisioni, lezioni, consulenze e codice
    stavano solo su GitHub: i dati si raccolgono di nuovo, la memoria no.
    """
    ok, _ = _esiste(".github/workflows/deposito.yml", '("/tmp/memoria", "memoria")')
    if not ok:
        return False, "il deposito non porta fuori la MEMORIA (documenti, codice, decisioni)"
    return True, "il deposito porta fuori dati E memoria"


def c_lezioni_provate():
    """Le lezioni devono avere un controllo che puo' fallire, non essere convinzioni."""
    try:
        r = subprocess.run([sys.executable, "-B", os.path.join(QUI, "lezioni.py")],
                           capture_output=True, text=True, timeout=120)
    except Exception as e:
        return False, f"non riesco a far girare le lezioni ({type(e).__name__})"
    if "smentite: 0" not in r.stdout:
        return False, "c'e' almeno una lezione SMENTITA: un controllo si e' acceso"
    return True, [x for x in r.stdout.splitlines() if "provate:" in x][0].strip()


def c_decisioni_protette():
    """Quante decisioni hanno davvero un controllo. Se calano, torniamo alla prosa."""
    senza = [d["id"] for d in DECISIONI if d.get("controllo") is None]
    if senza:
        return False, f"decisioni dichiarate ma NON protette: {', '.join(senza)}"
    return True, f"tutte e {len(DECISIONI)} le decisioni hanno un controllo"


def c_strategie_incrociate():
    """Le strategie devono essere COMBINAZIONI di condizioni incrociate, non manopole singole.

    Decisione di Nicolo' del 23/09, ritrovata il 30/09 nei trascritti dopo che l'avevo persa:
    «io mi aspetto una strategia mostruosa, dove si analizzano migliaia di combinazioni tutte
    perfette. Entriamo quando la pressione e' X%, poi si concatena con una percentuale costi
    cosi', oppure una percentuale di buyer che subentra in base alla liquidita', e poi si
    interseca questo settore. Una roba molto piu' complicata, tecnica, tutta fatta di parametri
    incrociati.»

    Sette giorni dopo ho portato «compra al 5o scambio, $25, tieni una settimana»: UNA manopola.
    Questo controllo esiste perche' non succeda una terza volta.
    """
    ok, _ = _esiste("agents/combinazioni.py")
    if not ok:
        return False, ("non esiste il motore che cerca COMBINAZIONI incrociate: stiamo ancora "
                       "provando manopole singole, contro una decisione del 23/09")
    return True, "il motore delle combinazioni esiste"


def c_memoria_delle_parole():
    """Quello che il fondatore ha detto non vive solo in una chat che verra' riassunta."""
    ok, _ = _esiste("data/memoria/parole_del_fondatore.jsonl.gz")
    if not ok:
        return False, "le parole del fondatore non sono estratte: vivono solo nei trascritti"
    # SI LEGGE COMPRESSO (1/10): il file e' passato a .gz perche' 1,9 MB non passavano
    # dall'interfaccia di pubblicazione. Il controllo lo leggeva come testo ed e' esploso —
    # ma ha bloccato la pubblicazione, che e' esattamente il suo mestiere.
    import gzip as _gz
    with _gz.open(os.path.join(RADICE, "data/memoria/parole_del_fondatore.jsonl.gz"),
                  "rt", encoding="utf-8") as _h:
        n = sum(1 for _ in _h)
    if n < 1000:
        return False, f"solo {n} messaggi estratti: l'estrazione e' incompleta"
    return True, f"{n:,} messaggi del fondatore, interrogabili per parola"


def c_prezzo_ottenibile():
    """Ogni misura di un'entrata usa il prezzo che si paga, non quello che si vede.

    Il 30/09 notte questa distinzione ha ucciso il primo numero positivo del progetto: +17,6%
    diventa -11,4% con UN solo scambio di latenza. Senza questo controllo la misura tornerebbe
    a essere ottimista alla prima riscrittura.
    """
    ok, _ = _esiste("agents/insieme.py", "_uscita_{taglia}_ritardo")
    if not ok:
        return False, ("l'insieme non calcola l'esito col prezzo ottenibile: le misure tornano "
                       "a usare un prezzo che non si puo' avere")
    ok2, _ = _esiste("agents/dati.py", "_uscita_25_ritardo")
    if not ok2:
        return False, "il dato non dichiara i campi col ritardo come esiti: si possono abusare"
    return True, "le misure nascono col prezzo ottenibile"


def c_ripristino_provato():
    """Esiste la prova che da una cartella vuota il sistema riparte davvero.

    Astra (1/10): «"verificata" puo' significare soltanto che il file trasferito ha lo stesso
    hash. La prova decisiva e' un ripristino in ambiente pulito, non un checksum.»
    Aveva ragione due volte: non l'avevamo mai fatto, e quando l'ho fatto ha scoperto che la
    memoria NON era ancora sul deposito — mentre io avevo gia' detto al fondatore che lo era.
    """
    ok, _ = _esiste("agents/prova_ripristino.py")
    if not ok:
        return False, "non esiste nessuna prova di ripristino: la copia e' una speranza"
    return True, "la prova di ripristino esiste (va fatta girare per valere)"


def c_osservatore_esterno():
    """Esiste almeno un osservatore fuori da GitHub Actions.

    Provato sul campo l'1/10: tre guardiani sulla stessa infrastruttura sono morti insieme e
    sono rimasti morti quattro ore. L'indipendenza si misura sul dominio di guasto.
    """
    ok, _ = _esiste("agents/dal_di_fuori.sh")
    if not ok:
        return False, "nessun osservatore fuori da GitHub Actions: i guardiani sono uno solo"
    return True, "c'e' un osservatore sul Mac (parziale: si ferma con la sessione)"


def c_prima_di_cancellare():
    """Esiste il controllo che rifiuta di cancellare cio' che non e' su GitHub.

    Paura di Nicolo' dell'1/10: «ho paura che cancelli della roba importante». Fondata: il
    25/09 una giornata di lavoro e' andata perduta cosi'. L'1/10 ho cancellato 26 GB di copia
    dopo aver verificato a mano — disciplina, non meccanismo, e la disciplina stanotte ha
    fallito tre volte.
    """
    ok, _ = _esiste("agents/prima_di_cancellare.py", "LA CANCELLAZIONE SI RIFIUTA")
    if not ok:
        return False, "nessun controllo prima di cancellare: dipende dalla mia attenzione"
    return True, "la cancellazione si rifiuta se qualcosa non e' su GitHub"


def c_segreti_non_escono():
    """Nessuna corsia stampa un segreto, e il repository e' pubblico."""
    ok, _ = _esiste("pubblica.sh", "segreti_non_escono")
    if not ok:
        return False, "la porta non controlla se le corsie stampano segreti"
    return True, "la porta rifiuta una corsia che stampa un segreto"


def c_regola_ripetizione():
    """Un segnale conta solo se si RIPETE: tre volte su cinque, su entrambe le chain.

    Fissata l'1/10 PRIMA di avere i risultati del ciclo automatico. Con otto prove al giorno,
    una configurazione fortunata salta fuori ogni giorno: senza la regola della ripetizione il
    ciclo diventa una fabbrica di illusioni che si auto-conferma.
    """
    ok, _ = _esiste("PIANO_OTTOBRE.md", "almeno tre ripetizioni su cinque")
    if not ok:
        return False, "la regola della ripetizione non e' scritta: un colpo fortunato passerebbe"
    return True, "un segnale conta solo se si ripete 3 volte su 5, su entrambe le chain"


# ---------------------------------------------------------------- le decisioni

DECISIONI = [
 {"id": "astra-tre-al-giorno", "data": "2026-09-23", "chi": "Nicolo'", "gravita": "grave",
  "testo": "Il consulente esterno si chiama fino a tre volte al giorno, e ogni strategia deve "
           "passare dal suo commento. E' un pezzo fondamentale: senza di lui non c'e' revisione.",
  "controllo": c_astra_gira},

 {"id": "due-revisori", "data": "2026-09-25", "chi": "Nicolo'", "gravita": "avviso",
  "testo": "I revisori esterni sono DUE e guardano cose diverse: Astra toglie le illusioni, "
           "Grok cerca dove non guardiamo. Uno solo e' un punto cieco condiviso.",
  "controllo": c_secondo_revisore},

 {"id": "prova-una-volta-sola", "data": "2026-09-30", "chi": "Claude, approvato da Nicolo'",
  "gravita": "grave",
  "testo": "Il contratto della prova in avanti si guarda UNA volta sola, al traguardo. "
           "Sbirciare e fermarsi quando il numero piace e' il modo classico di comprare rumore.",
  "controllo": c_prova_non_toccata},

 {"id": "modello-congelato", "data": "2026-09-30", "chi": "Claude", "gravita": "grave",
  "testo": "Il modello di selezione e' congelato: si applica, non si riaddestra. Un modello che "
           "impara ogni giorno non si puo' giudicare sul futuro.",
  "controllo": c_modello_congelato},

 {"id": "niente-soldi-veri", "data": "2026-08-06", "chi": "Nicolo'", "gravita": "grave",
  "testo": "Nessun euro rischiato finche' una strategia non ha superato la prova sul futuro.",
  "controllo": c_niente_soldi_veri},

 {"id": "memoria-fuori-github", "data": "2026-09-30", "chi": "Nicolo'", "gravita": "avviso",
  "testo": "«Abbiamo un altro server con 100 GB oltre che GitHub, dobbiamo salvare tutto cio'. "
           "Se la memoria e' importantissima e non la mettiamo, ci scordiamo le robe.»",
  "controllo": c_memoria_fuori_da_github},

 {"id": "lezioni-con-prova", "data": "2026-09-26", "chi": "Claude", "gravita": "avviso",
  "testo": "Una lezione vale solo se esiste un controllo che la prova E CHE PUO' FALLIRE. "
           "Le altre restano convinzioni.",
  "controllo": c_lezioni_provate},

 {"id": "strategie-incrociate", "data": "2026-09-23", "chi": "Nicolo'", "gravita": "grave",
  "testo": "«Io mi aspetto una strategia mostruosa, dove si analizzano migliaia di combinazioni "
           "tutte perfette. Entriamo quando la pressione e' X%, poi si concatena con una "
           "percentuale costi, poi una percentuale di buyer in base alla liquidita', e poi si "
           "interseca questo settore. Una roba fatta di parametri incrociati.» "
           "PERSA per sette giorni: il 30/09 ho portato una manopola sola.",
  "controllo": c_strategie_incrociate},

 {"id": "memoria-delle-parole", "data": "2026-09-30", "chi": "Nicolo'", "gravita": "grave",
  "testo": "«Ti vai a prendere tutta la memoria della chat, tutto quello che ti ho detto. "
           "Se magari certe volte te lo scordi, lo devi ripescare, lo salvi in modo preciso. "
           "E' impossibile arrivare al gol con l'Alzheimer.»",
  "controllo": c_memoria_delle_parole},

 {"id": "prezzo-ottenibile", "data": "2026-09-30", "chi": "Claude", "gravita": "grave",
  "testo": "Il prezzo che vedi non e' quello che paghi: si paga lo scambio successivo. Ogni "
           "misura di un'entrata usa il prezzo OTTENIBILE. Questa distinzione ha ucciso il "
           "primo numero positivo del progetto, e senza un controllo tornerebbe a essere "
           "dimenticata alla prima riscrittura.",
  "controllo": c_prezzo_ottenibile},

 {"id": "ripristino-provato", "data": "2026-10-01", "chi": "Astra, accolto da Claude",
  "gravita": "avviso",
  "testo": "Una copia di sicurezza che nessuno ha mai riaperto non e' una copia: e' una "
           "speranza. La prova decisiva e' ripartire da una cartella vuota, non confrontare "
           "un'impronta.",
  "controllo": c_ripristino_provato},

 {"id": "osservatore-esterno", "data": "2026-10-01", "chi": "Astra, provato sul campo",
  "gravita": "avviso",
  "testo": "Serve almeno un osservatore in un dominio di guasto distinto. Tre guardiani sulla "
           "stessa infrastruttura sono morti insieme e sono rimasti morti quattro ore. "
           "Definitivo: un conto gratuito su healthchecks.io, che richiede la mano di Nicolo'.",
  "controllo": c_osservatore_esterno},

 {"id": "prima-di-cancellare", "data": "2026-10-01", "chi": "Nicolo'", "gravita": "grave",
  "testo": "«Ho paura che cancelli della roba importante.» Niente si cancella se non esiste "
           "anche su GitHub, e se il controllo non puo' girare la cancellazione si rifiuta "
           "comunque: non sapere non e' sapere che va bene.",
  "controllo": c_prima_di_cancellare},

 {"id": "segreti-non-escono", "data": "2026-10-01", "chi": "Claude", "gravita": "grave",
  "testo": "Il repository e' PUBBLICO e la chiave del consulente vive fra i segreti. Nessuna "
           "corsia puo' stampare un segreto: un `echo` messo per debug lo regalerebbe a tutti.",
  "controllo": c_segreti_non_escono},

 {"id": "regola-ripetizione", "data": "2026-10-01", "chi": "Claude, prima dei risultati",
  "gravita": "grave",
  "testo": "Un segnale conta solo se si RIPETE: almeno tre volte su cinque, su entrambe le "
           "chain, con la soglia che sale col numero di prove. Con otto prove al giorno una "
           "configurazione fortunata salta fuori ogni giorno. E al 20/10, senza ripetizioni, "
           "la risposta non e' la prova numero 151: e' che il mercato non paga.",
  "controllo": c_regola_ripetizione},

 {"id": "decisioni-protette", "data": "2026-09-30", "chi": "Nicolo'", "gravita": "grave",
  "testo": "«Bisogna settare delle robe affinche' lui non faccia questi errori, non si scordi.» "
           "Ogni decisione permanente ha un controllo che gira da solo e che puo' fallire.",
  "controllo": c_decisioni_protette},
]


def verifica():
    gravi, avvisi, ok = [], [], []
    for d in DECISIONI:
        if d.get("controllo") is None:
            gravi.append((d, "NESSUN CONTROLLO: e' una dichiarazione, non una difesa"))
            continue
        try:
            passa, perche = d["controllo"]()
        except Exception as e:
            passa, perche = False, f"il controllo e' esploso ({type(e).__name__}: {e})"
        if passa:
            ok.append((d, perche))
        elif d["gravita"] == "grave":
            gravi.append((d, perche))
        else:
            avvisi.append((d, perche))
    return gravi, avvisi, ok


def main():
    gravi, avvisi, ok = verifica()
    print(f"DECISIONI | {len(ok)} rispettate, {len(avvisi)} avvisi, {len(gravi)} VIOLAZIONI GRAVI",
          flush=True)
    for d, perche in ok:
        print(f"   ok      {d['id']:26s} {perche}", flush=True)
    for d, perche in avvisi:
        print(f"   AVVISO  {d['id']:26s} {perche}", flush=True)
    for d, perche in gravi:
        print(f"   GRAVE   {d['id']:26s} {perche}", flush=True)
        print(f"           decisa il {d['data']} da {d['chi']}: {d['testo'][:110]}", flush=True)
    json.dump({"quando": dt.datetime.now(dt.timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds"),
               "rispettate": [d["id"] for d, _ in ok],
               "avvisi": {d["id"]: p for d, p in avvisi},
               "violazioni_gravi": {d["id"]: p for d, p in gravi}},
              open(os.path.join(RADICE, "data/decisioni_stato.json"), "w"), indent=1)
    if gravi:
        sys.exit(1)


if __name__ == "__main__":
    main()
