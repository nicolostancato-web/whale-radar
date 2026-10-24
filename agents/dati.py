"""Carica l'insieme di analisi SEPARANDO cio' che si sa prima di comprare da cio' che si sa dopo.

L'ERRORE CHE LO FA NASCERE, commesso DUE VOLTE IN DUE GIORNI (27 e 28/09).

 · 27/09: «i pool dove passano oltre 10.000 dollari rendono +24,9%». Vero, e inutile: quel volume
   si conosce DOPO aver comprato. Stavo dicendo che i sopravvissuti sopravvivono.
 · 28/09: identico, con un dato diverso. Condizionando sul denaro uscito dopo l'entrata il fondale
   risultava +15,0%; con il denaro visto PRIMA e' **-12,1%**. Ventisette punti di differenza fra
   guardare il futuro e non guardarlo.

La seconda volta me ne sono accorto prima di riportarlo, ma solo perche' me lo ricordavo. E le cose
che mi ricordo le violo: e' il difetto che ho dimostrato piu' volte di tutti.

**Quindi qui non c'e' una regola: c'e' un dato che si rifiuta.** Chi chiede le caratteristiche non
riceve i campi dell'esito, e se prova a filtrarci sopra ottiene un errore invece di un numero.

Per usare l'esito bisogna chiederlo a voce alta (`con_esito=True`), e quello e' il momento in cui
ci si ricorda che lo si sta usando.
"""
import gzip
import json
import os

# Cio' che si conosce AL MOMENTO DELLA DECISIONE: tutte le caratteristiche del flusso piu' questi.
PRIMA = {"_pool", "_t", "_valuta_prima", "_liq_prima", "_liq_copertura", "_giudicabile"}

# Cio' che si conosce SOLO DOPO: filtrarci sopra significa guardare il futuro.
DOPO = {"_uscita", "_uscita_min1", "_uscita_pesata", "_rend", "_max_vendibile",
        "_valuta_venduta", "_valuta_sopra_2x", "_valuta_sopra_5x", "_valuta_sopra_10x",
        "_vendite_dopo", "_scambi_dopo", "_ore_osservate",
        # la simulazione di vendita e i suoi riempimenti: sono ESITI, si misurano e non si filtrano
        "_uscita_25", "_uscita_50", "_riempito_25", "_riempito_50",
        "_uscita_25_ritardo", "_uscita_50_ritardo", "_uscita_100_ritardo",
        "_uscita_500_ritardo", "_uscita_2000_ritardo",
        "_uscita_100", "_uscita_500", "_uscita_2000",
        "_riempito_100", "_riempito_500", "_riempito_2000",
        # IL CAMMINO E' UN «DOPO» (29/09): serve a simulare QUANDO USCIRE, che e'
        # legittimo perche' usa cio' che si sa in quel momento. Ma come criterio di SCELTA
        # sarebbe la solita selezione col senno di poi, quindi vive di la'.
        "_cammino", "_cammino_in_dollari"}


class RigaSenzaEsito(dict):
    """Una riga senza i campi dell'esito. Chiederli non da' None: da' un errore che si vede."""

    def __missing__(self, k):
        if k in DOPO:
            raise KeyError(
                f"«{k}» si conosce solo DOPO aver comprato: filtrarci sopra e' guardare il futuro. "
                f"Se ti serve davvero come ESITO (non come filtro), carica con con_esito=True.")
        raise KeyError(k)


def carica(chain, con_esito=False, giudicabili=True, orizzonte_ore=24):
    p = f"data/loop1/insieme_{chain}.jsonl.gz"
    if not os.path.exists(p):
        return []
    righe = [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]
    if not righe:
        return []
    fine = max(x["_t"] + x.get("_ore_osservate", 0) * 3600 for x in righe)
    fuori = []
    for x in righe:
        if giudicabili and fine - x["_t"] < orizzonte_ore * 3600:
            continue
        if con_esito:
            fuori.append(x)
        else:
            fuori.append(RigaSenzaEsito({k: v for k, v in x.items() if k not in DOPO}))
    return fuori


def esiti(chain, **kw):
    """Le sole colonne dell'esito, nello stesso ordine di `carica`. Si usano per MISURARE, mai per
    scegliere: tenerle separate rende visibile quando si sta facendo l'una o l'altra cosa."""
    return [{k: x.get(k) for k in DOPO} for x in carica(chain, con_esito=True, **kw)]
