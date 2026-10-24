"""Le PORTE o le PERSONE: quale famiglia di attributi vale, deciso con il criterio scritto PRIMA.

PERCHE' ESISTE (2/10, scritto mentre l'insieme e' ancora in costruzione, quindi PRIMA di vedere
un solo numero). Il 25/09 abbiamo misurato che il campo usato come «chi ha fatto lo scambio» e'
il ROUTER nell'81% dei casi. Cinque attributi su trentatre misuravano quindi porte, non gente:
compratori, scambi_per_portafoglio, gini_portafogli, quota_primo_portafoglio,
quota_portafogli_nuovi_dopo.
Da stanotte accanto a quei cinque ce ne sono sei sulle PERSONE vere (`pers_*`). Per la prima
volta si possono confrontare sugli STESSI pool.

PERCHE' IL CRITERIO SI SCRIVE PRIMA. Guardando i numeri e poi scegliendo come giudicarli si
trova sempre il modo di dire quello che fa comodo: e' la trappola che Grok ha chiamato
`adaptive overfitting`, e stanotte ci sono finito due volte (il +16% che era futuro, la lista
generata dalla variante sbagliata «perche' la credevo la piu' grande»).

IL CRITERIO, dichiarato ora:
  Si fanno TRE ricerche sugli stessi pool e sugli stessi tre pezzi di tempo:
    A) solo i cinque attributi sui ROUTER (piu' quelli neutri, che non riguardano i partecipanti)
    B) solo i sei attributi sulle PERSONE (piu' gli stessi neutri)
    C) tutti
  Per ognuna si misura il margine sul pezzo mai visto e il METRO (le combinazioni scelte dalle
  ricerche sul rumore, giudicate sullo stesso pezzo).
  VINCE una famiglia solo se, su ENTRAMBE le chain:
    1. il suo margine supera il proprio metro, e
    2. il suo rendimento ASSOLUTO e' maggiore di quello dell'altra famiglia.
  Se nessuna delle due passa, la risposta e' «nessuna delle due»: e' un esito, non un fallimento.
  Se vince B, i cinque attributi sui router NON si cancellano — si smette di usarli, e la
  differenza resta scritta.

QUELLO CHE QUESTO PROGRAMMA NON FA: non decide niente da solo. Stampa i numeri secondo il
criterio qui sopra. L'adozione passa dalla regola di ripetizione e dai revisori esterni, come
tutto il resto.
"""
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))

ROUTER = ("compratori", "scambi_per_portafoglio", "gini_portafogli",
          "quota_primo_portafoglio", "quota_portafogli_nuovi_dopo")
PERSONE = ("pers_copertura", "pers_distinte", "pers_scambi_per", "pers_gini",
           "pers_quota_prima", "pers_solo_compra", "pers_nuove_dopo")


def giro(chain, ritardo, escludi):
    """Una ricerca con alcuni attributi messi da parte. ESCLUDI e' letto da combinazioni.py."""
    amb = dict(os.environ, CHAIN=chain, RITARDO=str(ritardo),
               ESCLUDI_ATOMI=",".join(escludi))
    r = subprocess.run([sys.executable, "-B", os.path.join(QUI, "combinazioni.py")],
                       capture_output=True, text=True, timeout=5400, env=amb)
    marg = metro = assoluto = None
    for riga in r.stdout.splitlines():
        if "margine vero" in riga and "contro il metro" in riga:
            try:
                marg = float(riga.split("margine vero")[1].split("%")[0].strip().replace("+", ""))
                metro = float(riga.split("contro il metro")[1].split("%")[0].strip().replace("+", ""))
            except Exception:
                pass
        if "IN MEDIA le dieci migliori" in riga:
            try:
                assoluto = float(riga.split("fanno")[1].split("%")[0].strip().replace("+", ""))
            except Exception:
                pass
    return marg, metro, assoluto, r.stdout


def copertura(chain):
    """La copertura mediana delle persone nell'insieme: se e' zero, il confronto non ha senso."""
    import gzip
    import json
    import statistics
    p = f"data/loop1/insieme_{chain}_sc5.jsonl.gz"
    if not os.path.exists(p):
        return None
    v = []
    for l in gzip.open(p, "rt"):
        if not l.strip():
            continue
        x = json.loads(l)
        if x.get("pers_copertura") is not None:
            v.append(x["pers_copertura"])
    return statistics.median(v) if v else 0.0


def main():
    chain_e = os.environ.get("CHAIN_E", "robinhood,base").split(",")
    # NON SI CONFRONTA UNA FAMIGLIA CHE NON E' ANCORA STATA RISOLTA (2/10). Gli attributi sulle
    # persone sono entrati nell'insieme con `pers_copertura` a mediana ZERO: presenti e vuoti,
    # perche' la catena che li popola (lista -> iniziatori -> ricostruzione) e' al secondo
    # passo. Girando il confronto adesso uscirebbe «le persone non valgono», per un motivo che
    # non ha niente a che fare con le persone — e sarebbe un verdetto falso scritto nel registro.
    # Questa e' la ragione per cui `pers_copertura` esiste: un attributo deve poter dire quando
    # non sa.
    minima = float(os.environ.get("COPERTURA_MINIMA", 0.30))
    for chain in chain_e:
        c = copertura(chain)
        if c is None:
            raise SystemExit(f"PORTE O PERSONE | manca l'insieme di {chain}: non confronto niente")
        if c < minima:
            raise SystemExit(
                f"PORTE O PERSONE | {chain}: copertura delle persone al {100*c:.0f}% "
                f"(serve almeno il {100*minima:.0f}%). NON confronto: il risultato direbbe «le "
                f"persone non valgono» mentre la verita' e' che non sono ancora risolte. "
                f"Fai girare agents/iniziatori.py e ricostruisci l'insieme.")
        print(f"   {chain}: copertura delle persone {100*c:.0f}%, si puo' confrontare", flush=True)
    ritardo = int(os.environ.get("RITARDO", 2))
    esiti = {}
    for chain in chain_e:
        for eti, escludi in (("A router", PERSONE), ("B persone", ROUTER), ("C tutti", ())):
            marg, metro, ass, testo = giro(chain, ritardo, escludi)
            esiti[(chain, eti)] = (marg, metro, ass)
            def n(v):
                return f"{v:+6.1f}%" if v is not None else "   n/d"
            print(f"   {chain:10s} {eti:10s} margine {n(marg)}  metro {n(metro)}  "
                  f"assoluto {n(ass)}"
                  + ("   batte il proprio metro" if (marg is not None and metro is not None
                                                     and marg > metro) else ""), flush=True)
    print("\n   IL VERDETTO, col criterio scritto prima di guardare:", flush=True)
    for eti, altra in (("A router", "B persone"), ("B persone", "A router")):
        ok = []
        for chain in chain_e:
            m, me, a = esiti.get((chain, eti), (None, None, None))
            m2, _, a2 = esiti.get((chain, altra), (None, None, None))
            ok.append(m is not None and me is not None and m > me
                      and a is not None and a2 is not None and a > a2)
        print(f"      {eti}: {'VINCE su entrambe le chain' if all(ok) else 'non passa'}",
              flush=True)
    print("      (se nessuna passa, la risposta e' «nessuna delle due»: e' un esito)",
          flush=True)


if __name__ == "__main__":
    main()
