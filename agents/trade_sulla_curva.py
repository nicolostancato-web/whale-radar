"""IL TRADE SULLA CURVA: comprare a 3,8 ETH incassati, vendere ALLA CURVA.

== PERCHE' (8/10/2026, sera) ==

Il trade nel pool e' bocciato: comprare ogni diplomata comprabile perde a qualunque soglia di
uscita (-15,6% a 1,3x fino a -2,6% a 3x), e il motivo e' che l'**82,1% dei pool e' muto** — non
c'e' nessuno a cui vendere.

Sulla curva e' diverso in un punto che decide: **il compratore e' il contratto**. Non serve che
arrivi qualcuno; la curva ricompra sempre, a un prezzo che la sua formula determina.

E il premio c'e': il segnale «curva a >=3,8 ETH entro 60 minuti» cattura il 91,8% dei diplomi con
quasi zero falsi allarmi, e al diploma resta ancora **+83,9%** di salita (mediana), perche' la
curva e' convessa — al 90% del denaro raccolto il prezzo ha fatto solo 6,49x dei 12,25x.

== LE DUE REGOLE, SCRITTE PRIMA DI MISURARE ==

- **entrata**: il primo acquisto che porta l'incassato cumulato a >= 3,8 ETH. Prezzo pagato: quello
  di quell'acquisto (contiene gia' lo scivolamento di chi l'ha fatto davvero).
- **uscita A, prudente**: l'**ultima** vendita osservata sulla curva prima che si chiuda.
- **uscita B, con obiettivo**: la **prima** vendita osservata a >= 1,5x il prezzo d'entrata;
  se non arriva, l'ultima.

I prezzi di uscita sono quelli di vendite **realmente eseguite** sulla curva: contengono lo
scivolamento della curva, che e' esattamente la voce che si vuole misurare e non immaginare.

Costi: 1% in entrata e 1% in uscita (le commissioni misurate sulla curva).

== IL CAMPIONE ==

Le diplomate del campione **casuale vero** (lanci a caso -> diploma verificato sulla chain), non
quelle del nostro registro: e' il difetto che oggi ha fatto ritirare due risultati.
"""
import gzip
import json
import os
import statistics
import sys
import time
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as CP                                      # noqa: E402


# UNA SOLA LIBRERIA DI LETTURA (11/10, prescrizione di Astra). `curva_lanci` e `coppie` erano
# oggetti unici da 52 e 16,6 MB: per aggiungere un dato si riscriveva tutto, e ogni riscrittura
# entrava INTERA nella storia di git. Ora stanno a righe, e queste due funzioni nascondono quale
# forma c'e' sul disco: se cambia di nuovo, cambia in agents/archivio.py e non in dodici file.
def _lanci_interi():
    import archivio as _AR
    _t, _v = _AR.leggi("curva_lanci")
    _d = dict(_t)
    _d["da"] = _v
    return _d


def _coppie():
    import archivio as _AR
    return _AR.leggi("coppie", "coppie")[1]


CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
DENTRO = f"{BASE}/diplomate_vere.jsonl"
ARCH = f"{BASE}/trade_sulla_curva.jsonl"
SOGLIA = float(os.environ.get("SOGLIA_ETH", "3.8"))
COSTO = 1.02
BUDGET = int(os.environ.get("BUDGET_SEC", "2500"))


