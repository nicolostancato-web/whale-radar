"""La regola dichiarata PRIMA, misurata in avanti sulle monete che nascono da adesso.

PERCHE' (18/10). Sul passato la regola rende +16,37% su 1.604 monete, con intervallo stretto e
stabile nelle due meta'. Ma in questa settimana ogni volta che un calcolo diceva di si' senza
che nessuno lo stesse facendo con successo, il calcolo aveva torto — e la ragione era sempre
la stessa: avevo scelto qualcosa guardando come era andata. Qui la regola e' CONGELATA prima
di vedere i dati, e si misura solo su monete nate dopo l'accensione.

LA REGOLA, dichiarata il 18/10/2026 e non piu' toccabile:
  - solo monete la cui tassa del creatore e' ZERO (leggibile dal primo acquisto)
  - si entra al primo prezzo disponibile dopo 4 secondi dalla nascita
  - si esce al triplo, oppure dopo 10 minuti al prezzo che c'e'
  - costo applicato: 2% (1% per lato), perche' su queste monete la tassa non c'e'
  - se dopo l'entrata non scambia piu' nessuno, la posizione vale quanto messo meno il costo
    (misurato: una posizione ferma conserva il 96% del valore su 483 casi)

Nessun euro viene speso: si registra cosa SAREBBE successo.
"""
import json
import os
import sys
import time

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import bot_curva as B                                          # noqa: E402
import curva_pons as CP                                        # noqa: E402

STATO = "data/multichain/robinhood/prova_tassa_zero.json"
ENTRO = 4.0
BERSAGLIO = 3.0
MINUTI = 10
COSTO = 1.02


def carica():
    if os.path.exists(STATO):
        return json.load(open(STATO))
    return {"ultimo_blocco": 0, "monete": {}, "nata_il": int(time.time())}


def salva(st):
    os.makedirs(os.path.dirname(STATO), exist_ok=True)
    tmp = STATO + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f)
    os.replace(tmp, STATO)


def main():
    st = carica()
    # 19/10: quando l'RPC inciampa, chiama() torna None e qui usciva un TypeError
    # illeggibile che rompeva il recupero notturno. Un guasto si dice, non si traveste.
    bn = B.chiama("eth_blockNumber", [])
    if not bn:
        print("PROVA TASSA ZERO | l'RPC non da la testa: non invento un blocco")
        return 1
    testa = int(bn, 16)
    if not st["ultimo_blocco"]:
        st["ultimo_blocco"] = testa - 1
        salva(st)
        print(f"PROVA TASSA ZERO | accesa al blocco {testa:,}: da qui in avanti, niente passato")
        return 0
    da = st["ultimo_blocco"] + 1
    a = min(testa, da + 29_999)
    if a <= da:
        return 0
    nas = B.chiama("eth_getLogs", [{"fromBlock": hex(da), "toBlock": hex(a),
                                    "topics": [CP.T_LANCIO]}])
    sc = B.chiama("eth_getLogs", [{"fromBlock": hex(da), "toBlock": hex(a),
                                   "topics": [CP.T_COMPRA]}])
    # ANCHE LE VENDITE: senza, la serie dei prezzi non vede le discese (18/10).
    sv = B.chiama("eth_getLogs", [{"fromBlock": hex(da), "toBlock": hex(a),
                                   "topics": [CP.T_VENDE]}])
    if nas is None or sc is None or sv is None:
        print("PROVA TASSA ZERO | lettura fallita: non avanzo il segnalibro")
        return 0
    for l in nas:
        cur = "0x" + l["topics"][2][-40:]
        st["monete"].setdefault(cur, {"nascita": int(l["blockNumber"], 16),
                                      "tassa": None, "p0": None, "esito": None,
                                      "max": 1.0, "ultimo": None})
    for l, verso in sorted([(x, "c") for x in sc] + [(x, "v") for x in sv],
                           key=lambda z: (int(z[0]["blockNumber"], 16),
                                          int(z[0].get("logIndex", "0x0"), 16))):
        cur = l["address"].lower()
        m = st["monete"].get(cur)
        if m is None or m["esito"] is not None:
            continue
        d = l["data"][2:]
        if len(d) < 256:
            continue
        x0 = int(d[:64], 16) / 1e18
        y0 = int(d[64:128], 16) / 1e18
        if x0 <= 0 or y0 <= 0:
            continue
        val, get = (x0, y0) if verso == "c" else (y0, x0)
        b = int(l["blockNumber"], 16)
        if m["tassa"] is None:
            if verso != "c":
                continue
            m["tassa"] = round(int(d[192:256], 16) / 1e18 / val, 5)
        if m["tassa"] >= 0.005:
            m["esito"] = {"verso": "scartata", "rendimento": None}
            continue
        prezzo = val / get
        if m["p0"] is None:
            if (b - m["nascita"]) * 0.093 < ENTRO:
                continue
            m["p0"] = prezzo
            m["blocco_entrata"] = b
            continue
        x = prezzo / m["p0"]
        m["ultimo"] = round(x, 5)
        m["max"] = max(m["max"], round(x, 5))
        if x >= BERSAGLIO:
            m["esito"] = {"verso": "bersaglio", "rendimento": round(BERSAGLIO / COSTO - 1, 4)}
        elif (b - m["blocco_entrata"]) * 0.093 > MINUTI * 60:
            m["esito"] = {"verso": "tempo", "rendimento": round(x / COSTO - 1, 4)}
    # LA SCADENZA SI MISURA SULL'OROLOGIO, NON SUL PROSSIMO SCAMBIO (18/10). Chiudevo allo
    # scadere dei dieci minuti solo quando arrivava un altro scambio: ma le monete che
    # muoiono subito — il 14%, proprio quelle che devono contare come «uscita in pari meno
    # il costo» — non ne hanno piu' nessuno, e restavano aperte per sempre. Il campione
    # accumulava solo le vive: la stessa selezione dei sopravvissuti, in diretta.
    for cur, m in st["monete"].items():
        if m.get("p0") and not m.get("esito"):
            if (a - m["blocco_entrata"]) * 0.093 > MINUTI * 60:
                x = m.get("ultimo") or 1.0
                m["esito"] = {"verso": "tempo", "rendimento": round(x / COSTO - 1, 4),
                              "senza_scambi": m.get("ultimo") is None}
    st["ultimo_blocco"] = a
    salva(st)
    tot = st["monete"]
    aperte = [m for m in tot.values() if m["p0"] and not m["esito"]]
    chiuse = [m for m in tot.values() if m["esito"] and m["esito"]["rendimento"] is not None]
    print(f"PROVA TASSA ZERO | blocchi {da:,}-{a:,} | {len(tot)} monete viste, "
          f"{len(aperte)} in corso, {len(chiuse)} chiuse", flush=True)
    if len(chiuse) >= 20:
        import statistics
        r = [m["esito"]["rendimento"] for m in chiuse]
        sd = statistics.stdev(r) if len(r) > 1 else 0
        print(f"   resa {statistics.mean(r)*100:+.2f}% ± {1.96*sd/len(r)**0.5*100:.1f} "
              f"su {len(r)} monete | in utile {sum(1 for x in r if x>0)}/{len(r)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
