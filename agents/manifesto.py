"""IL MANIFESTO: cosa esiste, chi lo produce, dove va. E il cancello che lo fa rispettare.

PERCHE' ESISTE. Nicolo' (10/10): «bisogna dire esattamente cosa deve fare, esattamente gli
orari, esattamente dove deve scrivere. C'e' molta confusione, roba gira a caso.»
Astra, consultata lo stesso giorno, ha dato la regola in forma applicabile da un programma:

    codice, configurazione, schema, documentazione approvata  -> GitHub
    risultato di esecuzione (dati, checkpoint, ricerca,
    consulenza, rapporto, allarme, log, ricevuta)             -> R2
    non dichiarato nel manifesto                              -> scrittura RIFIUTATA

La terza riga e' quella che conta. Finora non esisteva la nozione di «posto sbagliato»: un file
nato dove non doveva non violava niente, quindi nessun controllo poteva vederlo. Con il manifesto
la violazione esiste, e il cancello la ferma PRIMA che entri nella storia di git — che e' il
punto, perche' dalla storia non si torna indietro.

PERCHE' NON «piccolo su GitHub, grande su R2»: Astra ha scartato quel criterio, e ha ragione.
Un file piccolo riscritto ogni venti minuti produce piu' storia di uno grande scritto una volta.
Il criterio e' la NATURA del dato, non la sua taglia. La taglia resta solo come rete di
sicurezza: oltre 1 MB su GitHub serve un'eccezione con nome e cognome qui dentro.
"""
import fnmatch
import json
import os
import sys

FILE = "MANIFESTO.json"

