"""Quante chiamate restano all'API di GitHub. Da chiedere PRIMA di spenderne tante.

PERCHE' ESISTE (11/10, guasto mio). Ho esaurito la quota: 0 chiamate rimaste, e per un'ora
pubblicazione e verifiche si sono fermate — cioe' il database della demo non poteva essere messo
al sicuro. La colpa non e' di un picco: sono i controlli che ho scritto stanotte.

Il piu' golso e' il metro della crescita: elencava i commit di mezz'ora e poi chiedeva il
DETTAGLIO di ognuno, venti-quaranta chiamate per giro, ogni quaranta minuti. Piu' il manifesto,
piu' il confronto dei contenuti, piu' il recupero di 575 file. Sommati, bastano a bruciare 5.000
chiamate l'ora.

LA REGOLA, in positivo: un controllo che spende molte chiamate chiede prima quanto resta, e se
resta poco **si astiene dicendolo**. Astenersi dichiarando e' diverso da tacere: il referto dice
«non ho guardato, e perche'», che e' un'informazione vera. Era il contrario — i controlli
spendevano fino a far fallire la cosa che proteggevano.
"""
import json
import os
import re
import sys
import urllib.request


def _tok():
    for v in ("WR_PAT", "GITHUB_TOKEN"):
        if os.environ.get(v):
            return os.environ[v]
    c = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")
    if os.path.exists(c):
        m = re.search(r"ghp_[A-Za-z0-9]+", open(c, encoding="utf-8", errors="ignore").read())
        return m.group(0) if m else None
    return None


def quanto_resta():
    """(rimaste, totale, secondi_al_ricarico). Costa UNA chiamata, e non conta nella quota."""
    tok = _tok()
    if not tok:
        return None, None, None
    try:
        r = urllib.request.Request("https://api.github.com/rate_limit",
                                   headers={"Authorization": f"token {tok}"})
        d = json.load(urllib.request.urlopen(r, timeout=30))["resources"]["core"]
        import time
        return d["remaining"], d["limit"], max(0, int(d["reset"] - time.time()))
    except Exception:
        return None, None, None


def posso_spendere(quante, riserva=500):
    """True se dopo aver speso `quante` chiamate resta almeno la riserva.

    La riserva esiste perche' PUBBLICARE deve funzionare sempre: e' l'unica cosa che mette al
    sicuro il lavoro, e un controllo non puo' mai avere la precedenza su di lei.
    """
    rim, _, _ = quanto_resta()
    if rim is None:
        return True, "non so quanto resta: procedo, ma senza garanzie"
    if rim - quante < riserva:
        return False, (f"restano {rim} chiamate: spenderne {quante} lascerebbe meno di {riserva} "
                       f"per pubblicare. Mi astengo, e lo dico.")
    return True, f"restano {rim} chiamate: ne spendo {quante}"


def main():
    rim, tot, sec = quanto_resta()
    if rim is None:
        print("QUOTA | non leggibile")
        return 1
    print(f"QUOTA | {rim} chiamate su {tot} | si ricarica fra {sec//60} minuti")
    if rim < 500:
        print("QUOTA | SOTTO LA RISERVA: pubblicare e' a rischio, i controlli devono astenersi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
