"""I PRIMI COMPRATORI VERI di ogni pool: persone, non porte.

PERCHE' ESISTE (1/10, priorita' decisa da Nicolo': «partiamo dalla 3 e andiamo in insider mode»).

Il 25/09 `agents/iniziatori.py` ha scoperto una cosa grave: il campo che usavamo come «chi ha
fatto lo scambio» registra nell'81% dei casi il ROUTER, non la persona. Un solo indirizzo faceva
il 42,6% di tutti gli scambi. Conseguenza: cinque dei nostri attributi — compratori distinti,
portafogli nuovi, scambi per portafoglio, concentrazione dei portafogli, peso del primo
portafoglio — misuravano PORTE, non gente.

Quel file di correzione esiste da sei giorni e **non e' mai stato unito all'insieme**: la ricerca
ha continuato a girare sugli attributi sbagliati. Questo e' il pezzo che mancava.

COSTA ZERO CHIAMATE. Non raccoglie niente: incrocia due cose che abbiamo gia' sul disco —
i file degli scambi per pool (che hanno l'hash della transazione) e la mappa
`iniziatori.json.gz` (hash -> persona che ha firmato). Verificato su quattro pool vere l'1/10:
le prime cinque transazioni si risolvono in persone nel 5/5, 5/5, 3/5, 0/5 dei casi.

COSA PRODUCE: data/multichain/<chain>/insider.json.gz
    {"acq": <quando>, "da": {"<pool>": ["<persona1>", "<persona2>", ...]}}
le prime PRIMI_N persone che hanno comprato, in ordine di tempo, saltando quelle non risolte.

QUELLO CHE NON FA, di proposito: non calcola nessun punteggio e non decide niente. Separare chi
produce il dato da chi lo giudica e' la sola difesa contro il misurare cio' che fa comodo.
"""
import glob
import gzip
import json
import os
import sys
import time

CHAIN = os.environ.get("CHAIN", "robinhood")
# QUANTI COMPRATORI SI TENGONO (2/10). Erano DIECI, e quel dieci era il tetto invisibile di
# tutto il filone delle flotte: 73 portafogli risolti, 5 flotte di cui una da NOVE portafogli —
# e i pool toccati restavano CINQUE, sempre cinque, qualunque fosse l'accumulo.
# Il motivo: le flotte non comprano per prime. Comprano NELLA SCIA, dopo chi apre, e con dieci
# nomi per pool non le vedevamo mai. Alzarlo a quaranta costa ZERO chiamate — e' un incrocio sui
# file degli scambi che leggiamo gia' — e moltiplica le occasioni di incontrarle.
# Un parametro scelto quando serviva un'altra cosa diventa un tetto che non si vede.
PRIMI_N = int(os.environ.get("PRIMI_N", 40))
BUDGET = int(os.environ.get("BUDGET_SEC", 900))
BASE = f"data/multichain/{CHAIN}"
FUORI = f"{BASE}/insider.json.gz"
CARTELLE = ("storico", "vivo", "trades")


def persone():
    """La mappa hash della transazione -> chi ha firmato davvero. Minuscole: gli hash arrivano
    in due forme e abbinare per forma invece che per contenuto e' l'errore del 22/09."""
    p = f"{BASE}/iniziatori.json.gz"
    if not os.path.exists(p):
        raise SystemExit(f"INSIDER | manca {p}: senza la mappa delle persone non costruisco "
                         f"niente. Un dato che non c'e' non deve diventare un dato finto.")
    d = json.load(gzip.open(p, "rt")).get("da", {})
    return {k.lower(): v for k, v in d.items()}


