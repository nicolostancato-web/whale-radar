#!/usr/bin/env python3
"""
METRO — il costo con cui si giudica OGNI cosa. Un posto solo, misurato, non assunto.

Decisione dell'investitore del 03/09/2026 (vedi DECISIONS.md).

Il problema che risolve: per giorni abbiamo detto "i costi li abbiamo misurati" e poi nei conti
ne abbiamo usato un altro. Misurato su Jupiter: 4,1% di andata e ritorno a $25. Usato nel
backtest: ~33%. Otto volte piu' severo. Con quel 33% un token doveva salire del 50% solo per
pareggiare, e con quel metro abbiamo dichiarato morte quattro chain e diverse strategie.
Nessuno di quei verdetti era una scoperta: erano assunzioni travestite da risultati.

Come funziona adesso:
  METRO=vero    (default)  costo MISURATO — quello che paghi davvero quando riesci a uscire
  METRO=stress             il vecchio 33% — resta come scenario pessimistico, non come verita'

Il vecchio numero non si butta: diventa uno stress test. Cosi' non perdiamo la prudenza,
smettiamo solo di spacciarla per misura. Stesso schema che usiamo gia' per la percentuale
robusta: il numero onesto e' quello primario, il severo resta come prova di tenuta.

ATTENZIONE — cosa NON e' incluso qui, di proposito:
Le trappole (12% a $25: token da cui non esci, o esci con nulla) NON sono spalmate su questo
costo. Sono una perdita totale, non una percentuale, e vanno contate a parte: sommarle qui
significherebbe punire ogni singolo trade con un pezzo del disastro altrui — che e' esattamente
l'errore del 33% piatto. Il conteggio delle trappole vive in COSTO_MODELLO.md.
"""
import json, os

MODO = os.environ.get("METRO", "vero").lower()
_MIS = "data/costo_modello.json"
_TAGLIA = os.environ.get("TAGLIA_USD", "25")     # posizione di riferimento: piccola, ed e' un bene

# QUANTO SI PROSCIUGA IL POOL QUANDO SCAPPI (03/09, dall'audit avversariale).
# Il primo tentativo divideva il costo di andata e ritorno a meta' fra entrata e uscita. Sbagliato per
# due motivi, e il secondo e' grave:
#   1. l'asimmetria e' MISURATA, non va assunta: a $25 l'acquisto costa 2,76% e la vendita 1,07%
#      (l'opposto di quello che avevo ipotizzato — un motivo in piu' per misurare invece di dedurre)
#   2. quelle quote sono prese in CALMA, su token vivi. Ma lo stop scatta esattamente quando tutti
#      vendono e chi fa mercato ritira i soldi dal pool: in quel momento la profondita' e' il 20-50%
#      di quella misurata, e l'impatto sale almeno in proporzione inversa.
# Non e' un dettaglio prudenziale: e' la differenza fra misurare il costo di uscire e misurare il
# costo di uscire QUANDO VUOI USCIRE TU. Sono due numeri diversi, e conta solo il secondo.
# Il moltiplicatore resta un'assunzione dichiarata — la piu' conservativa dell'intervallo stimato.
FUGA = float(os.environ.get("FUGA", 3.0))       # uscite in stop/trailing: pool prosciugato ~3x
FUGA_MAX = 0.60                                  # tetto: oltre, il trade e' fantascienza

# lo scenario pessimistico storico (com'era prima del 03/09)
STRESS = {"ES": 0.15, "XS": 0.15, "FEE": 0.01, "GAS": 0.014, "SIZE": 2.0, "LAT": 0.08}
# fallback prudente se le misure non ci sono ancora: meta' strada, mai il piu' ottimistico
DEFAULT_VERO = {"ES": 0.03, "XS": 0.03, "FEE": 0.01, "GAS": 0.014, "SIZE": 25.0, "LAT": 0.08}


