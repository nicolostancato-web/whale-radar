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
    fn = f"REVISIONE_GROK_{time.strftime('%Y-%m-%d_%H%M', time.gmtime())}.md"
    open(fn, "w").write(
        f"# Revisione Grok — {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}\n\n"
        f"Modello {MODELLO}, sforzo {SFORZO}. Costo: ZERO (abbonamento, nessuna chiave API).\n"
        f"Tempo: {time.time()-t0:.0f}s\n\n---\n\n" + risposta + "\n")
    _pubblica(fn)
    print(f"GROK | scritto {fn} ({len(risposta)} caratteri in {time.time()-t0:.0f}s)", flush=True)


def _pubblica(fn):
    """Sul repository SUBITO. Le consulenze del 24/09 sono andate perse perche' vivevano solo sul
    Mac e una pulizia del disco le ha cancellate: terzo caso in due giorni. Una consulenza costa
    denaro o tempo, e va messa al sicuro nello stesso istante in cui nasce.

    PRIMA PASSAVA DA UN MODULO NELLA CARTELLA TEMPORANEA (corretto il 25/09): cioe' il salvataggio
    dipendeva da un file che vive esattamente nel posto che viene cancellato. La rete di sicurezza
    appesa al ramo che si sta segando. Ora si usa `git`, che sta nel repository stesso."""
    try:
        subprocess.run(["git", "add", fn], check=True, capture_output=True)
        subprocess.run(["git", "-c", "user.name=whale-radar-bot",
                        "-c", "user.email=bot@users.noreply.github.com",
                        "commit", "-q", "-m", f"consulenza: {fn}"], check=True, capture_output=True)
        for _ in range(10):
            # si riappoggia invece di fondere: i merge dei cicli di tentativi erano il 75% dei
            # commit del repository (26/09). Se il rebase non riesce, si fonde: meglio una
            # cicatrice che una consulenza non pubblicata.
            if subprocess.run(["git", "pull", "--rebase", "--autostash", "-q", "origin", "main"],
                              capture_output=True).returncode != 0:
                subprocess.run(["git", "pull", "--no-rebase", "--no-edit",
                                "--allow-unrelated-histories", "-X", "ours", "origin", "main"],
                               capture_output=True)
            if subprocess.run(["git", "push", "origin", "main"],
                              capture_output=True).returncode == 0:
                print(f"   pubblicata su GitHub: {fn}", flush=True)
                return
            time.sleep(6)
        print("   NON pubblicata: non sono riuscito a spingere. Mettila al sicuro a mano.",
              flush=True)
    except Exception as e:
        print(f"   NON pubblicata ({type(e).__name__}): mettila al sicuro a mano", flush=True)


if __name__ == "__main__":
    main()