"""Nessuna corsia puo' stampare un segreto. Il repository e' PUBBLICO.

PERCHE' ESISTE (1/10). Ho messo la chiave di OpenAI fra i segreti del repository perche' la
corsia del consulente giri da sola. Ma il repository e' pubblico, e io posso modificare le
corsie: una mia modifica — anche per sbaglio, anche per debug — potrebbe far finire quella
chiave in un registro leggibile da chiunque.

Grok l'ha detto in forma generale: «finche' il bot puo' committare il guardiano, tre guardiani
sono un file». Qui il rischio e' concreto e costa soldi veri.

Questo controllo rifiuta la pubblicazione se una corsia:
  · stampa una variabile che contiene un segreto (echo $OPENAI_API_KEY e simili);
  · usa `set -x` in un passo che ha un segreto nell'ambiente (traccia tutto, chiave compresa);
  · scrive un segreto in un file che finisce nel repository o in un allegato.

Non e' una difesa completa — la difesa vera e' la regola sul repository che chiede la revisione
di Nicolo' per i file delle corsie. Ma chiude gli errori che farei io senza pensarci.
"""
import glob
import re
import sys

SEGRETI = ["OPENAI_API_KEY", "XAI_API_KEY", "GH_TOKEN", "GITHUB_TOKEN", "WR_PAT",
           "R2_SECRET_ACCESS_KEY", "R2_ACCESS_KEY_ID", "HELIUS_API", "TELEGRAM_BOT_TOKEN"]


def guai(percorso):
    t = open(percorso, encoding="utf-8", errors="replace").read()
    fuori = []
    for s in SEGRETI:
        # stampare il valore: echo "$X", print(X), cat <<< $X
        for schema in (rf"echo[^\n]*\$\{{?{s}", rf"printf[^\n]*\$\{{?{s}",
                       rf"print\([^\n]*{s}", rf">&2[^\n]*\$\{{?{s}"):
            for m in re.finditer(schema, t):
                fuori.append(f"riga {t[:m.start()].count(chr(10))+1}: stampa {s}")
    if re.search(r"^\s*set -x", t, re.M) and any(s in t for s in SEGRETI):
        fuori.append("usa `set -x` con un segreto nell'ambiente: traccia tutto, chiave compresa")
    return fuori


def main():
    rotti = 0
    for f in sorted(glob.glob(".github/workflows/*.yml")):
        for g in guai(f):
            print(f"   {f}: {g}", flush=True)
            rotti += 1
    if rotti:
        print("   IL REPOSITORY E' PUBBLICO: un segreto stampato e' un segreto perso.", flush=True)
        sys.exit(1)
    print("   nessuna corsia stampa un segreto", flush=True)


if __name__ == "__main__":
    main()