def _misurato():
    """le due gambe misurate separatamente, piu' la gamba d'uscita nel caso in cui scappi."""
    try:
        d = json.load(open(_MIS))["taglie"][_TAGLIA]
        n = d.get("vendibili") or 0
        if n < 25: return None                   # sotto 25 misure non ci si fida: si resta prudenti
        acq = d.get("impatto_acquisto_mediano")
        ven = d.get("impatto_vendita_mediano")
        ven75 = d.get("impatto_vendita_p75")
        c = d.get("costo_mediano")
        if acq is None or ven is None:           # archivio vecchio: ripiego sul roundtrip diviso
            if c is None: return None
            acq = ven = ven75 = c / 2.0
        p = {**DEFAULT_VERO, "SIZE": float(_TAGLIA)}
        p["ES"] = max(0.005, acq)                                    # entri con calma
        p["XS"] = max(0.005, ven)                                    # esci a target: mercato normale
        p["XS_FUGA"] = min(FUGA_MAX, max(0.01, (ven75 or ven) * FUGA))  # esci in stop: pool prosciugato
        return p
    except Exception:
        return None


P = STRESS if MODO == "stress" else (_misurato() or DEFAULT_VERO)
MISURATO = MODO != "stress" and _misurato() is not None
ES = P["ES"]; XS = P["XS"]; FEE = P["FEE"]; GAS = P["GAS"]; SIZE = P["SIZE"]; LAT = P["LAT"]
XS_FUGA = P.get("XS_FUGA", XS)      # quanto costa uscire quando stai scappando, non quando scegli tu


def _curva():
    try:
        c = json.load(open(_MIS)).get("curva")
        return c if c and c.get("usabile") and c.get("fasce") else None
    except Exception:
        return None


CURVA = _curva()


def uscita_liquidita(volume_ora, size=None, fuga=False):
    """Il costo di uscita SECONDO QUANTO E' LIQUIDO il token in quel momento (03/09, curva misurata
    su 796 osservazioni). Non una costante: su un pool che gira 50.000 l'ora uscire con 25 dollari
    non si sente; sullo stesso token col volume crollato a 200, quei 25 dollari sono meta' del
    mercato — e lo stop scatta proprio li'.
    Fuori dalla fuga si usa il costo tipico della fascia; in fuga il suo caso peggiore, perche'
    quando scappi non sei l'unico e il pool si e' gia' assottigliato."""
    if not CURVA: return uscita(fuga)
    s = float(size or SIZE)
    r = s / max(1.0, float(volume_ora or 0) + 1.0)
    scelta = CURVA["fasce"][-1]
    for f in CURVA["fasce"]:
        if r <= f["rapporto_a"]: scelta = f; break
    roundtrip = scelta["costo_p75"] if fuga else scelta["costo_mediano"]
    # il roundtrip misurato copre entrata+uscita: qui serve la sola gamba d'uscita
    return min(FUGA_MAX, max(0.005, roundtrip * (XS / max(1e-6, ES + XS))))


def uscita(fuga=False):
    """lo slippage in uscita. `fuga` = stai uscendo perche' il prezzo ti sta scappando (stop o
    trailing), non perche' hai raggiunto il tuo obiettivo. Sono due mercati diversi."""
    return XS_FUGA if fuga else XS


def pareggio(fuga=False):
    """quanto deve salire un token perche' il trade vada in pari, con questo metro."""
    u = uscita(fuga)
    return (1 + (GAS * 2) / SIZE) * ((1 + ES) * (1 + FEE)) / ((1 - u) * (1 - FEE) * (1 - LAT))


def etichetta():
    return (f"metro={'STRESS (33% assunto)' if MODO == 'stress' else 'VERO (misurato)'} · "
            f"{'curva liquidità ATTIVA' if CURVA else 'curva non ancora usabile'} · "
            f"entrata {ES*100:.1f}% · uscita a target {XS*100:.1f}% · uscita in fuga {XS_FUGA*100:.1f}% · "
            f"pareggio {pareggio():.2f}x (in fuga {pareggio(True):.2f}x)"
            + ("" if MISURATO or MODO == "stress" else " · ⚠️ misure insufficienti, uso il prudente"))


if __name__ == "__main__":
    print(etichetta())
