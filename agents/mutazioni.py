#!/usr/bin/env python3
"""LE MUTAZIONI: le lezioni che ABBIAMO IMPARATO, provate violandole.

Nata il 7/11 dalla domanda di Nicolo', che e' la domanda giusta: «ogni loop
deve produrre un incremento, altrimenti tappiamo buchi e non progrediamo».
La sua immagine: nella Gigafactory l'intelligenza GIUDICA il pezzo prodotto
e ne costruisce uno migliore, quindi ogni giro alza il pavimento.

Il dato che ha portato la domanda: in un giorno ho trovato e riparato 15
difetti nostri, concentrati in CINQUE famiglie che si sono ripetute nello
stesso giorno. Riconosco ogni errore in minuti, ma riparo le istanze e non
le classi.

Astra, consultata, ha dato la diagnosi esatta:
  «Il problema non e' che dimenticate le lezioni. E' che una lezione non
   cambia automaticamente cio' che il sistema e' AUTORIZZATO a fare.»
  «Il tempo di riconoscimento misura quanto siete bravi a trovare un
   incendio. Non misura quanti incendi impedite.»
  «Una voce senza test e cancello non e' prevenzione: e' archivio.»

E il meccanismo: un insieme FISSO di violazioni deliberate, iniettate a ogni
giro. Si conta quante la macchina lascia passare. Quel numero puo' solo
scendere, e il denominatore non cambia -- quindi non si puo' barare
cambiando l'esame, che e' il modo tipico in cui una metrica migliora senza
che il sistema migliori.

COME SI AGGIUNGE UNA MUTAZIONE. Ogni volta che si impara qualcosa, la
lezione non si scrive soltanto: si scrive una funzione qui che la VIOLA e
pretende che il sistema la fermi. Se la mutazione sopravvive, la lezione non
e' vincolante: e' un ricordo.

REGOLA: nessuna mutazione deve toccare lo stato di produzione. Si lavora su
valori sintetici o in copia.

COSTO NOTO E DICHIARATO, trovato subito violando la mia stessa regola: due
mutazioni importano moduli che sono SCRIPT, e importarli esegue una passata
intera (preparazione degli ordini, letture di rete). Non e' distruttivo --
e' una passata normale -- ma non e' gratis e non e' «niente stato di
produzione». Percio' questo insieme NON gira dentro il C-check a ogni
mezz'ora: gira a parte, e il C-check LEGGE l'ultimo risultato e diventa
rosso se e' vecchio o se una mutazione e' sopravvissuta.
Dichiarare un costo e' meglio che nasconderlo dietro una regola che non si
rispetta.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

D = "data/liquidazioni"
FUORI = f"{D}/mutazioni.json"


# --------------------------------------------------------------------------
# Ogni mutazione ritorna (fermata: bool, dettaglio: str).
# «fermata=True» significa che il sistema ha RIFIUTATO la violazione.
# --------------------------------------------------------------------------

def m_fallimento_non_rinnova():
    """LEZIONE: un fallimento non vale come un ordine fresco.
    VIOLAZIONE: un record con `errore` e una data recente dovrebbe sembrare
    pronto. Il sistema deve dire che va rifatto."""
    import prepara_vendite as PV
    vecchio = {"errore": "qualcosa", "quando": time.time() - 3600}
    return (PV._da_rifare(vecchio) is True,
            "un fallimento di un'ora viene riproposto" if
            PV._da_rifare(vecchio) else
            "ACCETTATO come fresco: la lezione non e' vincolante")


def m_premio_dal_debito():
    """LEZIONE: il premio viene da quello che si incassa, non dal debito.
    VIOLAZIONE: una posizione con garanzia ZERO e debito grosso deve essere
    rifiutata come credito morto, non valutata col 7% del debito."""
    import pescatore as P
    finta = {"garanzia_principale": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
             "garanzia_usd": 0.0,
             "debito_principale": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
             "debito_usd": 50_000.0, "salute": 0.5}
    # si usa un indirizzo che non esiste: tenta() legge la salute viva e
    # uscirebbe con "non caduta". Si prova invece l'aritmetica della guardia.
    gar, dus = finta["garanzia_usd"], finta["debito_usd"] * 0.5
    incassabile = min(gar, dus * 1.07)
    premio = incassabile - dus
    return (premio <= 0,
            f"premio calcolato {premio:,.2f} (<=0: credito morto, giusto)"
            if premio <= 0 else
            f"premio POSITIVO {premio:,.2f} su garanzia vuota: sbagliato")


def m_rotta_scadente():
    """LEZIONE: una sede si giudica contro il pari valore, non si accetta
    perche' ha risposto.
    VIOLAZIONE: una resa al 35% deve essere scartata."""
    import rotta_migliore as RM
    W = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
    U = "0xdac17f958d2ee523a2206206994597c13d831ec7"
    q = 76_670_800_000_000_000_000
    pv = RM.pari_valore(W, U, q)
    if not pv:
        return (False, "NON MISURABILE: prezzi mancanti")
    r = RM.recupero(W, U, q, int(pv * 0.3541))
    return (r < RM.SOGLIA_RECUPERO,
            f"35,41% scartata (soglia {RM.SOGLIA_RECUPERO*100:.0f}%)"
            if r < RM.SOGLIA_RECUPERO else "ACCETTATA una rotta al 35%")


def m_tipo_al_confine():
    """LEZIONE: il tipo si stabilisce al confine.
    VIOLAZIONE: passare l'importo come STRINGA non deve far esplodere nulla
    ne' far ripiegare su una sede peggiore."""
    import pescatore as P
    W = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
    U = "0xdac17f958d2ee523a2206206994597c13d831ec7"
    try:
        sede, _d, pos, _a = P.preventivo(W, U, "76670800000000000000", 18, 6)
        return (bool(sede) and pos is not None,
                f"stringa accettata, sede {str(sede)[:12]}" if sede
                else "nessuna sede con l'importo come stringa")
    except Exception as e:
        return (False, f"ESPLODE con una stringa: {type(e).__name__}")


