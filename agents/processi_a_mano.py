"""I processi lanciati a mano su questo Mac: il punto cieco delle guardie.

PERCHE' ESISTE (11/10). Ho trovato un `while true` acceso il 9 ottobre alle 05:12 e rimasto in
piedi quarantaquattro ore. Chiamava due agenti della fase chiusa in loop e competeva per lo
STESSO nodo RPC con la prova in avanti, cioe' con la sola cosa che stiamo accumulando.

Nessuna guardia lo aveva visto, e per una ragione strutturale: **tutte le nostre guardie guardano
le corsie di GitHub, e quello girava qui.** Un processo lanciato a mano e' invisibile al sistema
di controllo — ed e' precisamente la categoria di cose che si accumulano e poi «girano a caso»,
come dice Nicolo'.

Quindi: si elencano i processi di questo progetto, si confrontano con un registro di quelli
ATTESI, e si grida su quelli che nessuno ha dichiarato. Chi dura piu' di un'ora senza essere
dichiarato e' un sospetto, non un dettaglio.
"""
import json
import os
import re
import subprocess
import sys
import time

REGISTRO = "data/processi_attesi.json"
ORE_SOSPETTE = 1.0

# Quello che e' normale trovare acceso. Un processo non in questo elenco va spiegato o fermato.
ATTESI = [
    {"modello": "dal_di_fuori.sh", "cosa": "la maglia dei controlli, lanciata da me a ogni giro",
     "ore_massime": 1.0},
    {"modello": "agents/prova_in_avanti.py", "cosa": "la prova in avanti: l'accumulo",
     "ore_massime": 1.0},
    {"modello": "agents/cammino_posizioni.py", "cosa": "il database del cammino", "ore_massime": 1.0},
    {"modello": "agents/chi_vende_nel_dump.py", "cosa": "chi vende nei crolli", "ore_massime": 1.0},
    {"modello": "agents/ricerca_venditori.py", "cosa": "la ricerca di Grok sui venditori",
     "ore_massime": 2.0},
    {"modello": "agents/consulta_grok.py", "cosa": "una domanda a Grok in corso", "ore_massime": 2.0},
    {"modello": "agents/consulta_astra.py", "cosa": "una consulenza in corso", "ore_massime": 1.0},
    {"modello": "agents/dove_si_perde.py", "cosa": "il controllo sulle perdite", "ore_massime": 0.5},
    {"modello": "agents/quanto_cresce.py", "cosa": "il metro della crescita", "ore_massime": 0.5},
    {"modello": "agents/revisione_struttura.py", "cosa": "la revisione della struttura",
     "ore_massime": 0.5},
    {"modello": "agents/manifesto.py", "cosa": "il manifesto", "ore_massime": 0.5},
    {"modello": "agents/custode_memoria.py", "cosa": "il custode della memoria", "ore_massime": 0.5},
]


def _eta_in_ore(e):
    """L'eta' che `ps` scrive come [[gg-]hh:]mm:ss."""
    e = e.strip()
    g = 0
    if "-" in e:
        d, e = e.split("-", 1)
        g = int(d)
    p = [int(x) for x in e.split(":")]
    while len(p) < 3:
        p.insert(0, 0)
    return g * 24 + p[0] + p[1] / 60 + p[2] / 3600


def guarda():
    r = subprocess.run(["ps", "-eo", "pid,etime,command"], capture_output=True, text=True)
    nostri = []
    for l in r.stdout.splitlines()[1:]:
        m = re.match(r"\s*(\d+)\s+(\S+)\s+(.*)$", l)
        if not m:
            continue
        pid, eta, cmd = m.group(1), m.group(2), m.group(3)
        if "grep" in cmd or "processi_a_mano" in cmd:
            continue
        if not re.search(r"agents/|whale-radar|dal_di_fuori", cmd):
            continue
        nostri.append({"pid": int(pid), "ore": _eta_in_ore(eta), "comando": cmd[:160]})
    return nostri


def main():
    nostri = guarda()
    sospetti = []
    for p in nostri:
        att = next((a for a in ATTESI if a["modello"] in p["comando"]), None)
        if att is None:
            sospetti.append((p, "NON DICHIARATO: nessuno lo attende"))
        elif p["ore"] > att["ore_massime"]:
            sospetti.append((p, f"dichiarato ({att['cosa']}) ma gira da {p['ore']:.1f}h, "
                                f"il massimo atteso e' {att['ore_massime']}h"))
    print(f"PROCESSI | {len(nostri)} processi del progetto accesi su questo Mac")
    for p, perche in sospetti:
        print(f"   SOSPETTO pid {p['pid']} ({p['ore']:.1f}h): {perche}")
        print(f"      {p['comando'][:120]}")
    if not sospetti:
        print("PROCESSI | tutti dichiarati e dentro il loro tempo")
    json.dump({"quando": int(time.time()), "accesi": nostri,
               "sospetti": [{"pid": p["pid"], "ore": round(p["ore"], 2), "perche": q}
                            for p, q in sospetti]},
              open(REGISTRO, "w"), indent=1)
    # un sospetto che dura da ore va fra gli allarmi, non solo nel log
    gravi = [(p, q) for p, q in sospetti if p["ore"] > ORE_SOSPETTE]
    if gravi:
        try:
            with open("data/allarmi_da_leggere.jsonl", "a", buffering=1) as f:
                for p, q in gravi:
                    f.write(json.dumps({"quando": int(time.time()), "da": "processi_a_mano",
                                        "testo": f"pid {p['pid']} da {p['ore']:.1f}h: {q} — "
                                                 f"{p['comando'][:120]}"}) + "\n")
            print(f"PROCESSI | {len(gravi)} allarmi scritti")
        except Exception as e:
            print(f"PROCESSI | non riesco a scrivere l'allarme: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
