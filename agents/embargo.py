#!/usr/bin/env python3
"""
EMBARGO — quanto indietro deve guardare una decisione, FONTE PER FONTE.

LA DECISIONE (15/09, delegata da Nicolò dopo tre giorni di discussione).

Il problema. Per simulare onestamente una decisione presa alle 15:00 si possono usare solo le
informazioni che alle 15:00 avevamo davvero. Fin qui la regola era UNA SOLA per tutto: 35,4 ore.
Nasceva da una misura vera — quanto tardi i fornitori ci consegnano i dati — ma prendeva il PEGGIORE
fra le chain, e il peggiore era BSC: una chain abbandonata il 9 settembre. Una chain morta decideva
per tutte le altre.

Conseguenza misurata: l'entrata e' a +3h dalla nascita del token, quindi il sistema cercava dati di
32 ore prima che il token esistesse. Il 92% delle righe aveva le variabili sugli scambi vuote. Il
modello che credevamo guardasse dieci cose ne guardava sei.

LA DECISIONE, in una riga: l'embargo smette di essere un numero scritto a mano e diventa una
proprieta' DELLA FONTE del singolo dato.

  - dato dai FORNITORI (API): il ritardo misurato di quella chain. Non il peggiore di tutte: il suo.
  - dato dalla CATENA (lo leggiamo noi): il tempo che impieghiamo NOI a leggerlo.

PERCHE' NON ZERO PER LA CATENA, che sarebbe la risposta comoda. Perche' dire "zero" significherebbe
sostenere di conoscere un blocco nell'istante in cui nasce, e non e' vero: lo conosciamo quando il
nostro collettore passa di li'. Quel passaggio ha una cadenza, e la cadenza si misura. Mettiamo
MEZZ'ORA, che e' piu' lento di quanto facciamo davvero: se sbagliamo, sbagliamo per prudenza.

  "Un embargo troppo stretto costa occasioni. Un embargo troppo largo costa soldi veri."

COSA NON FACCIAMO, ed e' la parte importante. NON riscriviamo il passato. Il metro vecchio resta
congelato con il suo nome; questo nasce accanto, con il suo. Ogni risultato dira' con quale metro e'
stato misurato, e non si confrontano mai numeri di metri diversi.
Non e' una correzione della storia: e' un secondo strumento, dichiarato.
"""
import json, os

VERSIONE = "v3-disponibilita-operativa"
CATENA_S = int(os.environ.get("EMBARGO_CATENA", 1800))     # mezz'ora, prudente
DIFETTO_S = 10 * 3600                                      # se non sappiamo, 10h come le chain vive


def _misurati():
    try:
        d = json.load(open("data/ritardo_reale.json")).get("ritardi") or {}
        return {k: int(v.get("tipico_s") or 0) for k, v in d.items() if v.get("tipico_s")}
    except Exception:
        return {}


_M = _misurati()
# BSC NON CONTA (e' abbandonata dal 9/9): il suo ritardo non deve decidere per le chain vive.
VIVE = ("base", "solana", "robinhood")


# IL RITARDO MISURATO RIGUARDA LE CANDELE, NON GLI SCAMBI (15/09).
# data/ritardo_reale.json nasce da agents/disponibilita.py, che misura «la distanza fra il momento a
# cui una CANDELA si riferisce e il momento in cui l'abbiamo in casa». Applicarlo agli SCAMBI e' lo
# stesso errore di categoria che ci ha fatto usare il ritardo di BSC per Base: si prende un numero
# vero, misurato su una cosa, e lo si applica a un'altra.
# Per gli scambi il ritardo non l'abbiamo ancora misurato — e non si puo' misurare all'indietro,
# serve il registro prospettico nato ieri. Finche' manca, si usa il vincolo che NON dipende da una
# misura: non si puo' leggere la storia di un pool prima di sapere che esiste.
TIPI_MISURATI = ("candele",)


def per_fonte(chain, fonte=None):
    """Quanti secondi deve essere vecchio un dato di questa fonte per poter essere usato."""
    if fonte == "catena":
        return CATENA_S
    v = _M.get(chain)
    if v: return v
    vivi = [_M[c] for c in VIVE if c in _M]
    return max(vivi) if vivi else DIFETTO_S


