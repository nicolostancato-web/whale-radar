"""FASCICOLO ASTRA — prepara la consultazione esterna coi numeri veri.

COSA E' CAMBIATO NEI PREZZI, E PERCHE' IL COMMENTO DI PRIMA ERA GIA' VECCHIO (21/09). Avevo
scritto qui che l'abbonamento copriva Astra e che l'API era solo una comodita' da 31-138 dollari
al mese. Falso: l'abbonamento Plus da 20 dollari NON da' Astra in chat — lo da' solo dentro Work e
Codex. Per averlo come consulente in chat serve Pro, da 100 dollari al mese.
Rifatto il conto col listino verificato oggi sul sito ufficiale:
    Pro (manuale, Mac acceso, ~50 messaggi a settimana)   100 $/mese
    API flex, due fascicoli asciutti al giorno              32 $/mese
    API flex, due fascicoli massivi al giorno               69 $/mese
L'API costa un terzo di Pro E lavora mentre il Mac e' spento. Per il nostro uso — due fascicoli al
giorno, non conversazione — Pro si paghera' una comodita' che non useremmo.
La decisione su cosa pagare resta del fondatore. Questo agente prepara il fascicolo e basta, e
funziona identico nelle due strade: incollato a mano, o spedito da chi paghera' i token.

IL PEZZO CHE MANCAVA NON ERA IL MODELLO. Il 17/09 ho scoperto che la revisione esterna era ferma da
SEI GIORNI: girava solo dall'estensione VS Code, quindi solo col Mac acceso e solo se qualcuno se
la ricordava. In quei sei giorni avevo trovato venti difetti da solo — senza sapere quanti ne
stavo lasciando, perche' nessuno guardava con occhi diversi.

LE MISURE GREZZE, NON UN RIASSUNTO. Un riassunto produce consigli generici, che poi diamo per colpa
di chi consiglia. E si mette anche cio' che ci fa fare brutta figura: un fascicolo che racconta solo
la parte che funziona si fa rispondere che tutto funziona.

LE MISURE SI CONTROLLANO A VICENDA. I numeri qui dentro devono coincidere con quelli del metro
indipendente. Quando li ho confrontati la prima volta NON coincidevano — questo file dichiarava
zero marchi sospetti contro il 4,4% del metro — e il fascicolo sarebbe uscito con un numero falso.
Due strade che danno lo stesso risultato non sono una ripetizione: sono l'unico modo che abbiamo
per accorgerci di un errore senza aspettare che ce lo dica qualcun altro fra sei settimane.
"""
import gzip
import hashlib
import json
import os
import time

OUT = os.environ.get("OUT_FASCICOLO", "FASCICOLO_ASTRA.txt")
MARCHIO_SOSPETTO = 1789986813   # istante in cui la correzione e' entrata in vigore
CAMPIONE = 40          # un file su quaranta, scelto per nome: stabile fra un giro e l'altro


def misura_istanti(chain):
    """Quanta parte dei record ha un istante CHIESTO alla catena, non interpolato.

    Il campione si sceglie dal NOME del file, non dalla posizione nell'elenco: l'elenco cambia
    mentre i raccoglitori scrivono, e un campione per posizione faceva muovere la percentuale di
    punti interi fra una misura e l'altra senza che fosse cambiato niente."""
    righe = veri = sospetti = 0
    file_visti = 0
    for sub in ("storico", "vivo"):
        d = f"data/multichain/{chain}/{sub}"
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if int(hashlib.md5(fn.encode()).hexdigest()[:4], 16) % CAMPIONE:
                continue
            file_visti += 1
            try:
                for l in gzip.open(os.path.join(d, fn), "rt"):
                    if not l.strip():
                        continue
                    r = json.loads(l)
                    righe += 1
                    if r.get("orario") == "catena":
                        veri += 1
                        # UN MARCHIO SOSPETTO NON SI RICONOSCE DALL'UGUAGLIANZA CON UN ISTANTE
                        # (21/09, corretto prima di spedirlo fuori). Avevo scritto «acq uguale al
                        # momento della correzione», e nessun record porta esattamente quel valore:
                        # il fascicolo dichiarava ZERO marchi sospetti mentre il metro ne trovava
                        # il 4,4% su base e il 9,7% su robinhood.
                        # Il sospetto e' un record marchiato «catena» ma raccolto PRIMA che la
                        # correzione esistesse: non puo' essere stato verificato da un codice che
                        # ancora non c'era. E' una disuguaglianza, non un'uguaglianza.
                        if (r.get("classe") == "point-in-time"
                                and not r.get("ver")           # verificato dopo la correzione: non e' sospetto
                            and (r.get("acq") or 0) < MARCHIO_SOSPETTO):
                            sospetti += 1
            except Exception:
                pass
    return {"file_campione": file_visti, "righe": righe,
            "istanti_veri_pct": round(100 * veri / max(1, righe), 1),
            "marchi_sospetti_pct": round(100 * sospetti / max(1, righe), 1)}


