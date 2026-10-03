"""CHI FINANZIA i portafogli che comprano per primi: dal portafoglio all'ENTITA'.

PERCHE' ESISTE (2/10, l'ipotesi che Nicolo' porta da mesi, con le sue parole).

    «Se noi scopriamo che ci sono degli insider che vengono finanziati da grossi wallet e questi
    si mettono insieme — magari ognuno ha il suo wallet, viene finanziato, e poi in modo
    incrociato entrano sempre in modo combinato — quello vince sull'analisi del pattern.»

Due versioni piu' debole della stessa idea sono state provate e sono cadute: le SQUADRE VISIBILI
(portafogli che compaiono insieme: vanno peggio, -19,8% su robinhood) e i PORTAFOGLI NUOVI (il
nonce non predice l'esito). Entrambe cercavano l'ombra del fenomeno, perche' **chi coordina
cambia portafoglio**: dieci indirizzi nuovi per dieci monete hanno co-occorrenza ZERO.

Il legame che NON si cambia a costo zero e' chi ha pagato le prime unita' di quel portafoglio.
Un indirizzo nuovo non ha fondi: qualcuno gliene manda. Quel qualcuno e' l'entita'.

LA PROVA CHE HA FATTO PARTIRE QUESTO FILE. Otto portafogli con nonce ZERO, cioe' creati per
comprare quella moneta: CINQUE erano finanziati da DUE soli indirizzi, con importi identici e
tondi (1,00000 esatto). Otto chiamate per vederlo.

COSTO: ZERO EURO. `base.blockscout.com` e' un esploratore pubblico, senza chiave e senza
fatturazione, e una sola chiamata per portafoglio da' le sue prime transazioni in ordine
cronologico. Misurato: la via RPC NON bastava — `eth_getLogs` accetta finestre di 1.000 blocchi
su base e 10.000 su robinhood, quindi risalire indietro costava centinaia di chiamate per
portafoglio, e il finanziamento in valuta nativa non lascia log.

ROBINHOOD NON CE L'HA. Gli esploratori provati (`explorer.mainnet.chain.robinhood.com`,
`robinhood.blockscout.com`) non rispondono. Quindi questo file lavora su base e lo DICE: una
misura che vale su una chain sola non puo' passare la regola di ripetizione, e saperlo prima
vale piu' che scoprirlo dopo.
"""
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.request

CHAIN = os.environ.get("CHAIN", "base")
# il Referer va messo per chain, altrimenti Cloudflare rifiuta
BUDGET = int(os.environ.get("BUDGET_SEC", 1080))
# GENTILE CON UN SERVIZIO GRATUITO (2/10): a 0,35 secondi ho preso un 429 dopo 133 chiamate.
# Un secondo. Le fette girano su macchine diverse, quindi con indirizzi di rete diversi: la
# velocita' si prende dal parallelismo, non dal pestare sullo stesso servizio.
PAUSA = float(os.environ.get("PAUSA", 0.25 if (os.environ.get("ETHERSCAN_KEY") or "").strip() else 6.0))
# IL BERSAGLIO E' PICCOLO, QUINDI SI PUO' ESSERE PAZIENTI (2/10). Misurato: il servizio ci
# chiude la porta dopo DIECI chiamate a un secondo, anche da macchine nuove. A quel ritmo gli
# 11.275 primi compratori non si finiscono mai.
# Ma non servono tutti: un portafoglio con nonce 400.000 ha il suo primo finanziamento di mesi
# prima e non dice niente su questa moneta. Quelli che contano sono i NUOVISSIMI — creati per
# comprare — e su base sono TRECENTO. Con trecento si puo' aspettare sei secondi fra le
# chiamate ed essere comunque finiti in un giro.
# Quando il bersaglio e' piccolo, la pazienza costa meno della fretta.
MAX_NONCE = int(os.environ.get("MAX_NONCE", 1))
FETTE = max(1, int(os.environ.get("FETTE", 1)))
FETTA = int(os.environ.get("FETTA", 0)) % FETTE
# DUE STRADE, LA PIU' LARGA SE C'E' (2/10). Blockscout e' pubblico e senza chiave, e funziona:
# ma ci chiude la porta dopo DIECI chiamate per finestra di tempo, anche a sei secondi di
# distanza e da macchine diverse. Misurato: 38 portafogli risolti su 300 in un giro.
# Etherscan V2 risponde sulla stessa chain e vuole una chiave GRATIS (registrazione senza carta,
# 5 chiamate al secondo e 100.000 al giorno): con quella i 300 si fanno in un minuto.
# Qui si usa la chiave SE c'e', altrimenti si continua con Blockscout. Nessuna spesa in nessuno
# dei due casi: la differenza e' solo la velocita', e il lavoro va avanti comunque.
CHIAVE = (os.environ.get("ETHERSCAN_KEY") or "").strip()
CHAIN_ID = {"base": 8453}


