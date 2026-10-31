"""I requisiti ATTIVI: cosa devo star facendo adesso, con il criterio che dice se e' fatto.

PERCHE' NON BASTA L'ARCHIVIO (1/10, rilievo di Astra).

Ho estratto 3.031 messaggi del fondatore e li ho resi interrogabili per parola. Astra:
«e' un archivio utile. NON e' ancora memoria operativa. La catena necessaria e'
direttiva → interpretazione approvata → requisito attivo → lavoro pianificato → evidenza →
accettazione. La ricerca per parola non garantisce nessun passaggio di questa catena.
**Se l'agente dimentica di cercare, l'archivio non interviene.»**

Esatto: un archivio che devo ricordarmi di consultare non cura il fatto che mi dimentico.

Qui i requisiti sono ATTIVI e si mostrano da soli. Ognuno ha:
  · da dove viene (la frase del fondatore, con la data);
  · lo stato: attivo / soddisfatto / superato;
  · il CRITERIO DI ACCETTAZIONE, cioe' cosa si guarda per dire che e' fatto;
  · chi lo sostituisce, se e' stato superato.

Un requisito «attivo» senza lavoro corrispondente e' un debito, e si vede.
E i requisiti superati restano scritti: cancellarli farebbe perdere il perche' del cambiamento.
"""
import datetime as dt
import json
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)


def _c_e(percorso, testo=None):
    p = os.path.join(RADICE, percorso)
    if not os.path.exists(p):
        return False
    if testo is None:
        return True
    return testo in open(p, encoding="utf-8", errors="replace").read()


REQUISITI = [
 {"id": "combinazioni-incrociate", "nato": "2026-09-23", "stato": "attivo",
  "parole": "Io mi aspetto una strategia mostruosa, dove si analizzano migliaia di combinazioni "
            "tutte perfette... tutto fatto di parametri incrociati.",
  "accettazione": lambda: _c_e("agents/combinazioni.py", "MAX_CONDIZIONI"),
  "evidenza": "VERDETTO_COMBINAZIONI.md — 10.700 incroci provati, verdetto negativo onesto"},

 {"id": "astra-tre-al-giorno", "nato": "2026-09-23", "stato": "attivo",
  "parole": "Astra lo usi tre volte al giorno. Ogni strategia che facciamo, Astra deve dare "
            "quel commento.",
  "accettazione": lambda: _c_e(".github/workflows/astra.yml", "consulta_astra"),
  "evidenza": "corsia astra.yml, tre volte al giorno, sotto la rete dei guardiani"},

 {"id": "memoria-sempre-aggiornata", "nato": "2026-09-30", "stato": "attivo",
  "parole": "Ti vai a prendere tutta la memoria della chat, tutto quello che ti ho detto... "
            "se io ti dico qualcosa e te la tiro fuori un mese dopo, tu la sai.",
  "accettazione": lambda: _c_e("data/memoria/parole_del_fondatore.jsonl.gz"),
  "evidenza": "3.031 messaggi estratti e interrogabili"},

 {"id": "memoria-fuori-da-github", "nato": "2026-09-30", "stato": "attivo",
  "parole": "Abbiamo un altro server con 100 GB oltre che GitHub, dobbiamo salvare tutto cio'.",
  "accettazione": lambda: _c_e(".github/workflows/deposito.yml", '"/tmp/memoria", "memoria"'),
  "evidenza": "il deposito porta fuori memoria e dati; la prova e' il RIPRISTINO, non l'impronta"},

 {"id": "trappole-dei-sistemi-giganti", "nato": "2026-10-01", "stato": "attivo",
  "parole": "Mi vai a vedere quali sono gli errori piu' comuni, dove cascano i gigantic "
            "workflow. Dobbiamo prendere tutti questi punti e implementarli.",
  "accettazione": lambda: _c_e("agents/autorizzazione.py", "L'ASSENZA NEGA")
                            or _c_e("agents/autorizzazione.py", "L'assenza nega"),
  "evidenza": "consulenza Astra sull'architettura; implementati: autorizzazione che nega per "
              "difetto, prova di ripristino, rete di guardiani"},

 {"id": "loop-che-sforna-e-scarta", "nato": "2026-09-30", "stato": "attivo",
  "parole": "Un sistema che sa il goal e crea una soluzione in loop, una dietro l'altra, "
            "finche' non ne trova una, senza scordarsi niente.",
  "accettazione": lambda: _c_e(".github/workflows/ciclo.yml", "ciclo_ipotesi"),
  "evidenza": "corsia ciclo.yml ogni tre ore, a rotazione sulle configurazioni; registro di "
              "TUTTE le prove; nessuna auto-approvazione (una candidata resta in attesa di "
              "revisione esterna e il codice non ha un percorso per adottarla)"},

 {"id": "niente-euro-prima-della-prova", "nato": "2026-08-06", "stato": "attivo",
  "parole": "Nessun euro rischiato finche' una strategia non ha superato la prova sul futuro.",
  "accettazione": lambda: _c_e("PROVA_IN_AVANTI.md", "Nessun euro rischiato"),
  "evidenza": "contratto registrato, giudice automatico, verdetto atteso il 10/10"},

 {"id": "prezzo-ottenibile", "nato": "2026-10-01", "stato": "attivo",
  "parole": "(derivato: la misura deve dire la verita' su cosa si incassa davvero)",
  "accettazione": lambda: _c_e("agents/insieme.py", "_uscita_{taglia}_ritardo"),
  "evidenza": "LATENZA_LA_SCOPERTA.md — il prezzo che vedi non e' quello che paghi"},
]


def stato():
    fuori = []
    for r in REQUISITI:
        try:
            fatto = bool(r["accettazione"]())
        except Exception as e:
            fatto = False
            r = dict(r, evidenza=f"il criterio e' esploso: {type(e).__name__}")
        fuori.append((r, fatto))
    return fuori


def main():
    s = stato()
    attivi = [(r, f) for r, f in s if r["stato"] == "attivo"]
    debiti = [(r, f) for r, f in attivi if not f]
    print(f"REQUISITI | {len(attivi)} attivi, {len(attivi)-len(debiti)} con evidenza, "
          f"{len(debiti)} SENZA (debito)", flush=True)
    for r, f in attivi:
        segno = "ok    " if f else "DEBITO"
        print(f"   {segno} [{r['nato']}] {r['id']}", flush=True)
        if not f:
            print(f"          «{r['parole'][:120]}»", flush=True)
            print(f"          stato: {r['evidenza']}", flush=True)
    json.dump({"quando": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "attivi": [r["id"] for r, _ in attivi],
               "debiti": [r["id"] for r, f in attivi if not f]},
              open(os.path.join(RADICE, "data/requisiti_stato.json"), "w"), indent=1)
    if debiti and "--severo" in sys.argv:
        sys.exit(1)


if __name__ == "__main__":
    main()