def primi_di(percorso, mappa):
    """Le prime PRIMI_N persone che hanno comprato in questa pool, in ordine di tempo."""
    try:
        righe = [json.loads(l) for l in gzip.open(percorso, "rt") if l.strip()]
    except Exception:
        return None
    righe = [y for y in righe if y.get("ts") and y.get("tx")]
    if not righe:
        return None
    righe.sort(key=lambda y: y["ts"])
    visti, fuori = set(), []
    for y in righe:
        chi = mappa.get(y["tx"].lower())
        if not chi or chi in visti:
            continue
        visti.add(chi)
        fuori.append(chi)
        if len(fuori) >= PRIMI_N:
            break
    return fuori or None


def main():
    t0 = time.time()
    mappa = persone()
    print(f"INSIDER | {CHAIN}: {len(mappa):,} transazioni con persona nota", flush=True)
    noti = {}
    if os.path.exists(FUORI):
        try:
            noti = json.load(gzip.open(FUORI, "rt")).get("da", {})
        except Exception:
            noti = {}
    prima = len(noti)
    # SI RIPRENDE DA DOVE SI ERA ARRIVATI, e non si rifa' cio' che e' gia' fatto: il lavoro
    # cresce coi dati e rifarlo da zero ogni giro e' il modo di non finirlo mai.
    fatti = saltati = senza = 0
    giro_piu_lungo = 0.0
    for cart in CARTELLE:
        d = os.path.join(BASE, cart)
        if not os.path.isdir(d):
            continue
        for percorso in sorted(glob.glob(os.path.join(d, "*.jsonl.gz"))):
            passato = time.time() - t0
            # IL BUDGET LASCIA SPAZIO AL SALVATAGGIO (lezione dell'1/10: otto corsie si
            # fermavano al limite del tetto e venivano annullate mentre consegnavano).
            if passato + giro_piu_lungo >= BUDGET:
                print(f"INSIDER | mi fermo a {passato/60:.0f} min per fare in tempo a salvare",
                      flush=True)
                break
            inizio = time.time()
            pool = os.path.basename(percorso).split(".")[0]
            # SI RIFA' SE NE SAPPIAMO MENO DI QUANTI NE CHIEDIAMO (2/10). Alzando PRIMI_N da
            # dieci a quaranta, i pool gia' fatti avevano liste di dieci: saltarli avrebbe
            # lasciato il tetto vecchio su tutto lo storico, e il cambiamento non sarebbe
            # servito a niente. Si rifanno quelli corti; quelli che hanno davvero meno
            # compratori di PRIMI_N si rifanno una volta e poi restano come sono.
            if pool in noti and len(noti[pool]) >= PRIMI_N:
                saltati += 1
                continue
            p = primi_di(percorso, mappa)
            if p:
                noti[pool] = p
                fatti += 1
            else:
                senza += 1
            giro_piu_lungo = max(giro_piu_lungo, time.time() - inizio)
    # SI CONTROLLA PRIMA DI SCRIVERE, NON DOPO (1/10, errore fatto e corretto nello stesso
    # file in cui avevo appena scritto l'avvertimento). La prima versione scriveva il file e
    # POI si accorgeva che era vuoto: un `insider.json.gz` da zero pool e' finito su GitHub,
    # cioe' esattamente il «segnaposto che somiglia a un risultato» di cui parla
    # CORREZIONE_LATENZA.md. Scrivere e poi pentirsi non e' un controllo.
    if not noti:
        print("INSIDER | nessuna pool risolta: NON scrivo niente. Un file vuoto col nome giusto "
              "e' peggio di un file assente, perche' chi lo legge crede di avere il dato.",
              flush=True)
        sys.exit(1)
    os.makedirs(os.path.dirname(FUORI), exist_ok=True)
    with gzip.open(FUORI, "wt") as h:
        json.dump({"acq": int(time.time()), "da": noti}, h)
    print(f"INSIDER | {CHAIN}: {fatti:,} pool nuove con i primi compratori veri "
          f"({prima:,} -> {len(noti):,}), {saltati:,} gia' fatte, "
          f"{senza:,} senza nessuna persona risolta", flush=True)


if __name__ == "__main__":
    main()