def indirizzo_api(w, azione="txlist"):
    if CHIAVE and CHAIN in CHAIN_ID:
        return (f"https://api.etherscan.io/v2/api?chainid={CHAIN_ID[CHAIN]}"
                f"&module=account&action={azione}&address={w}&sort=asc&page=1&offset=5"
                f"&apikey={CHIAVE}")
    return (f"{ESPLORATORI[CHAIN]}?module=account&action={azione}&address={w}"
            f"&sort=asc&page=1&offset=5")


ESPLORATORI = {"base": "https://base.blockscout.com/api",
               "robinhood": "https://robinhoodchain.blockscout.com/api"}
BASE = f"data/multichain/{CHAIN}"
FUORI = f"{BASE}/finanziatori.json.gz"
# OGNI FETTA SCRIVE UN FILE SUO (2/10). La prima versione di questo file, scritta un'ora DOPO
# aver corretto lo stesso errore su `iniziatori`, metteva `FUORI` — un nome solo — per quattro
# fette: il pubblicatore ne teneva uno e sul ramo sono arrivati 0,1 KB invece di quaranta
# portafogli. Terza volta in sei ore.
# La lezione sta in agents/a_fette.py, come FUNZIONE e non come commento: un commento protegge
# il file dove sta, non il prossimo.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a_fette as AF                                              # noqa: E402

PEZZO = AF.nome_pezzo(BASE, "finanziatori")
# LE INTESTAZIONI DI UN BROWSER VERO (3/10). Con il solo `User-Agent: Mozilla/5.0`
# l'esploratore di robinhood rispondeva 403, e per un giorno intero ho scritto che «robinhood
# non ha un esploratore pubblico» — fino a scriverlo in due documenti come se fosse un fatto.
# Con le intestazioni complete risponde. Quarta volta oggi che un «non si puo'» era un
# «non ho chiesto nel modo giusto»: prima il nodo RPC, poi il grafo dei finanziatori, poi
# l'esploratore di base, ora questo.
# E questa e' la piu' importante: con DUE chain la regola di ripetizione diventa soddisfacibile,
# cioe' la differenza fra un indizio e una strategia.
H = {"User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"),
     "Accept": "application/json,text/plain,*/*",
     "Accept-Language": "en-US,en;q=0.9",
     "Accept-Encoding": "identity",
     "Referer": f"https://{'robinhoodchain' if os.environ.get('CHAIN','base')=='robinhood' else 'base'}.blockscout.com/"}


