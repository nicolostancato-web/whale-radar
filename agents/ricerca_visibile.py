"""LA RICERCA SUL MONDO CHE VEDIAMO: la curva di Pons, chi ci gioca, e come si misura.

== IL MANDATO (Nicolo', 7/10/2026, sera) ==

«Grok ha girato due o tre giorni per quell'altro 50%. Pero' se possiamo usare Grok per cercare
delle informazioni in X riguardanti il NOSTRO 50%, cioe' comunque lo sfruttiamo: lui va a leggere
dei documenti e proviamo. Perche' secondo me anche in questo 50%, piu' informazioni abbiamo
sempre meglio e'.»

Giusto, e c'e' un motivo preciso oltre al «piu' informazioni e' meglio»: **abbiamo dei buchi
dichiarati nelle nostre misure** che un documento ufficiale chiuderebbe in un colpo. Il piu'
grosso sta scritto dentro `storie_complete.py`: gli indirizzi esentati dalla tassa dei primi
cinque secondi (fino a 32 per lancio) NON sono esclusi dalle nostre classifiche, e quelli non
sono bravi — sono privilegiati. Se la regola e' pubblicata, la nostra misura migliora stasera.

Quindi queste domande non sono curiosita': ognuna, se ha risposta, cambia un numero che diamo.

== DOVE GIRA, E PERCHE' NON NEL CIELO ==

Solo da questo Mac: il programma `grok` e' autenticato qui, sull'abbonamento gia' pagato. Da
GitHub Actions userebbe la chiave a consumo di xAI, che e' precisamente l'errore da 77 euro di
maggio (e il 5/10 l'ho rifatto per sbaglio). Costo di questa ricerca: ZERO.
"""
import glob
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ricerca_prelancio as RP                               # noqa: E402

QUI = RP.QUI
REGISTRO = os.path.join(QUI, "data", "ricerca_visibile.json")
MIN_ORE = float(os.environ.get("MIN_ORE", "3"))