# La prima stesura descrive cio' che esiste OGGI, con il deposito che DEVE avere. Dove i due non
# combaciano, il cancello lo dira': e' lavoro da fare, non un errore del manifesto.
PRODOTTI = [
    # --- GitHub: il programma ---
    {"nome": "codice", "modello": "agents/*.py", "deposito": "github", "tipo": "codice",
     "proprietario": "io", "conservazione": "permanente"},
    {"nome": "corsie", "modello": ".github/workflows/*.yml", "deposito": "github",
     "tipo": "configurazione", "proprietario": "io", "conservazione": "permanente"},
    {"nome": "documenti", "modello": "*.md", "deposito": "github", "tipo": "documentazione",
     "proprietario": "io", "conservazione": "permanente"},
    {"nome": "decisioni e contratti", "modello": "data/{strategy.yaml,corsie_spente.json,"
     "inventario_atteso.json,organizzazione.json}", "deposito": "github",
     "tipo": "configurazione", "proprietario": "io", "conservazione": "permanente"},

    # --- GitHub per eccezione: lo stato della demo, che deve essere leggibile dal codice ---
    {"nome": "stato della prova in avanti", "modello": "data/multichain/*/prova_in_avanti.json",
     "deposito": "github", "tipo": "stato", "proprietario": "prova_avanti",
     "conservazione": "permanente", "eccezione_oltre_1mb": True,
     "perche_eccezione": "e' lo stato che decide le entrate e le uscite: deve stare dove il "
                         "codice lo legge senza scaricare niente. 1,1 MB, 10.970 record, "
                         "100 byte l'uno: scritto bene."},
    {"nome": "database del cammino", "modello": "data/multichain/*/cammino_posizioni.json",
     "deposito": "github", "tipo": "stato", "proprietario": "cammino",
     "conservazione": "permanente"},
    {"nome": "chi vende nel crollo", "modello": "data/multichain/*/chi_vende_nel_dump.json",
     "deposito": "github", "tipo": "stato", "proprietario": "dump",
     "conservazione": "permanente"},

    # --- R2: cio' che il programma produce ---
    {"nome": "archivi storici delle chain", "modello": "data/multichain/*/{curva_lanci.json.gz,"
     "coppie.json,censimento.jsonl.gz,iniziatori.json.gz,tenute_pezzo_*.jsonl.gz,serie_pool.jsonl,"
     "curva_lanci.voci.jsonl,curva_lanci.meta.json,coppie.voci.jsonl,coppie.meta.json}",
     "deposito": "r2", "prefisso": "archive/", "tipo": "runtime", "proprietario": "fasi chiuse",
     "conservazione": "permanente"},
    {"nome": "dati della fase loop1", "modello": "data/loop1/*", "deposito": "r2",
     "prefisso": "archive/loop1/", "tipo": "runtime", "proprietario": "fasi chiuse",
     "conservazione": "permanente"},
    {"nome": "dati della chain base", "modello": "data/multichain/base/*", "deposito": "r2",
     "prefisso": "archive/base/", "tipo": "runtime", "proprietario": "fase base (ferma)",
     "conservazione": "permanente"},
    {"nome": "ricerche sui venditori", "modello": "ricerca/venditori/*.md", "deposito": "github",
     "tipo": "documentazione", "proprietario": "ricerca_venditori",
     "conservazione": "permanente",
     "perche": "sono il lavoro di Grok sulla domanda «chi vende forte e da dove prende i "
               "gettoni»: si leggono a mano, pesano decine di KB, e devono stare in un posto "
               "con un indirizzo stabile. Dichiarate qui perche' Nicolo' ha chiesto di sapere "
               "ESATTAMENTE dove scrive."},
    {"nome": "registro delle ricerche", "modello": "data/ricerca_*.json", "deposito": "github",
     "tipo": "stato", "proprietario": "ricerca", "conservazione": "permanente"},
    {"nome": "consulenze del revisore", "modello": "CONSULENZA_*.md", "deposito": "r2",
     "prefisso": "research/consulenze/", "tipo": "runtime", "proprietario": "astra",
     "conservazione": "permanente", "anche_su_github": True,
     "perche_anche_github": "costano denaro e si leggono a mano: finche' pesano 10 KB l'una, "
                            "tenerle anche nel ramo costa meno che perderle."},
    {"nome": "programmi di analisi", "modello": "analysis/*.py", "deposito": "github",
     "tipo": "codice", "proprietario": "io", "conservazione": "permanente"},
    {"nome": "comandi", "modello": "*.sh", "deposito": "github", "tipo": "codice",
     "proprietario": "io", "conservazione": "permanente"},
    {"nome": "comandi degli agenti", "modello": "agents/*.sh", "deposito": "github",
     "tipo": "codice", "proprietario": "io", "conservazione": "permanente"},
    {"nome": "configurazione di git", "modello": ".git*", "deposito": "github",
     "tipo": "configurazione", "proprietario": "io", "conservazione": "permanente"},
    {"nome": "fascicoli per il revisore", "modello": "FASCICOLO_*.txt", "deposito": "r2",
     "prefisso": "research/fascicoli/", "tipo": "runtime", "proprietario": "io",
     "conservazione": "90 giorni"},
    {"nome": "ricerche scartate perche' troppo corte", "modello": "*.troppo_corta",
     "deposito": "scarto", "tipo": "runtime", "proprietario": "ricerca",
     "conservazione": "nessuna: si cancellano",
     "perche": "sono risposte troncate, tenute per capire perche' si troncavano. Ora che il "
               "motivo e' noto non servono piu': 15 file che nessuno legge."},
    # LA CONFIGURAZIONE E LO STATO DELLE CORSIE VIVE STANNO NEL RAMO (10/10). Il modello largo
    # `data/*.json*` aveva classificato come «risultato di esecuzione» anche i file di criterio e
    # i contatori che le corsie ACCESE leggono a ogni giro: spostarli in R2 avrebbe rotto
    # quattordici letture. Trovato prima di spostare, perche' ho registrato i lettori come dice
    # Astra — non dopo, scoprendo un guasto. Questi vanno dichiarati PRIMA del modello largo:
    # il manifesto prende il primo che combacia.
    {"nome": "registro delle pubblicazioni", "modello": "data/{prodotti,potati}.json",
     "deposito": "github", "tipo": "stato", "proprietario": "io",
     "conservazione": "permanente", "eccezione_oltre_1mb": True,
     "perche_eccezione": "e' il registro di cosa e' stato pubblicato e quando: lo scrive "
                         "pubblica_file.py a OGNI invio da questo Mac. Il mio primo controllo "
                         "sui lettori guardava solo le corsie di GitHub e non vedeva gli "
                         "strumenti che giro io: stava per finire nella lista da cancellare "
                         "(10/10). Un punto cieco trovato per un soffio."},
    {"nome": "le monete diplomate verificate", "modello": "data/multichain/*/diplomate_vere.jsonl",
     "deposito": "github", "tipo": "stato", "proprietario": "diplomate",
     "conservazione": "permanente", "eccezione_oltre_1mb": True,
     "perche_eccezione": "69.966 record a 81 byte l'uno: e' il file scritto BENE del progetto, "
                         "cresce per aggiunta e non per riscrittura, quindi nel ramo costa solo "
                         "le righe nuove. E' anche il campione su cui si misura tutto."},
    {"nome": "criteri e contatori delle corsie vive",
     "modello": "data/{criteri,holdout_config,ispezione,audit_flags,cfo_flags,"
                "lettori_dei_dati,rilanci}.json",
     "deposito": "github", "tipo": "configurazione", "proprietario": "corsie accese",
     "conservazione": "permanente"},
    {"nome": "contatore delle consulenze", "modello": "data/consulenze/*.json",
     "deposito": "github", "tipo": "stato", "proprietario": "astra",
     "conservazione": "permanente"},
    {"nome": "dati delle fasi chiuse nella radice di data", "modello": "data/*.json*",
     "deposito": "r2", "prefisso": "archive/vecchi/", "tipo": "runtime",
     "proprietario": "fasi chiuse", "conservazione": "permanente"},
    {"nome": "righe delle fasi chiuse nella radice di data", "modello": "data/*.jsonl*",
     "deposito": "r2", "prefisso": "archive/vecchi/", "tipo": "runtime",
     "proprietario": "fasi chiuse", "conservazione": "permanente"},
    {"nome": "il manifesto stesso", "modello": "MANIFESTO.json", "deposito": "github",
     "tipo": "configurazione", "proprietario": "io", "conservazione": "permanente"},
    {"nome": "lo stato da leggere a voce", "modello": "STATO_COMPLETO.txt", "deposito": "github",
     "tipo": "documentazione", "proprietario": "io", "conservazione": "permanente",
     "perche": "Nicolo' lo apre col telefono e lo legge con un'altra AI: deve stare in un posto "
               "con un indirizzo stabile, e pesa pochi KB."},
    {"nome": "strumenti condivisi", "modello": "strumenti/*.py", "deposito": "github",
     "tipo": "codice", "proprietario": "io", "conservazione": "permanente"},
    {"nome": "stato operativo del vecchio motore", "modello": "{state,metrics,directives}.json",
     "deposito": "r2", "prefisso": "archive/vecchi/", "tipo": "runtime",
     "proprietario": "fasi chiuse", "conservazione": "permanente"},
    {"nome": "prompt del revisore", "modello": "prompt_astra.txt", "deposito": "github",
     "tipo": "configurazione", "proprietario": "io", "conservazione": "permanente"},
    {"nome": "ricevute delle consegne", "modello": "data/ricevute_consegne.jsonl",
     "deposito": "github", "tipo": "stato", "proprietario": "monitor",
     "conservazione": "permanente",
     "perche": "e' la prova che una consegna e' avvenuta e verificata: deve stare dove si "
               "legge senza dipendere dal deposito che certifica."},
    {"nome": "ricevute e allarmi", "modello": "data/{allarmi_*.jsonl,peso_repository.jsonl}", "deposito": "r2", "prefisso": "ops/", "tipo": "runtime",
     "proprietario": "monitor", "conservazione": "90 giorni"},
]