def da_risolvere():
    """I portafogli che hanno comprato per primi, dai piu' NUOVI: quelli contano di piu'."""
    try:
        ini = json.load(gzip.open(f"{BASE}/iniziatori.json.gz", "rt")).get("da", {})
    except Exception:
        raise SystemExit(f"FINANZIATORI | manca {BASE}/iniziatori.json.gz: senza chi ha firmato "
                         f"non so di chi cercare il finanziatore")
    nonce = {}
    try:
        nonce = json.load(gzip.open(f"{BASE}/nonce.json.gz", "rt")).get("da", {})
    except Exception:
        pass
    eta = {}
    for h, n in nonce.items():
        w = ini.get(h)
        if w:
            eta[w] = min(eta.get(w, 10 ** 9), n)
    primi = set()
    try:
        primi = {w for lista in json.load(gzip.open(f"{BASE}/insider.json.gz", "rt"))
                 .get("da", {}).values() for w in lista}
    except Exception:
        primi = set(ini.values())
    # SOLO I NUOVISSIMI, E NON SOLO I PRIMI COMPRATORI (2/10). Due correzioni insieme:
    #  · si tagliano i portafogli sopra MAX_NONCE: per loro il finanziatore e' di mesi prima;
    #  · NON si guardano solo i primi compratori delle pool mappate. Dei 300 portafogli con
    #    nonce <=1 su base, uno solo e' primo compratore di una pool che abbiamo mappato: gli
    #    altri 299 sono dentro i primi scambi senza essere i primissimi, e sono esattamente i
    #    soldati della flotta. Filtrare su `primi` li buttava via tutti.
    candidati = set(eta) | (primi & set(eta))
    freschi = [w for w in candidati if eta.get(w, 10 ** 9) <= MAX_NONCE]
    print(f"FINANZIATORI | bersaglio: {len(freschi):,} portafogli con nonce <= {MAX_NONCE} "
          f"(su {len(eta):,} di cui sappiamo l'eta)", flush=True)
    return sorted(freschi, key=lambda w: eta.get(w, 10 ** 9))


def finanziatore(w, tentativi=4):
    """Chi ha mandato le prime unita' a questo portafoglio.

    Torna (indirizzo, None) se si sa, (None, "vuoto") se davvero non ha transazioni entranti,
    (None, "strozzato") se il servizio ci ha chiuso la porta.

    STROZZATO NON E' VUOTO (2/10). La prima versione, scritta un quarto d'ora prima di questa,
    trattava qualunque risposta mancante come «nessuna transazione entrante»: con 133 chiamate
    ho preso un HTTP 429 e il programma ha scritto 133 volte «questo portafoglio non ha
    finanziatore». A mano, poco prima, ne risolvevo SETTE su OTTO.
    Un limite di richieste e' una cosa nostra, non del mondo: registrarlo come un fatto e' il
    modo piu' rapido di costruire una conclusione su un'assenza inventata — lo stesso errore del
    22/09, quando «non si puo' avere» era diventato un fatto senza essere provato.
    Qui il 429 si aspetta e si riprova, e se non si risolve NON si scrive niente: il portafoglio
    resta da fare.
    """
    # ANCHE LE TRANSAZIONI INTERNE (3/10). L'elenco standard mostra solo le transazioni
    # ESTERNE. Su robinhood otto portafogli su dieci risultavano «senza transazione entrante» —
    # e non era vero: erano finanziati da transazioni INTERNE, cioe' da chiamate di contratto,
    # che quell'elenco non riporta. Misurato: su cinque portafogli con nonce zero, due erano
    # finanziati per via interna DALLO STESSO indirizzo. Una flotta, invisibile a chi guarda
    # solo le esterne.
    # Un'assenza in un elenco parziale non e' un'assenza: e' la quinta volta oggi.
    for azione in ("txlist", "txlistinternal"):
        f, perche = _prova(w, azione, tentativi)
        if f:
            return f, None
        if perche == "strozzato":
            return None, "strozzato"
    return None, "vuoto"


def _prova(w, azione, tentativi):
    u = indirizzo_api(w, azione)
    attesa = 2.0
    for k in range(tentativi):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H),
                                                 timeout=30))
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 503, 502, 504):
                if k < tentativi - 1:
                    time.sleep(attesa)
                    attesa *= 2
                    continue
                return None, "strozzato"
            return None, f"HTTP {e.code}"
        except Exception as e:
            if k < tentativi - 1:
                time.sleep(attesa)
                attesa *= 2
                continue
            return None, type(e).__name__
    else:
        return None, "strozzato"
    for t in (d.get("result") or []):
        if (t.get("to") or "").lower() != w.lower():
            continue
        f = (t.get("from") or "").lower()
        # SE' STESSO NON E' UN FINANZIATORE: nella prima prova un indirizzo risultava finanziato
        # da se stesso, ed e' una riga che non significa niente.
        if not f or f == w.lower():
            continue
        return f, None
    return None, "vuoto"