# Ordinate per quanto cambiano un numero che diamo OGGI, non per curiosita'.
# A SOTTO-DOMANDE CORTE, NON A FASCICOLI (7/10 notte). Due giri su due, la domanda lunga e'
# tornata TRONCATA: solo il preambolo, 300-440 caratteri. Diagnosticato per esclusione, non per
# intuizione: una domanda corta che richiede ricerca sul web funziona perfettamente (mi ha dato
# il gas token di Robinhood Chain col link, 425 caratteri pieni); la stessa domanda lunga si
# ferma, a sforzo alto e a sforzo medio. E' un tetto sull'uscita, non un problema di ricerca.
# Quindi ogni tema e' una LISTA di domande corte: Grok risponde a ciascuna, e il fascicolo lo
# assemblo io. Costa qualche minuto in piu' e rende un documento invece di un preambolo.
PROGRAMMA = [
    ("tassa_e_esenti", [
        "Sulla curva di Pons di Robinhood Chain: esiste una tassa anti-snipe nei primi secondi "
        "dopo il lancio? Dimmi la percentuale e per quanti secondi vale, col link alla fonte.",
        "Sulla curva di Pons: esistono indirizzi ESENTATI dalla tassa anti-snipe? Quanti per "
        "lancio, chi li scegle, e come si leggono dalla transazione di creazione? Col link.",
        "Sulla curva di Pons: qual e' la commissione normale di acquisto e di vendita, e chi la "
        "incassa? Col link alla fonte ufficiale.",
        "Sulla curva di Pons: quale soglia fa 'graduare' una moneta e cosa succede esattamente "
        "alla graduazione? Col link.",
    ]),
    ("grappoli_e_bundler", [
        "Comprare per molti portafogli in UNA transazione sulle piattaforme di lancio memecoin: "
        "come si chiama questa pratica e quali strumenti pubblici la fanno? Nomi e link.",
        "Quali metodi pubblicati esistono per riconoscere dalla blockchain che piu' portafogli "
        "sono controllati dallo stesso operatore? Elencali con una riga ciascuno e i link.",
        "Gli strumenti di bundling distribuiscono le vendite su piu' blocchi per non far "
        "crollare il prezzo? Con quali parametri tipici? Col link.",
    ]),
    ("chi_pubblica_vincite", [
        "Su X, chi pubblica guadagni su Robinhood Chain o su Pons mostrando l'indirizzo del "
        "portafoglio o il link alla transazione? Dammi i profili e un esempio di post.",
        "Esistono classifiche pubbliche di portafogli vincenti su Robinhood Chain? Dammi i link "
        "e di' se i dati sono controllabili sulla chain.",
    ]),
    ("dove_stanno_le_x", [
        "Esistono misure pubblicate sul percorso del prezzo delle memecoin DOPO la graduazione "
        "su piattaforme di lancio EVM: quota che supera 2x, 5x, 10x? Dammi fonti e numeri.",
        "Qual e' la quota di memecoin che va praticamente a zero dopo la graduazione, secondo "
        "misure pubblicate? Col metodo dichiarato e il link.",
        "Quanto tempo passa in mediana fra la graduazione e il prezzo massimo, secondo misure "
        "pubblicate? Col link.",
    ]),
    ("chi_compra_il_primo_blocco", [
        "Robinhood Chain ha un mempool pubblico o le transazioni passano da un sequencer "
        "privato? Col link alla documentazione.",
        "Come si riesce tecnicamente a comprare nel blocco stesso del lancio di una moneta su "
        "una chain EVM? Elenca i modi documentati, con i link.",
    ]),
    ("dati_pubblici_robinhood", [
        "Quali fonti di dati pubbliche e gratuite esistono per Robinhood Chain (explorer con "
        "API, indicizzatori)? Dammi endpoint e limiti di chiamata, coi link.",
        "L'explorer di Robinhood Chain ha condizioni d'uso che vietano l'accesso automatico "
        "alle sue API? Citami il passaggio e il link.",
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
        print(f"VISIBILE | l'ultima e' di {ore:.1f} ore fa (minimo {MIN_ORE}): non ne chiedo "
              f"un'altra. {len(r['fatte'])}/{len(PROGRAMMA)} domande fatte.")
        return 0
    resta = [(n, d) for n, d in PROGRAMMA if n not in r["fatte"]]
    if not resta:
        print(f"VISIBILE | programma finito: {len(PROGRAMMA)} domande fatte.")
        return 0
    nome, domanda = resta[0]
    print(f"VISIBILE | domanda {len(r['fatte'])+1}/{len(PROGRAMMA)}: {nome}", flush=True)

    sys.path.insert(0, os.path.join(QUI, "agents"))
    import consulta_grok as CG
    pezzi, corte = [], 0
    t0 = time.time()
    for i, sd in enumerate(domanda, 1):
        print(f"   sotto-domanda {i}/{len(domanda)}…", flush=True)
        risp = CG.chiedi(sd, sforzo=os.environ.get("SFORZO_GROK", "high"), minuti=20)
        if not risp or len(risp) < 150:
            # una risposta sotto i 150 caratteri non e' una risposta: si conta e si dice
            corte += 1
            pezzi.append(f"### {sd}\n\n_(risposta troppo corta o assente: {len(risp or '')} "
                         f"caratteri — da riprovare)_\n")
            continue
        pezzi.append(f"### {sd}\n\n{risp}\n")
    testo = (f"# Ricerca Grok — {nome}\n\nModello grok-4.7. Costo: ZERO (abbonamento, nessuna "
             f"chiave API). Tempo: {int(time.time()-t0)}s. "
             f"{len(domanda)-corte}/{len(domanda)} sotto-domande con risposta.\n\n---\n\n"
             + "\n".join(pezzi))
    if corte == len(domanda):
        print(f"VISIBILE | tutte le {len(domanda)} sotto-domande sono tornate vuote: "
              f"NON segno il tema come fatto, il giro dopo ritenta.")
        return 0
    from datetime import datetime, timezone
    q = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    f = os.path.join(QUI, f"RICERCA_VISIBILE_{nome}_{q}.md")
    open(f, "w").write(testo)
    print(f"VISIBILE | scritto {os.path.basename(f)} ({len(testo)} caratteri, "
          f"{corte} sotto-domande da riprovare)", flush=True)
    RP._metti_al_sicuro(f)
    r["fatte"].append(nome)
    r["ultima"] = int(time.time())
    r["storia"].append({"nome": nome, "quando": int(time.time()), "secondi": int(time.time()-t0)})
    os.makedirs(os.path.dirname(REGISTRO), exist_ok=True)
    json.dump(r, open(REGISTRO, "w"), indent=1)
    print(f"VISIBILE | fatta in {int(time.time()-t0)}s. {len(r['fatte'])}/{len(PROGRAMMA)}",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
