# -*- coding: utf-8 -*-
"""I PREZZI, con un giro tutto loro.

Perche' esiste (3/11 sera, trovato dal C-check). Il rinfresco dei prezzi
stava dentro il giro del laghetto, che a ogni nona passata legge tutta la
storia di Aave: 202 finestre, 88.183 debitori, mezz'ora. Il controllo
"rigenera se piu' vecchi di 300 secondi" era giusto, ma veniva raggiunto
solo all'inizio del giro successivo -- quindi i prezzi arrivavano a 24
minuti di eta' con tutti gli altri indicatori verdi.

LA LEZIONE, che vale oltre questo file: un passo lungo dentro un giro
AFFAMA tutti gli altri passi di quel giro, e la soglia di freschezza non
ci puo' niente. Quello che deve essere fresco *sempre* vuole un giro suo.

Costa 67 letture all'oracolo ogni due minuti, cioe' niente. Dichiara il
proprio pid, quindi guardia.sh lo sorveglia come gli altri tre.
"""
import json, os, subprocess, sys, time
OGNI = int(sys.argv[1]) if len(sys.argv) > 1 else 120
D = "data/liquidazioni"
VITA = f"{D}/prezzi_sempre_vivo.json"
FILE = f"{D}/prezzi_oracolo.json"
def battito(**extra):
    d = {"pid": os.getpid(), "quando": time.time(),
         "ultimo": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
    d.update(extra)
    tmp = VITA + ".tmp"
    with open(tmp, "w") as f: json.dump(d, f)
    os.replace(tmp, VITA)      # mai un file di vita mezzo scritto
def main():
    giri = rifatti = falliti = 0
    t0 = time.time()
    while True:
        giri += 1
        eta = int(time.time() - os.path.getmtime(FILE)) if os.path.exists(FILE) else 99999
        if eta >= OGNI:
            r = subprocess.run([".venv_bot2/bin/python", "agents/prezzi_dall_oracolo.py"],
                               capture_output=True, text=True, timeout=180)
            # il generatore ha i suoi due cancelli (non sovrascrive se trova
            # meno della meta' degli asset o meno dell'80% del conteggio
            # precedente): qui si guarda solo se il file si e' mosso
            nuova = int(time.time() - os.path.getmtime(FILE)) if os.path.exists(FILE) else 99999
            if nuova < eta: rifatti += 1
            else:
                falliti += 1
                print(f"   prezzi NON rigenerati (eta {nuova}s): "
                      f"{(r.stdout or r.stderr or '')[-160:]}")
        battito(giri=giri, rifatti=rifatti, falliti=falliti,
                eta_prezzi=int(time.time()-os.path.getmtime(FILE)) if os.path.exists(FILE) else -1,
                minuti=round((time.time()-t0)/60, 1), ogni=OGNI)
        time.sleep(20)
if __name__ == "__main__":
    main()