def main():
    dl = _lanci_interi()
    L, assets = dl["da"], dl["assets"]
    dip = [json.loads(l) for l in open(DENTRO) if l.strip()]
    dip = [d for d in dip if d.get("diplomata")]
    fatte = set()
    if os.path.exists(ARCH):
        for l in open(ARCH):
            if l.strip():
                try:
                    fatte.add(json.loads(l)["moneta"])
                except Exception:
                    pass
    print(f"CURVA | {len(dip)} diplomate casuali, {len(fatte)} gia' fatte", flush=True)
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("CURVA | la chain non risponde.")
        return 0
    t0 = time.time()
    n = 0
    with open(ARCH, "a", buffering=1) as f:
        for d in dip:
            tok = d["moneta"]
            if tok in fatte:
                continue
            if time.time() - t0 > BUDGET:
                print("CURVA | finito il tempo: l'archivio resta.", flush=True)
                break
            v = L[tok]
            curva = v["curva"].lower()
            a = assets.get((v.get("quote") or "").lower(), {})
            if a.get("simbolo") != "NATIVO" or a.get("decimali") is None:
                continue                  # una valuta sola: 3,8 ETH e' una soglia in ETH
            valute = {curva: (a.get("simbolo"), a.get("decimali"))}
            comp = CP.log_di_finestra(CP.T_COMPRA, v["blocco"],
                                      min(bn, v["blocco"] + 9999999), indirizzo=curva)
            vend = CP.log_di_finestra(CP.T_VENDE, v["blocco"],
                                      min(bn, v["blocco"] + 9999999), indirizzo=curva)
            if comp is None or vend is None:
                continue
            B = [CP._riga(x, "compra", valute) for x in comp]
            B = [r for r in B if r and r["valuta"] > 0 and r["gettoni"] > 0]
            S = [CP._riga(x, "vende", valute) for x in vend]
            S = [r for r in S if r and r["valuta"] > 0 and r["gettoni"] > 0]
            n += 1
            B.sort(key=lambda r: (r["blocco"], r["ordine"]))
            S.sort(key=lambda r: (r["blocco"], r["ordine"]))
            cum = 0.0
            entrata = None
            quando = None
            for r in B:
                cum += r["valuta"]
                if cum >= SOGLIA:
                    entrata = r["valuta"] / r["gettoni"]
                    quando = (r["blocco"], r["ordine"])
                    break
            rec = {"moneta": tok, "acquisti": len(B), "vendite": len(S)}
            if entrata is None:
                rec["esito"] = f"la curva non ha mai raccolto {SOGLIA} ETH"
            else:
                dopo = [r for r in S if (r["blocco"], r["ordine"]) > quando]
                rec["entrata"] = entrata
                rec["vendite_dopo"] = len(dopo)
                if not dopo:
                    # NESSUNA vendita dopo l'entrata: non significa «non si poteva vendere»,
                    # significa che nessuno ha venduto. Il prezzo di uscita non lo so, e non lo
                    # invento: la moneta si dichiara e non entra nelle medie.
                    rec["esito"] = "nessuna vendita osservata dopo l'entrata"
                else:
                    ultima = dopo[-1]["valuta"] / dopo[-1]["gettoni"]
                    primo15 = next((r["valuta"] / r["gettoni"] for r in dopo
                                    if r["valuta"] / r["gettoni"] >= 1.5 * entrata), None)
                    rec["esito"] = "misurata"
                    rec["uscita_A_ultima"] = round(ultima / (entrata * COSTO) - 1, 4)
                    rec["uscita_B_15x"] = round(
                        ((primo15 if primo15 else ultima) / (entrata * COSTO) - 1), 4)
                    rec["max_vendita"] = round(
                        max(r["valuta"] / r["gettoni"] for r in dopo) / entrata, 3)
            f.write(json.dumps(rec) + "\n")
            time.sleep(0.25)
            if n % 40 == 0:
                print(f"CURVA | {n} fatte, {int(time.time()-t0)}s", flush=True)

    tutte = [json.loads(l) for l in open(ARCH) if l.strip()]
    c = collections.Counter(x["esito"] for x in tutte)
    print(f"\nCURVA | {len(tutte)} diplomate esaminate:")
    for k, val in c.most_common():
        print(f"   {val:4}  {k}")
    mis = [x for x in tutte if x["esito"] == "misurata"]
    if len(mis) >= 40:
        for k, nome in (("uscita_A_ultima", "esco all'ultima vendita prima del diploma"),
                        ("uscita_B_15x", "esco alla prima vendita a >=1,5x")):
            r = [x[k] for x in mis]
            print(f"\nCURVA | {nome}:")
            print(f"   medio {100*statistics.mean(r):+.1f}%, mediano {100*statistics.median(r):+.1f}%, "
                  f"in guadagno {sum(1 for v in r if v>0)}/{len(r)}")
        mx = sorted(x["max_vendita"] for x in mis)
        print(f"\n   migliore prezzo di VENDITA dopo l'entrata: mediana {mx[len(mx)//2]:.2f}x, "
              f"90% {mx[int(.9*len(mx))]:.2f}x")
    else:
        print(f"\nCURVA | solo {len(mis)} misurabili: sotto 40 non concludo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
