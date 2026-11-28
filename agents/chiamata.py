"""CHIAMATA — interrogare un contratto senza farsi ingannare da un vuoto.

IL DIFETTO (18/09). Il nodo pubblico di base, sotto raffica, risponde `"0x"` a una eth_call
PERFETTAMENTE VALIDA, senza segnalare alcun errore. Non e' "il contratto non ha quella funzione":
e' il nodo che cede e restituisce niente con l'aria di aver risposto.

QUANTO MI E' COSTATO: ho classificato 29 indirizzi di base come "non sono pool" con UNA sola
domanda ciascuno, li ho messi in quarantena e ho escluso la quarantena dal registro in produzione.
Riprovando con pause, 28 su 29 erano pool veri. Uno di essi aveva 95.600 scambi e 22.142 byte di
codice — la dimensione esatta di un pool Uniswap V3 — e alla stessa domanda ripetuta dieci volte
ha risposto nove volte su dieci.

LA REGOLA: un vuoto non e' una risposta finche' non lo si e' chiesto piu' volte. Qui si riprova
con pause crescenti, e si distingue in modo esplicito fra:
    valore          -> il contratto ha risposto
    None            -> NON LO SAPPIAMO (il nodo non ha risposto nemmeno dopo le riprove)
Chi chiama deve trattare None come "da riprovare", MAI come "no".

NOTA: eth_getLogs NON ha questo difetto — misurato lo stesso giorno, 15 raffiche su 15 e 12 su 12
hanno restituito risposte piene, e quando la domanda e' troppo larga il nodo rifiuta apertamente
con un 413. Il vuoto silenzioso e' un vizio della sola eth_call.
"""
import json
import time
import urllib.request


def eth_call(url, contratto, dati, tentativi=4, pausa=0.8, timeout=30):
    """Torna (valore, stato). Lo STATO va guardato, non dedotto dal valore.

        ("0x...", "ok")        il contratto ha risposto
        (None, "rifiutato")    il contratto NON ha quella funzione (il nodo lo dice: revert)
        (None, "ignoto")       il nodo non ci ha risposto nemmeno dopo le riprove

    "rifiutato" e "ignoto" NON sono la stessa cosa, ed e' proprio averli confusi a produrre i 28
    falsi positivi: un nodo che tace non e' un contratto che nega."""
    for k in range(tentativi):
        corpo = json.dumps({"jsonrpc": "2.0", "method": "eth_call",
                            "params": [{"to": contratto, "data": dati}, "latest"],
                            "id": 1}).encode()
        try:
            r = urllib.request.Request(url, data=corpo,
                                       headers={"Content-Type": "application/json",
                                                "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=timeout) as x:
                d = json.load(x)
            if "error" in d:
                return None, "rifiutato"         # il nodo dichiara: quella funzione non c'e'
            v = d.get("result")
            if v and v != "0x":
                return v, "ok"
            time.sleep(pausa * (k + 1))          # vuoto muto: puo' essere il nodo che cede
        except Exception:
            time.sleep(pausa * 1.5 * (k + 1))
    return None, "ignoto"


def e_un_pool(url, indirizzo):
    """True / False / None, dove None vuol dire NON MISURATO — e non si mette in quarantena."""
    a, sa = eth_call(url, indirizzo, "0x0dfe1681")
    b, sb = eth_call(url, indirizzo, "0xd21220a7")
    if sa == "ok" and sb == "ok":
        return len(a) >= 42 and len(b) >= 42
    if "ignoto" in (sa, sb):
        return None                              # il nodo ha taciuto: non si conclude niente
    return False                                 # il contratto ha negato entrambe: non e' un pool