LIMITE_GITHUB = 1_000_000          # rete di sicurezza, non il criterio


def _combacia(percorso, modello):
    """Come fnmatch, ma capisce anche le graffe {a,b,c} dentro il modello."""
    if "{" in modello:
        testa, resto = modello.split("{", 1)
        dentro, coda = resto.split("}", 1)
        return any(_combacia(percorso, testa + x + coda) for x in dentro.split(","))
    return fnmatch.fnmatch(percorso, modello)


def _pulisci(p):
    """Togliere solo il «./» iniziale.

    `lstrip("./")` toglie QUALUNQUE punto e barra iniziale, quindi `.github/workflows/x.yml`
    diventava `github/workflows/x.yml` e il modello non combaciava mai: il cancello avrebbe
    rifiutato TUTTI i file di corsia, cioe' si sarebbe rotto proprio dove deve funzionare.
    Trovato al primo referto, perche' 73 file di corsia risultavano «non dichiarati» (10/10).
    """
    return p[2:] if p.startswith("./") else p


def prodotto_di(percorso):
    p = _pulisci(percorso)
    for x in PRODOTTI:
        if _combacia(p, x["modello"]):
            return x
    return None


def dove_deve_andare(percorso):
    """(deposito, prodotto) oppure (None, None) se non e' dichiarato."""
    x = prodotto_di(percorso)
    return (x["deposito"], x) if x else (None, None)


