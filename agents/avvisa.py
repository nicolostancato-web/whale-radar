"""Avvisa il founder su Telegram, ma solo quando serve davvero.

PERCHE' (24/09). Oggi il disco del Mac si e' riempito alle cinque del mattino e il lavoro si e'
fermato: l'ho potuto dire solo quando Nicolo e' tornato a leggere la chat. Un avviso lo avrebbe
sbloccato in un minuto.

QUANDO SI SCRIVE, e la regola e' stretta apposta:
 - una corsia e' caduta e non si e' ripresa da sola
 - lo spazio su disco o il peso del repository stanno per bloccare tutto
 - un revisore ha demolito un risultato su cui stavamo costruendo
 - serve una decisione che non prendo da solo

QUANDO NON SI SCRIVE: per i progressi normali. Quelli si leggono in chat. Un avviso che arriva
troppo spesso smette di essere letto, e quando serve davvero non lo guarda nessuno.

La chiave si legge SOLO dal file delle credenziali, mai dalla chat, mai dal codice.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

FILE = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")


def _credenziali():
    tok = cid = None
    try:
        for riga in open(FILE, errors="ignore"):
            if "TELEGRAM_BOT_TOKEN" in riga:
                v = riga.split("=", 1)[-1].strip()
                if v and "INCOLLA" not in v:
                    tok = v
            elif "TELEGRAM_CHAT_ID" in riga:
                v = riga.split("=", 1)[-1].strip()
                if v:
                    cid = v
    except Exception:
        pass
    return tok or os.environ.get("TELEGRAM_BOT_TOKEN"), cid or os.environ.get("TELEGRAM_CHAT_ID")


def avvisa(testo):
    """Torna True se il messaggio e' partito. Non solleva mai: un avviso che fallisce
    non deve fermare il lavoro che stava provando a segnalare."""
    tok, cid = _credenziali()
    if not tok or not cid:
        print("AVVISO | manca il token o il chat id: non mando niente", flush=True)
        return False
    d = urllib.parse.urlencode({"chat_id": cid, "text": testo[:3900]}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(
                f"https://api.telegram.org/bot{tok}/sendMessage", data=d), timeout=25) as x:
            return bool(json.load(x).get("ok"))
    except Exception as e:
        print(f"AVVISO | non inviato: {type(e).__name__}", flush=True)
        return False


if __name__ == "__main__":
    t = " ".join(sys.argv[1:]) or "prova"
    print("inviato" if avvisa(t) else "non inviato")