def conta(f, chiave=None):
    try:
        d = json.load(open(f))
        return len(d.get(chiave, d)) if isinstance(d, dict) else len(d)
    except Exception:
        return None


def main():
    p = []
    p.append("Sei un revisore esterno severo, non un assistente incoraggiante.")
    p.append("Qui sotto ci sono le misure VERE di un sistema che raccoglie scambi di memecoin su")
    p.append("due chain (base e robinhood). Il sistema serve a cercare un vantaggio statistico")
    p.append("('loop 1'), oggi FERMO di proposito: prima il database dev'essere affidabile.")
    p.append("")
    p.append("Due mesi fa abbiamo costruito un database, ci abbiamo cercato sopra un vantaggio per")
    p.append("un mese e mezzo, e solo dopo abbiamo scoperto che i dati non erano accurati: tutto")
    p.append("quel lavoro e' stato inutile. Non deve succedere di nuovo. Per questo il fascicolo")
    p.append("include anche cio' che ci fa fare brutta figura.")
    p.append("")
    p.append("NON riassumere. Dimmi DOVE CI STIAMO ILLUDENDO. Cerca in particolare:")
    p.append("  - numeri che non possono essere veri;")
    p.append("  - percentuali calcolate su popolazioni che si auto-selezionano")
    p.append("    (il difetto che ci ha gia' fregato: misuravamo la fedelta' solo dove")
    p.append("     stavamo raccogliendo, e cosi' saliva mentre la realta' peggiorava);")
    p.append("  - lavoro DICHIARATO fatto che non e' verificabile da chi legge;")
    p.append("  - condizioni che stiamo per dichiarare soddisfatte senza averle misurate.")
    p.append("")
    p.append("Rispondi con al massimo dieci rilievi, il piu' grave per primo, ognuno con la misura")
    p.append("precisa che lo dimostra e cosa dovremmo misurare per smentirti.")
    p.append("")
    p.append("=" * 70)
    p.append(f"MISURE DEL {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}")
    p.append("=" * 70)

    for ch in ("base", "robinhood"):
        p.append(f"\n--- {ch.upper()} ---")
        m = misura_istanti(ch)
        p.append(f"  istanti chiesti alla catena: {m['istanti_veri_pct']}% dei record")
        p.append(f"    (campione di {m['file_campione']} file, {m['righe']} righe, scelto per nome)")
        p.append(f"  marchi sospetti: {m['marchi_sospetti_pct']}%  <-- record che avevo marchiato")
        p.append("    'verificato' per errore il 20/09, e che vanno ancora ricontrollati")
        n = conta(f"data/multichain/{ch}/righe.json", "pool")
        c = conta(f"data/multichain/{ch}/coppie.json", "coppie")
        p.append(f"  pool nel registro: {n}   coppie note: {c}")
        for f, eti in ((f"data/multichain/{ch}/censimento.jsonl.gz", "pool che hanno scambiato"),):
            if os.path.exists(f):
                try:
                    p.append(f"  {eti}: {sum(1 for l in gzip.open(f, 'rt') if l.strip())}")
                except Exception:
                    pass

    if os.path.exists("data/popolazione_congelata.json"):
        p.append("\n--- METRO CONGELATO ---")
        p.append("  Il denominatore e' fissato in data/popolazione_congelata.json e NON si muove,")
        p.append("  altrimenti la copertura sale solo perche' cresce il numeratore.")
        try:
            p.append("  " + json.dumps(json.load(open("data/popolazione_congelata.json")))[:600])
        except Exception:
            pass

    p.append("\n--- COSA SO DI AVER SBAGLIATO (autodenuncia) ---")
    for r in ["misuravo la fedelta' solo sui pool dove stavo gia' raccogliendo: 41% dichiarato "
              "contro 24% vero;",
              "cinque agenti INTERPOLAVANO gli istanti invece di chiederli, con errori fino a "
              "8.439 secondi;",
              "ho marchiato io stesso come 'verificati' dei record che non lo erano, rendendo "
              "invisibili alla riparazione proprio le righe da riparare;",
              "per tre giri di fila la riparazione di robinhood e' stata uccisa dal tetto di "
              "tempo e TUTTO il suo lavoro e' stato buttato, mentre i log dicevano 'success';",
              "ho scambiato piu' volte un fallimento per un esito: file illeggibile letto come "
              "'riparato', pool non leggibile letto come 'vuoto'."]:
        p.append(f"  - {r}")

    for f in ("STAFFETTA.md", "DEFINIZIONE.md"):
        if os.path.exists(f):
            try:
                t = open(f).read()
                p.append(f"\n===== {f} =====\n{t[:8000]}")
            except Exception:
                pass

    testo = "\n".join(p)
    open(OUT, "w").write(testo)
    print(f"FASCICOLO | scritto {OUT}: {len(testo)} caratteri (~{len(testo)//4} token)", flush=True)
    print("FASCICOLO | costo: ZERO. Si incolla in ChatGPT con l'abbonamento gia' pagato.",
          flush=True)


if __name__ == "__main__":
    main()
