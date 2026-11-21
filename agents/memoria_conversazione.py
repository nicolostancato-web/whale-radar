"""Ripesca TUTTO quello che il fondatore ha detto, da tutte le conversazioni su disco.

PERCHE' ESISTE (30/09). Nicolo': «abbiamo un grosso problema, ci siamo addormentati... e' come
se avessimo l'Alzheimer, e' impossibile arrivare al gol con l'Alzheimer. Ti avevo raccontato
della successione di combinazioni e tu due giorni fa te ne sei venuto fuori con strategie di
bassissimo livello, entrare a sei ore, come se ti fossi scordato tutto.»

Aveva ragione. Le sue parole vivono in 306 MB di trascritti su disco che nessun processo ha mai
letto: una conversazione lunga viene riassunta, e il riassunto perde le direttive vecchie.
**Il riassunto conserva il filo, non gli ordini.**

Questo processo estrae ogni messaggio del fondatore da tutte le conversazioni, in ordine di
tempo, e ne fa un archivio interrogabile che vive su GitHub E sul deposito da 100 GB.
Da qui si cerca per parola: «combinazioni», «astra», «goal», e si ritrova cosa aveva detto
davvero — non cosa mi ricordo che avesse detto.
"""
import datetime as dt
import glob
import json
import os
import re
import sys

CARTELLA = os.path.expanduser(
    "~/.claude/projects/-Users-nicolostancato-n8n-builder")
# COMPRESSO PERCHE' 1,9 MB NON PASSAVANO (1/10). L'interfaccia con cui pubblico rifiutava il
# file con un «conflitto» ripetuto, che sembrava contesa ed era dimensione: 620 KB passano al
# primo colpo. Una diagnosi sbagliata mi ha fatto perdere sei tentativi.
FUORI = "data/memoria/parole_del_fondatore.jsonl.gz"


def messaggi():
    """Ogni messaggio umano, con la data. Ordine cronologico."""
    fuori = []
    for f in sorted(glob.glob(os.path.join(CARTELLA, "*.jsonl"))):
        with open(f, encoding="utf-8", errors="replace") as h:
            for riga in h:
                riga = riga.strip()
                if not riga or '"user"' not in riga:
                    continue
                try:
                    d = json.loads(riga)
                except ValueError:
                    continue
                if d.get("type") != "user":
                    continue
                m = d.get("message") or {}
                c = m.get("content")
                if isinstance(c, list):
                    c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
                if not isinstance(c, str):
                    continue
                c = c.strip()
                # si scartano i messaggi generati dal sistema, non dall'uomo
                if not c or c.startswith(("<", "#", "Caller:", "Result of calling")):
                    continue
                if "tool_use_id" in riga and len(c) < 5:
                    continue
                fuori.append({"quando": d.get("timestamp", "")[:19],
                              "sessione": os.path.basename(f)[:8],
                              "testo": c})
    fuori.sort(key=lambda x: x["quando"])
    return fuori


def main():
    msg = messaggi()
    os.makedirs(os.path.dirname(FUORI), exist_ok=True)
    import gzip as _gz
    with _gz.open(FUORI, "wt", encoding="utf-8") as h:
        for m in msg:
            h.write(json.dumps(m, ensure_ascii=False) + "\n")
    giorni = sorted({m["quando"][:10] for m in msg if m["quando"]})
    print(f"MEMORIA | {len(msg):,} messaggi del fondatore, "
          f"da {giorni[0] if giorni else '?'} a {giorni[-1] if giorni else '?'} "
          f"({len(giorni)} giorni) -> {FUORI}", flush=True)
    if len(sys.argv) > 1:
        # si rilegge dal compresso: e' l'unico che esiste su GitHub e nel deposito
        chiave = " ".join(sys.argv[1:]).lower()
        trovati = [m for m in msg if chiave in m["testo"].lower()]
        print(f"\n   «{chiave}»: {len(trovati)} messaggi\n", flush=True)
        for m in trovati[-12:]:
            t = re.sub(r"\s+", " ", m["testo"])[:300]
            print(f"   [{m['quando'][:10]}] {t}\n", flush=True)


if __name__ == "__main__":
    main()
