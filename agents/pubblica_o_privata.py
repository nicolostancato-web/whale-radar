# -*- coding: utf-8 -*-
"""GLI AGGIORNAMENTI DELL'ORACOLO PASSANO DALLA MEMPOOL PUBBLICA?

PERCHE' ESISTE (6/11). Sentiamo il 15,8% degli aggiornamenti Chainlink, e
stavo per investire tempo (o soldi) per alzare quella copertura. Ma ci sono
DUE spiegazioni possibili e portano a decisioni opposte:
  1. il nostro punto di osservazione e' povero -> conviene allargarlo
  2. quegli aggiornamenti NON passano dalla mempool pubblica (inviati
     privatamente ai costruttori, come fa chiunque non voglia essere
     anticipato) -> nessuna copertura pubblica potra' mai vederli, e la
     strada della campanella ha un tetto che non si supera
Si distinguono con UN confronto: quale frazione vediamo delle transazioni
NORMALI dello stesso blocco. Se vediamo il 90% delle normali e il 16% di
quelle dell'oracolo, sono private. Se vediamo il 16% di tutto, siamo noi.

E' il filtro delle osservazioni applicato a una decisione di investimento:
si misura PRIMA di spendere, non dopo.
"""
import sys, json, time, threading
sys.path.insert(0, "agents")
import occhio_ws as O, vendita_curve as VC
INOLTRA = "0x6fadcf72"
MINUTI = float(__import__("os").environ.get("MINUTI", "11"))
visti = set()
def main():
    stop = []
    def senti(tx, porta):
        h = (tx.get("hash") or "").lower()
        if h: visti.add(h)
    # tutte le porte che PORTANO qualcosa, senza filtro di selettore
    O.ascolta_tutte(senti, selettore=None, ferma=lambda: bool(stop),
                    porte=["wss://ethereum-rpc.publicnode.com", "wss://eth.drpc.org"])
    b0 = int(VC._rpc("eth_blockNumber", []), 16)
    time.sleep(MINUTI * 60)
    stop.append(1); time.sleep(1)
    b1 = int(VC._rpc("eth_blockNumber", []), 16)
    tot_n = presi_n = tot_o = presi_o = 0
    for b in range(b0 + 2, b1 - 1):       # si salta il primo e l'ultimo: finestra parziale
        bl = VC._rpc("eth_getBlockByNumber", [hex(b), True]) or {}
        for t in (bl.get("transactions") or []):
            h = (t.get("hash") or "").lower()
            if (t.get("input") or "0x").startswith(INOLTRA):
                tot_o += 1; presi_o += 1 if h in visti else 0
            else:
                tot_n += 1; presi_n += 1 if h in visti else 0
    print(f"   ascoltato {b1-b0} blocchi, {len(visti)} hash in mano")
    print(f"   transazioni NORMALI:        {presi_n:>5} su {tot_n:>5} = "
          f"{100*presi_n/max(tot_n,1):.1f}%")
    print(f"   aggiornamenti dell'ORACOLO: {presi_o:>5} su {tot_o:>5} = "
          f"{100*presi_o/max(tot_o,1):.1f}%")
    if tot_o < 25:
        print(f"   NON CONCLUDO sull'oracolo: {tot_o} osservazioni sono poche")
    else:
        qn = presi_n/max(tot_n,1); qo = presi_o/max(tot_o,1)
        if qn > 0.6 and qo < qn/2:
            print("   VERDETTO: il nostro occhio e' buono sulle normali e cieco "
                  "sull'oracolo -> quegli aggiornamenti sono in gran parte PRIVATI, "
                  "e allargare la mempool pubblica NON li portera'.")
        elif qn < 0.4:
            print("   VERDETTO: siamo ciechi su TUTTO allo stesso modo -> il punto "
                  "di osservazione e' povero, allargarlo serve.")
        else:
            print("   VERDETTO: non netto, serve piu' campione.")
    json.dump({"quando": time.time(), "blocchi": b1-b0,
               "normali_viste": presi_n, "normali_totali": tot_n,
               "oracolo_visti": presi_o, "oracolo_totali": tot_o},
              open("data/liquidazioni/pubblica_o_privata.json", "w"), indent=2)
    return 0
if __name__ == "__main__":
    sys.exit(main())