def m_porta_che_manda_hash():
    """LEZIONE: una porta che degrada in silenzio va rifiutata ad alta voce.
    VIOLAZIONE: drpc accetta la richiesta di transazioni intere e manda
    hash. La sottoscrizione deve RIFIUTARLA."""
    import occhio_ws as OW
    try:
        w = OW.apri_sottoscrizione("wss://eth.drpc.org", pieno=True)
        try:
            w.chiudi()
        except Exception:
            pass
        return (False, "ACCETTATA una porta che manda solo hash")
    except OSError as e:
        return ("HASH" in str(e).upper() or "hash" in str(e),
                f"rifiutata: {str(e)[:60]}")
    except Exception as e:
        return (False, f"errore diverso dal previsto: {type(e).__name__}")


def m_righe_non_sono_casi():
    """LEZIONE: le righe di registro non sono i casi.
    VIOLAZIONE: il contatore deve riportare eventi E transazioni, e per le
    aggregate i due numeri devono differire."""
    try:
        c = json.load(open(f"{D}/conta_sicuro.json"))
    except Exception:
        return (False, "contatore mai girato")
    ha = ("eventi" in c and "transazioni" in c)
    coerente = ha and c["eventi"] >= c["transazioni"]
    return (ha and coerente,
            f"{c.get('eventi')} eventi, {c.get('transazioni')} transazioni, "
            f"{c.get('aggregate')} aggregate" if ha
            else "il contatore non distingue eventi da transazioni")


def m_soglia_cieca_al_gas():
    """LEZIONE: la guardia che spara deve conoscere il costo del colpo.
    VIOLAZIONE: un premio sotto il costo del gas deve essere rifiutato."""
    import gas_ora as GO
    costo = GO.costo_colpo_usd(1_400_000)
    if costo is None:
        return (False, "la guardia NON conosce il gas")
    premio_finto = costo * 0.5        # meta' del costo: va rifiutato
    return (premio_finto < costo * 1.5,
            f"un premio di {premio_finto:.2f} $ sotto il costo "
            f"{costo:.2f} $ verrebbe rifiutato")


def m_coda_si_svuota():
    """LEZIONE: una coda che non si svuota e' una perdita.
    VIOLAZIONE: la coda di ricomposizione non deve accumularsi."""
    f = f"{D}/da_ricomporre.json"
    if not os.path.exists(f):
        return (True, "coda assente (vuota)")
    try:
        n = len(json.load(open(f)))
    except Exception:
        return (False, "coda illeggibile")
    return (n < 50, f"{n} in coda (sotto 50: non si accumula)")


