"""Il processo continuo: il cervello decide, le mani eseguono, nello stesso ciclo.

PERCHE' ESISTE. La corsia su GitHub gira ogni 15 minuti e va benissimo per accumulare lo
storico. Ma il bot rifiuta le decisioni piu' vecchie di 60 secondi — giustamente, perche'
entrare tardi e' la cosa che abbiamo misurato non funzionare — quindi con un ciclo da 15
minuti salterebbe SEMPRE tutto. Andare live non e' «accendere la corsia»: e' un'altra cosa,
un processo che non si ferma mai e in cui fra la decisione e l'ordine passano secondi.

COSA FA, in ordine, per sempre:
  1. una passata del cervello (prova_nella_curva): legge la chain, apre e chiude posizioni
  2. una passata delle mani (bot_curva): esce dalle posizioni chiuse, entra in quelle nuove
  3. scrive un battito con lo stato, cosi' da fuori si vede se e' vivo senza interromperlo

SI FERMA DA SOLO se: il cervello fallisce troppe volte di fila (qualcosa e' rotto), il tetto
cumulato e' raggiunto (ci pensa il bot), o qualcuno cancella il file di marcia.

COSTO. Nodo pubblico e gratuito. L'unica spesa sono le transazioni: 0,007 EUR l'una, dentro
i tetti scritti nel bot (2 EUR a posizione, 40 EUR in tutto).
"""
import json
import os
import subprocess
import sys
import time

QUI = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
BATTITO = "data/multichain/robinhood/live_battito.json"
MARCIA = "/tmp/live_curva.marcia"
PAUSA = float(os.environ.get("PAUSA_SEC", "3"))
# ROTTURE DI FILA PRIMA DI FERMARSI. Una passata che fallisce ogni tanto e' il nodo che
# tossisce; venti di fila sono un guasto, e continuare a girare su un guasto significa
# tenere posizioni aperte che nessuno chiude.
ROTTE_MAX = 20


def passata(script, extra=(), amb=None):
    try:
        o = subprocess.run([PY, "-B", os.path.join(QUI, script), *extra],
                           capture_output=True, text=True, timeout=120, env=amb)
        return o.returncode == 0, (o.stdout or "") + (o.stderr or "")
    except Exception as e:
        return False, f"non parte: {e}"


def main():
    vero = "--vero" in sys.argv
    print(f"LIVE | parto in modo {'VERO (si spende)' if vero else 'A VUOTO'}, "
          f"una passata ogni {PAUSA}s")
    print(f"LIVE | per fermarmi: rm {MARCIA}")
    open(MARCIA, "w").write(str(os.getpid()))
    giri = rotte_cervello = 0
    acquisti = uscite = 0
    t0 = time.time()
    while os.path.exists(MARCIA):
        giri += 1
        # CON LE MANI FUSE IL CERVELLO FA TUTTO (14/10). Chiamarle anche a parte dopo
        # significherebbe due compratori per la stessa decisione.
        amb = dict(os.environ, MANI="1", **({"MANI_VERE": "1"} if vero else {}))
        ok_c, out_c = passata("prova_nella_curva.py", amb=amb)
        rotte_cervello = 0 if ok_c else rotte_cervello + 1
        if rotte_cervello >= ROTTE_MAX:
            print(f"LIVE | il cervello fallisce da {ROTTE_MAX} giri di fila. Mi fermo.")
            print(out_c[-800:])
            break
        ok_b, out_b = True, out_c
        # SI SCRIVE TUTTO QUELLO CHE RIGUARDA I SOLDI. Nel primo giro a vuoto il battito
        # diceva «4 acquisti visti» ma nel diario non c'era una riga: contavo senza
        # registrare, e un numero senza la riga che lo spiega non si puo' controllare.
        for riga in out_b.splitlines():
            # SI REGISTRA ANCHE QUANTE NE VEDE, non solo cosa compra. Senza questa riga non
            # si distingue «il mercato e' fermo» da «il bot non le vede»: nella notte del
            # 13/10 sette occasioni sono passate e il diario era muto in entrambi i sensi.
            if any(x in riga for x in ("MANDATO", "VENDERE", "COMPRARE", "SALTO",
                                       "A VUOTO:", "TETTO TOTALE", "rifiuta", "fallisce")) \
               or ("posizioni aperte" in riga and "ha 0 " not in riga):
                print(f"LIVE | {time.strftime('%H:%M:%S')} {riga.strip()}", flush=True)
        acquisti += out_b.count("COMPRARE")
        uscite += out_b.count("VENDERE")
        os.makedirs(os.path.dirname(BATTITO), exist_ok=True)
        with open(BATTITO, "w") as f:
            json.dump({"giri": giri, "vivo_da_sec": int(time.time() - t0),
                       "ultimo_battito": int(time.time()), "modo": "vero" if vero else "a vuoto",
                       "cervello_ok": ok_c, "mani_ok": ok_b,
                       "acquisti_visti": acquisti, "uscite_viste": uscite,
                       "ultimo_referto_mani": out_b[-1500:]}, f)
        # IL CAMPANELLO, non a ogni giro: ogni 100 passate bastano, e suona solo se si supera
        # una quota nuova. Costa una lettura dei saldi, niente di piu'.
        if giri % 100 == 0:
            passata("squillo.py")
        if giri % 20 == 0:
            print(f"LIVE | {giri} giri in {int(time.time()-t0)}s, "
                  f"{acquisti} acquisti e {uscite} uscite viste")
        time.sleep(PAUSA)
    print("LIVE | fermato.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