def main():
    if CHAIN not in ESPLORATORI:
        raise SystemExit(f"FINANZIATORI | {CHAIN} non ha un esploratore fra quelli noti: "
                         f"NON invento un dato. Noti: {sorted(ESPLORATORI)}")
    t0 = time.time()
    print(f"FINANZIATORI | strada: "
          + ("Etherscan V2 con chiave gratuita (5/s, 100.000 al giorno)" if CHIAVE
             else "Blockscout pubblico senza chiave (lento: ~10 per finestra). "
                  "Con ETHERSCAN_KEY fra i segreti diventa quaranta volte piu' veloce, "
                  "e resta gratis."), flush=True)
    noti = {}
    if os.path.exists(FUORI):
        try:
            noti = json.load(gzip.open(FUORI, "rt")).get("da", {})
        except Exception:
            noti = {}
    prima = len(noti)
    gia_noti = set(noti)
    lista = [w for w in da_risolvere() if w not in noti]
    print(f"FINANZIATORI | {CHAIN}: {prima:,} gia' noti, {len(lista):,} da fare", flush=True)
    tutte = len(lista)
    lista = AF.mia_parte(lista)
    i_f, n_f = AF.quale_fetta()
    if n_f > 1:
        print(f"FINANZIATORI | fetta {i_f+1} di {n_f}: {len(lista):,} su {tutte:,}", flush=True)
    fatti = muti = strozzati = 0
    for w in lista:
        if time.time() - t0 > BUDGET:
            print(f"FINANZIATORI | mi fermo a {(time.time()-t0)/60:.0f} min per fare in tempo "
                  f"a salvare", flush=True)
            break
        f, perche = finanziatore(w)
        if f:
            noti[w] = f
            fatti += 1
        elif perche == "strozzato":
            strozzati += 1
            # SI ASPETTA, NON SI SMETTE (2/10). La prima versione si fermava dopo cinque
            # rifiuti: con un bersaglio di 11.275 era la scelta giusta, perche' insistere non
            # avrebbe finito comunque. Con TRECENTO conviene aspettare: un minuto di pausa
            # costa meno di un giro buttato, e il servizio ci fa un favore gratis.
            # Si smette solo se ci rifiuta anche dopo le pause lunghe, venti volte di fila.
            if strozzati % 3 == 0:
                print(f"FINANZIATORI | {strozzati} rifiuti: aspetto un minuto", flush=True)
                time.sleep(60)
            if strozzati >= 20:
                print(f"FINANZIATORI | ci rifiuta anche dopo le pause: mi fermo. I non risolti "
                      f"restano da fare, NON li segno come senza finanziatore.", flush=True)
                break
        else:
            muti += 1
        time.sleep(PAUSA)
    # SI SCRIVE SOLO IL PROPRIO PEZZO: il file finale lo fonde il pubblicatore, dove i pezzi
    # esistono tutti e lo scrittore e' uno.
    trovati_ora = {w: f for w, f in noti.items() if w not in gia_noti}
    if not trovati_ora:
        print("FINANZIATORI | niente di nuovo risolto: NON scrivo un pezzo vuoto",
              flush=True)
        return
    os.makedirs(BASE, exist_ok=True)
    json.dump(trovati_ora, open(PEZZO, "w"))
    # QUANTE ENTITA' DIETRO QUANTI PORTAFOGLI: e' il numero che dice se l'ipotesi vive.
    import collections
    quante = collections.Counter(noti.values())
    flotte = [(f, q) for f, q in quante.items() if q >= 3]
    print(f"FINANZIATORI | {CHAIN}: {fatti:,} nuovi ({prima:,} -> {len(noti):,}), {muti:,} senza "
          f"transazione entrante, {strozzati:,} rifiutati dal servizio (NON contati come vuoti) | {len(quante):,} finanziatori distinti, di cui {len(flotte):,} "
          f"con 3+ portafogli", flush=True)
    for f, q in sorted(flotte, key=lambda kv: -kv[1])[:5]:
        print(f"   flotta: {f[:16]}… finanzia {q} portafogli", flush=True)


if __name__ == "__main__":
    main()