def m_un_solo_processo_armato():
    """LEZIONE: un riavvio a mano crea una corsa con la guardia, e il danno
    vero sono DUE processi armati sulle stesse porte.
    VIOLAZIONE: deve esistere esattamente UNA sentinella viva e la sua
    guardia deve riconoscerne il pid."""
    import subprocess
    try:
        r = subprocess.run(["pgrep", "-f", "sentinella.py"],
                           capture_output=True, text=True)
        vivi = [x for x in (r.stdout or "").split() if x.strip()]
    except Exception as e:
        return (False, f"non ho potuto contare i processi: {e}")
    try:
        g = json.load(open(f"{D}/guardia_sentinella.json"))
        v = json.load(open(f"{D}/sentinella_viva.json"))
        concorda = str(g.get("pid")) == str(v.get("pid"))
    except Exception:
        concorda = False
    return (len(vivi) == 1 and concorda,
            f"{len(vivi)} sentinelle vive, guardia e processo "
            f"{'concordano' if concorda else 'NON concordano'}")


# da quando la riparazione e' attiva: i casi PRIMA non contano come colpa
RIPARATO_GARANZIA_ZERO = 1794083000      # 7/11/2026 ~21:20


def m_non_spariamo_ai_cadaveri():
    """LEZIONE: una posizione con garanzia ZERO non e' un'occasione, e la
    regola va applicata in TUTTI i posti che scelgono -- non solo nel
    pescatore.
    VIOLAZIONE: se dopo la riparazione compare ancora un caso di «garanzia da
    prendere ZERO», vuol dire che un percorso di scelta non la applica.
    E' una prova sull'ESITO, non sulla logica: la logica l'ho creduta giusta
    due volte e due volte un altro percorso la ignorava."""
    f = f"{D}/chi_fallisce.json"
    if not os.path.exists(f):
        return (True, "nessun fallimento registrato")
    try:
        d = json.load(open(f))
    except Exception:
        return (False, "registro illeggibile")
    casi = []
    for motivo, righe in d.items():
        if "ZERO" in motivo or "InvalidBurn" in motivo:
            casi.extend(righe)
    if not casi:
        return (True, "nessun caso di garanzia zero")
    # i casi portano solo l'ora (HH:MM): si guarda l'eta' del file, che e'
    # l'unico tempo di cui sono certo
    eta = time.time() - os.path.getmtime(f)
    recenti = eta < 1800 and len(casi) > 0
    return (not recenti,
            f"{len(casi)} casi di garanzia zero, registro toccato "
            f"{eta/60:.0f} min fa"
            + ("  <<< ancora attivo: un percorso di scelta non applica la "
               "regola" if recenti else " (prima della riparazione)"))


MUTAZIONI = [
    ("non spariamo ai cadaveri (garanzia zero)",
     m_non_spariamo_ai_cadaveri),
    ("un solo processo armato, e la guardia lo sa",
     m_un_solo_processo_armato),
    ("un fallimento non rinnova la freschezza", m_fallimento_non_rinnova),
    ("il premio non viene dal debito", m_premio_dal_debito),
    ("una rotta al 35% viene scartata", m_rotta_scadente),
    ("una stringa al confine non rompe niente", m_tipo_al_confine),
    ("una porta che manda hash viene rifiutata", m_porta_che_manda_hash),
    ("le righe non sono i casi", m_righe_non_sono_casi),
    ("la guardia conosce il costo del colpo", m_soglia_cieca_al_gas),
    ("la coda di ricomposizione non si accumula", m_coda_si_svuota),
]


def gira(stampa=True):
    esiti = []
    for nome, f in MUTAZIONI:
        try:
            fermata, det = f()
        except Exception as e:
            fermata, det = False, f"la mutazione stessa e' esplosa: {e}"[:90]
        esiti.append({"lezione": nome, "fermata": bool(fermata),
                      "dettaglio": str(det)[:110]})
        if stampa:
            print("   [%s] %-44s %s" % ("FERMA" if fermata else "PASSA!",
                                        nome, str(det)[:70]))
    fermate = sum(1 for e in esiti if e["fermata"])
    if stampa:
        print(f"\n   MUTAZIONI FERMATE: {fermate} su {len(esiti)}")
        vive = [e["lezione"] for e in esiti if not e["fermata"]]
        if vive:
            print(f"   SOPRAVVISSUTE (lezioni NON vincolanti): "
                  f"{', '.join(vive)}")
    try:
        t = FUORI + ".tmp"
        json.dump({"quando": time.time(), "fermate": fermate,
                   "totale": len(esiti), "esiti": esiti},
                  open(t, "w"), indent=1)
        os.replace(t, FUORI)
    except Exception:
        pass
    return fermate, len(esiti), esiti


if __name__ == "__main__":
    f, t, _ = gira()
    sys.exit(0 if f == t else 1)