def puo_andare_su_github(percorso):
    """(True/False, motivo). E' il cancello che serve a pubblica_file.py."""
    dep, x = dove_deve_andare(percorso)
    if x is None:
        return False, (f"{percorso} non e' dichiarato nel manifesto. Un file senza prodotto non "
                       f"ha un posto: dichiaralo in agents/manifesto.py, oppure non scriverlo.")
    if dep != "github" and not x.get("anche_su_github"):
        pre = x.get("prefisso", "")
        return False, (f"{percorso} e' «{x['nome']}», un risultato di esecuzione: va nel deposito "
                       f"R2 sotto {pre}, non nel ramo. GitHub tiene la storia per sempre, e una "
                       f"riscrittura costa il peso intero a ogni salvataggio.")
    try:
        peso = os.path.getsize(percorso)
    except OSError:
        peso = 0
    if peso > LIMITE_GITHUB and not x.get("eccezione_oltre_1mb"):
        return False, (f"{percorso} pesa {peso/1e6:.1f} MB e «{x['nome']}» non ha l'eccezione "
                       f"oltre 1 MB nel manifesto. Se deve stare nel ramo, scrivi l'eccezione "
                       f"con il perche'; altrimenti va in R2.")
    return True, f"«{x['nome']}», {x['tipo']}: il ramo e' il posto giusto"


def main():
    if len(sys.argv) > 1:
        for p in sys.argv[1:]:
            ok, motivo = puo_andare_su_github(p)
            print(("PUO' |  " if ok else "NO   |  ") + motivo)
        return 0
    # il referto: cosa c'e' sul disco che il manifesto non dichiara, o dichiara altrove
    fuori, sbagliati, dichiarati = [], [], 0
    for r, _, ff in os.walk("."):
        if any(x in r for x in (".git/", "__pycache__", "/venv")):
            continue
        for x in ff:
            p = _pulisci(os.path.join(r, x))
            if p.startswith(".git/"):
                continue
            dep, prod = dove_deve_andare(p)
            if prod is None:
                fuori.append(p)
            else:
                dichiarati += 1
                if dep == "r2" and not prod.get("anche_su_github") and os.path.exists(p):
                    sbagliati.append((p, prod["nome"]))
    print(f"MANIFESTO | {len(PRODOTTI)} prodotti dichiarati, {dichiarati} file coperti")
    print(f"MANIFESTO | {len(fuori)} file NON dichiarati (un file senza prodotto non ha un posto)")
    for p in sorted(fuori)[:12]:
        print(f"   {p}")
    if len(fuori) > 12:
        print(f"   … e altri {len(fuori)-12}")
    print(f"\nMANIFESTO | {len(sbagliati)} file sono nel ramo ma il loro posto e' R2")
    for p, n in sorted(sbagliati)[:12]:
        print(f"   {p}  ({n})")
    if len(sbagliati) > 12:
        print(f"   … e altri {len(sbagliati)-12}")
    json.dump({"prodotti": PRODOTTI, "non_dichiarati": sorted(fuori),
               "nel_ramo_ma_vanno_in_r2": sorted(p for p, _ in sbagliati)},
              open(FILE, "w"), indent=1)
    print(f"\nMANIFESTO | scritto {FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
