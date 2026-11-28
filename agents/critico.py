"""Il critic: puo' RIFIUTARE una modifica, e guarda le due cose che io non posso vedere da solo.

PERCHE' (28/09, dall'audit dell'auto-learning). Il ciclo era: propongo, eseguo, dichiaro fatto.
Nessun passaggio usciva dalle mie mani. Un critic che «commenta» non cambia niente — sarebbe solo
un'altra voce che discute col mio racconto. Questo invece sta sulla porta e blocca.

Guarda due cose, scelte perche' sono i due rischi che ho nominato io stesso nell'audit e che **non
posso giudicare mentre li commetto**:

1. **STAI AGGIUSTANDO IL METRO CON CUI TI MISURI?**
   Il 28/09 ho modificato DUE VOLTE il codice che raccoglie le prove su cui il sistema giudica se
   sta migliorando. Le modifiche erano giuste, ma e' letteralmente la trappola del paper di Google:
   un sistema che ottimizza il proprio esame. Se una pubblicazione tocca SOLO gli strumenti di
   misura e niente del sistema misurato, va fermata e giustificata a voce alta.

2. **QUANTE COSE STAI CAMBIANDO INSIEME?**
   Con dieci file in un colpo non si capisce piu' quale modifica ha prodotto l'effetto, e il
   rollback diventa impossibile. Il 28/09 ne ho cambiati 47 in una volta: e' andata bene, ma non
   potevo saperlo.

NON E' UN DIVIETO ASSOLUTO. Si passa dichiarando il motivo (`MOTIVO="..."`), e il motivo finisce
scritto in `data/eccezioni_critico.json`. **Le eccezioni impossibili si aggirano; quelle visibili
si contano.**
"""
import json
import os
import re
import subprocess
import sys
import time

# gli strumenti con cui il sistema misura se stesso: toccarli e' un atto speciale
STRUMENTI = {"agents/prova_metro.py", "agents/incidenti.py", "agents/lezioni.py",
             "agents/piu_intelligente.py", "pubblica.sh", "agents/critico.py"}
MASSIMO_FILE = 12          # oltre, non si capisce piu' cosa ha causato cosa


def cambiati():
    r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    return sorted({l.split()[-1] for l in r.stdout.splitlines() if l.strip()})


def ragione_cancellata():
    """Un numero rimasto dopo che il commento che lo giustificava e' sparito.

    IL PRUNING DI CUI ABBIAMO DAVVERO BISOGNO (28/09). Il 27/09 ho alzato un parametro a 45 con una
    ragione scritta accanto, e due ore dopo ho eliminato quella ragione lasciando il 45: per mezza
    giornata un numero ha difeso un problema che non esisteva piu'.
    Non serve un «processo di pruning» generico: serve accorgersi di QUESTA decadenza, che e' la
    sola che ci e' costata qualcosa. Un valore senza piu' motivo non e' una scelta, e' un residuo.
    """
    r = subprocess.run(["git", "diff", "-U3"], capture_output=True, text=True).stdout
    sospetti = []
    righe = r.splitlines()
    for i, l in enumerate(righe):
        if not (l.startswith("-") and not l.startswith("---")):
            continue
        if "#" not in l:
            continue                                   # non e' un commento tolto
        # c'e' un assegnamento numerico che RESTA (contesto o aggiunta) nelle righe vicine?
        vicine = righe[max(0, i - 3):i + 4]
        for v in vicine:
            if v.startswith("-"):
                continue
            testo = v[1:] if v[:1] in " +" else v
            if re.search(r"=\s*\d+", testo) and "#" not in testo:
                sospetti.append(testo.strip()[:70])
                break
    return sorted(set(sospetti))


def giudica(file_cambiati, motivo=None):
    """Torna (va_bene, elenco di obiezioni)."""
    obiezioni = []
    strumenti = [f for f in file_cambiati if f in STRUMENTI]
    altro = [f for f in file_cambiati if f not in STRUMENTI and not f.startswith("data/")]

    if strumenti and not altro:
        obiezioni.append(
            "TOCCHI SOLO GLI STRUMENTI DI MISURA (" + ", ".join(strumenti) + ") e nient'altro. "
            "Stai aggiustando l'esame invece di studiare: se la modifica e' giusta, dillo a voce "
            "alta con MOTIVO=\"...\".")

    if len(file_cambiati) > MASSIMO_FILE:
        obiezioni.append(
            f"CAMBI {len(file_cambiati)} FILE INSIEME (massimo {MASSIMO_FILE}). Con questo numero "
            "non si capisce quale modifica ha prodotto l'effetto, e tornare indietro e' un lavoro. "
            "Spezza in piu' pubblicazioni, oppure dichiara MOTIVO=\"...\".")

    orfani = ragione_cancellata()
    if orfani:
        obiezioni.append(
            "CANCELLI LA RAGIONE E LASCI IL NUMERO: " + "; ".join(orfani[:3]) +
            ". Un valore senza piu' motivo non e' una scelta, e' un residuo — il 27/09 un 45 e' "
            "rimasto mezza giornata a difendere un problema che non esisteva piu'.")

    return (not obiezioni), obiezioni


def registra_eccezione(motivo, file_cambiati, obiezioni):
    p = "data/eccezioni_critico.json"
    try:
        tutte = json.load(open(p)) if os.path.exists(p) else []
    except Exception:
        tutte = []
    tutte.append({"quando": time.strftime("%Y-%m-%d %H:%M", time.gmtime()), "motivo": motivo,
                  "file": file_cambiati, "obiezioni": obiezioni})
    os.makedirs("data", exist_ok=True)
    json.dump(tutte, open(p, "w"), indent=1, ensure_ascii=False)
    print(f"   eccezione registrata ({len(tutte)} in tutto): «{motivo}»", flush=True)


def main():
    f = cambiati()
    if not f:
        return 0
    ok, obiezioni = giudica(f)
    if ok:
        print(f"   il critico non ha obiezioni ({len(f)} file)")
        return 0
    motivo = os.environ.get("MOTIVO", "").strip()
    print("   IL CRITICO OBIETTA:")
    for o in obiezioni:
        print("     -", o)
    if not motivo:
        print("\n   Non si pubblica. Se l'obiezione non regge, rispondi:  MOTIVO=\"...\" ./pubblica.sh ...")
        return 1
    registra_eccezione(motivo, f, obiezioni)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