_SCOPERTA = {}


def scoperto_il(chain, pool):
    """Quando ABBIAMO SAPUTO che quel pool esisteva. E' il vincolo che mancava."""
    if chain not in _SCOPERTA:
        try:
            d = json.load(open(f"data/multichain/{chain}/pools.json"))
            _SCOPERTA[chain] = {k.lower(): (v or {}).get("seen") for k, v in d.items()}
        except Exception:
            _SCOPERTA[chain] = {}
    return _SCOPERTA[chain].get((pool or "").lower())


def utilizzabile(scambio, entrata, chain, pool=None):
    """La domanda vera: alle 'entrata' avevamo gia' questo scambio?

    LA CORREZIONE CHE IL REVISORE HA IMPOSTO (15/09). La prima versione chiedeva solo che il blocco
    fosse abbastanza vecchio. Sbagliata, e lui l'ha smontata in una riga:

        «acq dimostra che quei dati sono entrati adesso, settimane dopo il blocco.
         Non prova che fossero disponibili dopo 30 minuti: per quei record prova il contrario.»

    Ci sono TRE cose diverse, e io ne stavo usando la piu' comoda:
      1. il nodo oggi puo' servire quel log          (disponibilita' fisica)
      2. il nodo lo avrebbe servito allora           (disponibilita' del nodo)
      3. NOI sapevamo che quel pool esisteva e lo stavamo interrogando   (disponibilita' OPERATIVA)

    Solo la terza conta. Non si puo' leggere la storia di un pool di cui non si sa l'esistenza: se
    l'abbiamo scoperto dieci ore dopo la nascita — perche' ce l'ha detto un fornitore, col suo
    ritardo — allora i suoi primi scambi NON erano nostri prima di quel momento, per quanto la
    catena li conservasse.

    Quindi un dato e' disponibile dal PIU' TARDI fra: quando e' successo, e quando abbiamo saputo
    che quel pool esisteva. Piu' il tempo che ci mettiamo a leggerlo."""
    ts = scambio.get("ts")
    if not ts: return False
    latenza = per_fonte(chain, scambio.get("fonte"))
    quando_lo_avevamo = ts + latenza
    if scambio.get("fonte") == "catena" and pool:
        visto = scoperto_il(chain, pool)
        if visto:
            quando_lo_avevamo = max(quando_lo_avevamo, visto + CATENA_S)
        else:
            # non sappiamo quando l'abbiamo scoperto: non si indovina, si applica il ritardo del
            # fornitore, che e' il modo in cui i pool ci arrivano.
            quando_lo_avevamo = max(quando_lo_avevamo, ts + per_fonte(chain))
    return quando_lo_avevamo <= entrata


def stato_conoscenza(chain):
    """Cosa sappiamo davvero, e cosa no. Serve a non spacciare un'assunzione per una misura."""
    return {
        "ritardo candele": f"{_M.get(chain, 0)/3600:.1f}h — MISURATO",
        "ritardo scambi": "NON MISURATO — serve il registro prospettico",
        "vincolo usato per gli scambi": "quando abbiamo scoperto il pool (disponibilita' operativa)",
        "classe dei record storici": "ricostruzione-storica, non certificati point-in-time",
    }


def etichetta(chain):
    return (f"embargo {VERSIONE} · fornitori {per_fonte(chain)/3600:.1f}h · "
            f"catena {CATENA_S/3600:.2f}h")


if __name__ == "__main__":
    print(f"EMBARGO {VERSIONE}")
    print(f"  ritardi misurati: " + ", ".join(f"{k} {v/3600:.1f}h" for k, v in sorted(_M.items())))
    print(f"  BSC esclusa dal calcolo: e' abbandonata")
    for c in VIVE:
        print(f"  {c:10} fornitori {per_fonte(c)/3600:5.1f}h | catena {per_fonte(c,'catena')/3600:5.2f}h")
    print(f"\n  vecchio metro (congelato, non toccato): 35.4h per tutto")
    print("\n  COSA SAPPIAMO DAVVERO:")
    for k, v in stato_conoscenza("base").items():
        print(f"    {k:34} {v}")
