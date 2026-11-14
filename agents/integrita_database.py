"""IL CONTROLLO DI INTEGRITA' DEL DATABASE, a ogni giro.

== PERCHE' (9/10/2026) ==

Nicolo': «mi raccomando focus sull'accumulazione corretta, fra cinque giorni il database deve
essere al top». E ha ragione a insistere: un buco nei dati si scopre quando li si analizza, e
allora e' tardi — i cinque giorni sono passati e non si rifanno.

Questo agente controlla sei cose a ogni giro e **le dichiara**. Non ripara: segnala. Riparare in
automatico un dato che non si capisce e' il modo di nascondere il problema.

== I SEI CONTROLLI ==

1. ogni posizione operativa ha un record nel database del cammino (e viceversa);
2. nessun record e' **vecchio**: se l'aggiornamento non e' dell'ultimo giro, il dato sta fermo e
   sembra buono;
3. ogni record ha gli attributi che deve avere per la sua eta' (a 1h dopo un'ora, ecc.);
4. il denominatore e' completo: nessun pool riconosciuto senza stato;
5. la copia su GitHub e' identica a quella locale (altrimenti i cinque giorni vivono su un Mac);
6. le posizioni chiuse continuano a essere tracciate, perche' servono per valutare orizzonti piu'
   lunghi di quello usato (16,7 ore) senza toccare la prova in corso.
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.request

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
PROVA = f"{BASE}/prova_in_avanti.json"
CAMM = f"{BASE}/cammino_posizioni.json"
REPO = "nicolostancato-web/whale-radar"
CRED = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")


def su_github(percorso):
    try:
        t = re.search(r"ghp_[A-Za-z0-9]+", open(CRED).read()).group(0)
        u = f"https://api.github.com/repos/{REPO}/contents/{percorso}"
        r = urllib.request.Request(u, headers={"Authorization": f"token {t}"})
        import base64
        c = base64.b64decode(json.load(urllib.request.urlopen(r, timeout=40))["content"])
        return hashlib.sha256(c).hexdigest()
    except Exception:
        return None


def main():
    guai = []
    st = json.load(open(PROVA))
    db = json.load(open(CAMM)) if os.path.exists(CAMM) else {"monete": {}}
    m = db.get("monete", {})
    pos = st["posizioni"]
    oper = {k for k, v in pos.items() if v["stato"] in ("aperta", "chiusa") and v.get("entrata")}

    # 1) corrispondenza
    manca_db = oper - set(m)
    in_piu = set(m) - oper
    if manca_db:
        guai.append(f"{len(manca_db)} posizioni operative SENZA record nel cammino")
    if in_piu:
        guai.append(f"{len(in_piu)} record nel cammino senza posizione operativa")

    # 2) record vecchi
    bn = db.get("blocco") or 0
    vecchi = [t for t, v in m.items()
              if bn and v.get("aggiornato_al_blocco", 0) < bn - 20000]
    if vecchi:
        guai.append(f"{len(vecchi)} record non aggiornati da oltre mezz'ora di blocchi")

    # 3) attributi attesi per eta'
    attesi = [("a_5min", 3000), ("a_15min", 9000), ("a_1h", 36000), ("a_4h", 144000)]
    buchi = 0
    for t, v in m.items():
        eta = bn - v.get("blocco_entrata", bn)
        for k, w in attesi:
            if eta > w * 1.5 and v.get(k) is None:
                buchi += 1
    if buchi:
        guai.append(f"{buchi} attributi mancanti su posizioni abbastanza vecchie per averli")

    # 4) denominatore
    noti = st.get("pool_noti") or {}
    # UN POOL APPENA CREATO NON E' UN BUCO (9/10). La sua finestra del primo minuto non e' ancora
    # passata, quindi e' giusto che non abbia un esito: contarlo faceva gridare al lupo a ogni
    # giro, e una guardia che grida al lupo si impara a ignorarla — peggio che non averla.
    # Si contano solo i pool la cui finestra E' passata e che restano senza stato.
    FINESTRA = 600
    ult = st.get("ultimo_blocco") or 0
    senza = [pid for pid, v in noti.items()
             if v[1] not in pos and ult > v[2] + FINESTRA + 1200]
    if senza:
        guai.append(f"{len(senza)} pool con finestra passata e SENZA stato "
                    f"(denominatore incompleto)")

    # 5) copia su GitHub
    loc = hashlib.sha256(open(CAMM, "rb").read()).hexdigest()
    rem = su_github(CAMM)
    if rem is None:
        guai.append("non riesco a leggere la copia su GitHub: non dico che e' al sicuro")
    elif rem != loc:
        guai.append("la copia su GitHub e' DIVERSA dalla locale")

    # 6bis) NESSUNA POSIZIONE DEVE RESTARE APERTA OLTRE L'ORIZZONTE (10/10). Se una ci resta, la
    # regola non e' stata applicata e quella posizione non entrera' mai nel conto: un campione
    # che perde le perdenti e' il difetto peggiore possibile qui.
    ORIZZONTE = 600000
    ult = st.get("ultimo_blocco") or 0
    scadute = [k for k, v in pos.items()
               if v["stato"] == "aperta" and ult - v.get("primo_blocco", ult) > ORIZZONTE]
    if scadute:
        guai.append(f"{len(scadute)} posizioni APERTE oltre l'orizzonte: la regola non e' stata "
                    f"applicata ({', '.join(t[:10] for t in scadute[:4])})")

    # 6) le chiuse restano tracciate
    chiuse = {k for k, v in pos.items() if v["stato"] == "chiusa"}
    chiuse_senza = chiuse - set(m)
    if chiuse_senza:
        guai.append(f"{len(chiuse_senza)} posizioni chiuse non piu' tracciate")

    att = len({k for v in m.values() for k in v})
    if guai:
        print(f"INTEGRITA' | {len(guai)} PROBLEMI:")
        for g in guai:
            print(f"   - {g}")
    else:
        print(f"INTEGRITA' | tutto in regola: {len(m)} record, {att} attributi, "
              f"{len(pos)} pool archiviati, copia su GitHub identica", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
