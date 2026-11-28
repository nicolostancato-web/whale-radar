"""LA MECCANICA DI BASE, studiata prima di toccare un numero.

== IL MANDATO (Nicolo', 8/10/2026 sera) ==

La demo su Robinhood gira da se' e non ha bisogno di attenzione: serve un controllo per giro, non
«un sacco di calcoli». Quindi il tempo di attesa si usa per **una** preparazione limitata — non per
esplorare — su Base, il solo posto dove abbiamo gia' 159 MB di dati raccolti.

== PERCHE' LA MECCANICA E NON I DATI ==

Su Robinhood tutto quello che vale e' nato dal capire la meccanica di Pons: la soglia di 4,2 ETH,
la tassa anti-sniper del 99% nei primi 5 secondi, il pool che apre **esattamente** al prezzo di
chiusura della curva (mediana misurata 1,068x). Senza quelle tre cose avrei prodotto numeri senza
significato — e infatti i numeri prodotti prima di capirle li ho ritirati tutti.

Su Base la meccanica e' **un'altra**: non c'e' una curva di Pons, ci sono piattaforme di lancio
diverse, ognuna con le sue regole. Quindi non si copia il risultato: si ricomincia dalla meccanica.

== COSTO ==

ZERO: passa dall'abbonamento via `consulta_grok`, mai dalla chiave a consumo. Una domanda ogni tre
ore, in sottofondo, senza togliere un minuto alla demo.
"""
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ricerca_prelancio as RP                               # noqa: E402
import consulta_grok as CG                                   # noqa: E402

QUI = RP.QUI
REGISTRO = os.path.join(QUI, "data", "ricerca_base.json")
MIN_ORE = float(os.environ.get("MIN_ORE", "3"))

# A sotto-domande corte: le domande lunghe tornano troncate (misurato il 7/10, due volte su due).
PROGRAMMA = [
    ("quali_piattaforme", [
        "Su Base (chain id 8453), quali sono le piattaforme di lancio di memecoin piu' usate nel "
        "2026? Dammi i nomi e il link alla documentazione di ognuna.",
        "Qual e' la piattaforma di lancio con piu' volume su Base oggi? Dammi il dato e la fonte.",
    ]),
    ("come_si_gradua", [
        "Sulla principale piattaforma di lancio di Base: esiste una soglia che fa passare una "
        "moneta dalla curva al mercato vero? Quanto vale, in che valuta? Col link.",
        "Alla graduazione, il prezzo del nuovo mercato coincide con l'ultimo prezzo della curva, "
        "oppure c'e' un salto? Col link alla documentazione o al contratto.",
    ]),
    ("tassa_e_privilegi", [
        "Sulle piattaforme di lancio di Base esiste una tassa sui primi secondi dopo il lancio "
        "(anti-sniper)? Percentuale e durata, col link.",
        "Esistono indirizzi esentati da quella tassa, o posizioni privilegiate concesse al "
        "creatore? Col link.",
    ]),
    ("commissioni_e_liquidita", [
        "Quali commissioni si pagano comprando e vendendo sulla curva della principale "
        "piattaforma di lancio di Base, e chi le incassa? Col link.",
        "Alla graduazione la liquidita' viene bloccata? Esiste una funzione per sbloccarla? "
        "Col link.",
    ]),
    ("quanti_graduano", [
        "Che percentuale delle monete lanciate sulla principale piattaforma di Base arriva alla "
        "graduazione? Dammi il numero e come e' stato calcolato.",
        "Esistono misure pubblicate su quanto sale in mediana una moneta di Base dopo la "
        "graduazione? Col metodo dichiarato e il link.",
    ]),
    ("dati_pubblici_base", [
        "Quali fonti dati gratuite esistono per Base: endpoint RPC pubblici, limiti di blocchi "
        "per chiamata su eth_getLogs, explorer con API. Dammi i numeri e i link.",
        "Su Base, l'indirizzo del gestore dei pool di Uniswap v4 e il factory di Uniswap v3: "
        "dammi gli indirizzi, col link alla fonte.",
    ]),
]


def _registro():
    if os.path.exists(REGISTRO):
        try:
            d = json.load(open(REGISTRO))
            d.setdefault("fatte", [])
            d.setdefault("storia", [])
            return d
        except Exception:
            pass
    return {"fatte": [], "storia": [], "ultima": 0}


def main():
    r = _registro()
    ore = (time.time() - r.get("ultima", 0)) / 3600
    if ore < MIN_ORE:
        print(f"BASE | l'ultima e' di {ore:.1f} ore fa (minimo {MIN_ORE}): "
              f"{len(r['fatte'])}/{len(PROGRAMMA)} temi fatti.")
        return 0
    resta = [(n, d) for n, d in PROGRAMMA if n not in r["fatte"]]
    if not resta:
        print(f"BASE | programma finito: {len(PROGRAMMA)} temi studiati.")
        return 0
    nome, sotto = resta[0]
    print(f"BASE | tema {len(r['fatte'])+1}/{len(PROGRAMMA)}: {nome}", flush=True)
    pezzi, corte = [], 0
    t0 = time.time()
    for i, sd in enumerate(sotto, 1):
        print(f"   sotto-domanda {i}/{len(sotto)}…", flush=True)
        risp = CG.chiedi(sd, sforzo=os.environ.get("SFORZO_GROK", "high"), minuti=20)
        if not risp or len(risp) < 150:
            corte += 1
            pezzi.append(f"### {sd}\n\n_(risposta troppo corta o assente: "
                         f"{len(risp or '')} caratteri — da riprovare)_\n")
            continue
        pezzi.append(f"### {sd}\n\n{risp}\n")
    if corte == len(sotto):
        print("BASE | tutte le sotto-domande vuote: non segno il tema, il giro dopo ritenta.")
        return 0
    from datetime import datetime, timezone
    q = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    testo = (f"# Ricerca Grok — Base — {nome}\n\nModello grok-4.7. Costo: ZERO (abbonamento). "
             f"Tempo: {int(time.time()-t0)}s. {len(sotto)-corte}/{len(sotto)} con risposta.\n\n"
             f"---\n\n" + "\n".join(pezzi))
    f = os.path.join(QUI, f"RICERCA_BASE_{nome}_{q}.md")
    open(f, "w").write(testo)
    print(f"BASE | scritto {os.path.basename(f)} ({len(testo)} caratteri)", flush=True)
    RP._metti_al_sicuro(f)
    r["fatte"].append(nome)
    r["ultima"] = int(time.time())
    r["storia"].append({"tema": nome, "quando": int(time.time()),
                        "secondi": int(time.time() - t0), "vuote": corte})
    os.makedirs(os.path.dirname(REGISTRO), exist_ok=True)
    json.dump(r, open(REGISTRO, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
