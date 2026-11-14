"""Raccoglie l'hook di ogni pool V4, con segnalibro, per misurare quanto pesa il problema.

Un terzo dei pool V4 di base ha un hook, e TUTTI quelli visti hanno i permessi per intervenire
sulla vendita o trattenere il ricavato. Non vuol dire che siano truffe — molti hook legittimi fanno
contabilita' dopo lo swap — ma vuol dire che su quei pool NON possiamo affermare, guardando solo
gli scambi, che si sarebbe potuto uscire.

Il segnalibro ricorda **per quali pool** e' gia' stato fatto, non solo quanti: e' l'errore del
recupero nascite, che saltava per sempre i pool nuovi (23/09).
"""
import gzip
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hook_v4 as H                                            # noqa: E402

CHAIN = os.environ.get("CHAIN", "base")
BUDGET = int(os.environ.get("BUDGET_SEC", 1500))
PAUSA = float(os.environ.get("PAUSA", 0.25))
FUORI = f"data/multichain/{CHAIN}/hook.json"


def main():
    t0 = time.time()
    noti = {}
    if os.path.exists(FUORI):
        try:
            noti = json.load(open(FUORI)).get("hook", {})
        except Exception:
            noti = {}
    da_fare = []
    for sub in ("storico", "vivo"):
        d = f"data/multichain/{CHAIN}/{sub}"
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            p = fn.split(".")[0]
            if len(p) != 66 or p in noti:
                continue                      # 66 = identificativo V4; gli altri hanno indirizzo
            da_fare.append((p, os.path.join(d, fn)))
    print(f"HOOK | {CHAIN}: {len(noti)} gia' noti, {len(da_fare)} da fare", flush=True)
    fatti = 0
    for p, percorso in da_fare:
        if time.time() - t0 > BUDGET:
            break
        try:
            bl = [x.get("blocco") for x in
                  (json.loads(l) for l in gzip.open(percorso, "rt") if l.strip())
                  if x.get("blocco")]
        except Exception:
            continue
        if not bl:
            continue
        h, c0, c1 = H.nascita_di(p, min(bl))
        if h is None:
            time.sleep(2)                     # il nodo non risponde: si rallenta, non si scrive
            continue
        tipo, attivi = H.descrivi(h)
        noti[p] = {"hook": h, "tipo": tipo,
                   "puo_toccare_uscita": bool(set(attivi) & H.PERICOLOSI),
                   "t0": c0, "t1": c1}        # la coppia: serve per la trappola a due pool
        fatti += 1
        if fatti % 25 == 0:
            json.dump({"acq": int(time.time()), "hook": noti}, open(FUORI, "w"))
            print(f"HOOK | {fatti} nuovi", flush=True)
        time.sleep(PAUSA)
    os.makedirs(os.path.dirname(FUORI), exist_ok=True)
    json.dump({"acq": int(time.time()), "hook": noti}, open(FUORI, "w"))
    con = sum(1 for v in noti.values() if v["tipo"] == "con_hook")
    per = sum(1 for v in noti.values() if v.get("puo_toccare_uscita"))
    print(f"HOOK | {CHAIN}: {fatti} nuovi in {time.time()-t0:.0f}s | totale {len(noti)} | "
          f"con hook {con} ({100*con/max(1,len(noti)):.0f}%) | "
          f"che possono toccare l'uscita {per} ({100*per/max(1,len(noti)):.0f}%)", flush=True)


if __name__ == "__main__":
    main()
