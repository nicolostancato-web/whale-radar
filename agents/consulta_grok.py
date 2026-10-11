"""Il secondo revisore: Grok, dall'ABBONAMENTO di Nicolo, mai dall'API.

PERCHE' MAI DALL'API. Nel file delle credenziali esiste una chiave xAI. Usarla significherebbe
pagare a consumo IN AGGIUNTA ai 35 euro al mese gia' pagati: due volte la stessa cosa. Qui si passa
sempre dal programma `grok`, autenticato col suo account via OAuth. Nessuna chiave, costo zero.

IL PROTOCOLLO (deciso da Nicolo il 24/09/2026):
 - massimo 3 revisioni di Astra al giorno (~$0,11 l'una)
 - OGNI VOLTA che si chiede ad Astra si chiede ANCHE a Grok: due pareri indipendenti allo stesso
   prezzo di uno
 - dalla QUARTA revisione in poi, solo Grok, perche' e' gia' nell'abbonamento

Perche' due e non uno: il 24/09 Grok ha trovato un errore logico che Astra non aveva visto (una
spiegazione che richiedeva un effetto di segno costante, mentre i dati lo mostravano cambiare
segno). Ragionano in modo diverso. Quando concordano per strade diverse il risultato vale molto di
piu'; quando si contraddicono, si e' imparato dove scavare.
"""
import os
import subprocess
import sys
import time

GROK = os.path.expanduser("~/.grok/bin/grok")
MODELLO = os.environ.get("MODELLO_GROK", "grok-4.7")
SFORZO = os.environ.get("SFORZO_GROK", "high")
FASCICOLO = os.environ.get("OUT_FASCICOLO", "FASCICOLO_ASTRA.txt")


def chiedi(testo, modello=MODELLO, sforzo=SFORZO, minuti=25):
    """Manda il fascicolo a Grok e torna la risposta. Nessuna chiave: usa l'abbonamento."""
    if not os.path.exists(GROK):
        print("GROK | non installato: https://x.ai/cli/install.sh", flush=True)
        return None
    amb = dict(os.environ)
    # cintura di sicurezza: qualunque chiave nell'ambiente viene tolta, cosi' non c'e' modo
    # che una consulenza finisca per sbaglio sul conto a consumo
    for k in ("XAI_API_KEY", "GROK_API_KEY", "X_AI_API_KEY"):
        amb.pop(k, None)
    try:
        r = subprocess.run([GROK, "-p", testo, "--output-format", "plain",
                            "--model", modello, "--effort", sforzo],
                           capture_output=True, text=True, timeout=minuti * 60, env=amb)
    except subprocess.TimeoutExpired:
        print(f"GROK | scaduto dopo {minuti} minuti", flush=True)
        return None
    if r.returncode != 0:
        print(f"GROK | errore: {(r.stderr or '')[:300]}", flush=True)
        return None
    return r.stdout.strip()


def main():
    if not os.path.exists(FASCICOLO):
        print(f"GROK | manca {FASCICOLO}: prima si scrive la domanda, poi si chiede")
        return
    testo = open(FASCICOLO).read()
    print(f"GROK | mando {len(testo)} caratteri a {MODELLO} (sforzo {SFORZO}), "
          f"dall'abbonamento", flush=True)
    t0 = time.time()
    risposta = chiedi(testo)
    if not risposta:
        return
    # OUT_NOME permette di accumulare un fascicolo con un nome proprio (es. la ricerca di due
    # settimane sul pre-lancio) invece di confonderlo con le revisioni quotidiane. Senza, resta
    # il nome di sempre.
    base = os.environ.get("OUT_NOME") or "REVISIONE_GROK"
    titolo = "Ricerca Grok" if os.environ.get("OUT_NOME") else "Revisione Grok"
    # DOVE SCRIVE E' DETTO DA CHI CHIAMA (10/10, richiesta di Nicolo'). Prima scriveva SEMPRE
    # nella radice del repo: Nicolo' se n'e' accorto perche' «per tre giorni scriveva in un punto
    # in cui non si vedeva». Ora chi chiama puo' dare OUT_DIR, la cartella viene creata, e il
    # percorso completo finisce nell'ultima riga stampata — cosi' «dove ha scritto» non e' una
    # cosa da indovinare.
    cart = os.environ.get("OUT_DIR") or "."
    os.makedirs(cart, exist_ok=True)
    fn = os.path.join(cart, f"{base}_{time.strftime('%Y-%m-%d_%H%M', time.gmtime())}.md")
    open(fn, "w").write(
        f"# {titolo} — {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}\n\n"
        f"Modello {MODELLO}, sforzo {SFORZO}. Costo: ZERO (abbonamento, nessuna chiave API).\n"
        f"Tempo: {time.time()-t0:.0f}s\n\n---\n\n" + risposta + "\n")
    _pubblica(fn)
    print(f"GROK | scritto {fn} ({len(risposta)} caratteri in {time.time()-t0:.0f}s)", flush=True)


def _pubblica(fn):
    """Sul repository SUBITO, passando dall'INTERFACCIA di GitHub e non da git.

    PRIMA PASSAVA DA GIT (commit + pull --rebase + push). Il 6/10 ha fallito tre volte di fila,
    sempre per lo stesso motivo: il pull lasciava `data/prodotti.json` in conflitto, e da quel
    momento OGNI commit successivo era impossibile. Una ricerca di Grok e' rimasta solo sul Mac,
    ed e' esattamente il modo in cui il 25/09 avevamo perso le consulenze del giorno prima.

    **Una rete di sicurezza che dipende dallo stato dell'indice di git e' il ramo che si sta
    segando.** `pubblica_file.py` parla con l'interfaccia di GitHub: non ha un indice, non ha
    conflitti, e non puo' essere bloccata da niente di locale.

    In piu' il pull approfondiva la copia di lavoro a ogni consulenza: era la radice del gonfiore
    da 16 GB che il 6/10 ha riempito il disco (vedi agents/disco_e_copia.py).
    """
    try:
        r = subprocess.run([sys.executable,
                            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "pubblica_file.py"),
                            f"consulenza: {fn}"],
                           capture_output=True, text=True, timeout=600)
        if "sono su GitHub" in (r.stdout or ""):
            print(f"   pubblicata su GitHub: {fn}", flush=True)
            return True
        print(f"   NON pubblicata: {(r.stdout or r.stderr or '')[-200:]} — mettila al sicuro "
              f"a mano", flush=True)
    except Exception as e:
        print(f"   NON pubblicata ({type(e).__name__}): mettila al sicuro a mano", flush=True)
    return False


# IL LANCIATORE, RIMESSO IL 6/10. Riscrivendo `_pubblica` avevo sostituito tutto il testo dal suo
# `def` fino alla fine, e con esso se n'era andato anche questo blocco: il file girava, usciva con
# codice 0 e NON FACEVA NIENTE. Nessun errore, nessun messaggio, nessun file prodotto — una
# consulenza "riuscita" che non e' mai partita.
# E' la quarta volta oggi che un guasto senza voce mi costa tempo. Da qui la regola:
# **dopo aver riscritto un pezzo di file, si conta cosa c'era prima e cosa c'e' dopo.**
if __name__ == "__main__":
    main()
