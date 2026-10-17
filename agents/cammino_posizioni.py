"""IL DATABASE DEL CAMMINO: come si muove ogni moneta dopo che siamo entrati.

== IL MANDATO (Nicolo', 9/10/2026) ==

«Traccia tutti questi dati di tutte queste cripto, devi sapere tutto: minimi e massimi. Perche'
fra cinque giorni magari vediamo che i raddoppi ci sono, pero' se mettiamo uno stop loss al 30%
riusciamo a fare dei soldi. Oppure ci accorgiamo che vanno a -100% ma poi vanno sempre su. Fai un
database ad hoc: non abbiamo tante monete, puoi mettere tanti attributi.»

== LA DOMANDA CHE QUESTO DATABASE DEVE POTER RISPONDERE ==

**Quanto scende una moneta PRIMA di raddoppiare?** Se le vincenti non scendono mai sotto -30%,
allora uno stop al -30% e' gratis: taglia le perdenti e non tocca le vincenti. Se invece le
vincenti passano da -60% prima di salire, quello stesso stop le ammazzerebbe tutte.

E' una domanda che si risponde solo col **cammino**, non col risultato: due posizioni che finiscono
entrambe a +89% possono averci fatto passare una da -10% e l'altra da -70%.

== COSA REGISTRA, PER OGNI POSIZIONE ==

- il prezzo a **orizzonti fissi** dall'entrata: 5 min, 15 min, 1h, 4h, 12h, 24h, 48h, 7 giorni;
- **minimo e massimo** raggiunti, e dopo quanti minuti;
- **la discesa peggiore PRIMA del primo raddoppio** (la risposta alla domanda di sopra);
- quanto denaro e' passato in ogni orizzonte, comprato e venduto;
- il cammino **ridotto**: una mediana ogni 10 scambi, per poter ridisegnare il grafico.

Si aggiorna a ogni giro del loop e **non tocca nessuna regola di decisione**: e' osservazione.
"""
import gzip
import json
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as CP                                      # noqa: E402
import prima_la_prova as PP                                  # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
STATO = f"{BASE}/prova_in_avanti.json"
ARCH = f"{BASE}/cammino_posizioni.json"
GESTORE_V4 = os.environ.get("GESTORE_V4", "0x8366a39cc670b4001a1121b8f6a443a643e40951").lower()
P_ETH = 2575.78
# orizzonti in blocchi (10 blocchi al secondo)
ORIZZONTI = [("5min", 3000), ("15min", 9000), ("1h", 36000), ("4h", 144000),
             ("12h", 432000), ("24h", 864000), ("48h", 1728000), ("7g", 6048000)]


def _prezzo(l, lato, dec):
    n = CP._numeri(l.get("data", "0x"))
    if len(n) < 2:
        return None
    a0 = n[0] - (1 << 256) if n[0] >= (1 << 255) else n[0]
    a1 = n[1] - (1 << 256) if n[1] >= (1 << 255) else n[1]
    qt = a1 if lato == "t1" else a0
    qq = a0 if lato == "t1" else a1
    if qt == 0 or qq == 0:
        return None
    vq = abs(qq) / (10 ** int(dec))
    if vq < 1e-9:
        return None
    # IL VERSO ERA INVERTITO (10/10, verificato sulla chain su 4 casi). Nel Swap di
    # Uniswap v4 gli importi sono quelli dello SCAMBIATORE, non del pool: negativo = lo
    # scambiatore PAGA, positivo = RICEVE. Quindi valuta POSITIVA vuol dire che riceve
    # valuta, cioe' ha VENDUTO il gettone. Il codice diceva `qq < 0`, cioe' il contrario,
    # e tutte le attribuzioni compra/vendi erano scambiate (i prezzi no: usano abs()).
    # Trovato guardando i Transfer del gettone nella stessa transazione: in una vendita il
    # gettone ENTRA nel pool. La prova e' questa, non la convenzione letta in un documento.
    return vq / (abs(qt) / 1e18), vq * P_ETH if int(dec) == 18 else vq, qq > 0


def main():
    st = json.load(open(STATO))
    noti = st.get("pool_noti") or {}
    db = json.load(open(ARCH)) if os.path.exists(ARCH) else {"versione": 2, "monete": {}}
    # versione 2 = ogni punto del cammino porta [blocchi, mediana, minimo, massimo]. La corsia
    # ricalcola tutte le posizioni a ogni giro, quindi non serve migrare: basta dichiararlo,
    # perche' chi legge sappia se puo' fidarsi degli estremi.
    db["versione"] = 2
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("CAMMINO | la chain non risponde.")
        return 0
    quali = [(k, v) for k, v in st["posizioni"].items()
             if v["stato"] in ("aperta", "chiusa") and v.get("entrata")]
    print(f"CAMMINO | {len(quali)} posizioni da tracciare", flush=True)
    agg = 0
    mancate = []
    for tok, pos in quali:
        pid = pos["pool"]
        info = noti.get(pid) or ["t0", tok, pos["primo_blocco"], None, 18]
        lato = info[0]
        dec = info[4] if len(info) > 4 else 18
        inizio = pos["primo_blocco"] + 600          # l'entrata
        ev = CP.log_di_finestra(PP.SWAP_V4, inizio, min(bn, inizio + 9999999),
                                indirizzo=GESTORE_V4, secondo=pid)
        if ev is None:
            mancate.append(tok)
            continue
        serie = []
        for x in ev:
            q = _prezzo(x, lato, dec)
            if q:
                serie.append((int(x["blockNumber"], 16), q[0], q[1], q[2]))
        if not serie:
            continue
        serie.sort()
        e = pos["entrata"]
        rel = [(b, pr / e, den, vende) for b, pr, den, vende in serie]
        d = {"entrata": e, "blocco_entrata": inizio, "stato": pos["stato"],
             "scambi_dopo_entrata": len(rel),
             "aggiornato_al_blocco": bn}
        # orizzonti fissi
        for nome, w in ORIZZONTI:
            dentro = [x for x in rel if x[0] <= inizio + w]
            if not dentro or bn < inizio + w:
                d[f"a_{nome}"] = None            # non ancora trascorso: None, non zero
                continue
            d[f"a_{nome}"] = round(statistics.median([x[1] for x in dentro[-5:]]), 5)
            d[f"comprato_{nome}"] = round(sum(x[2] for x in dentro if not x[3]), 2)
            d[f"venduto_{nome}"] = round(sum(x[2] for x in dentro if x[3]), 2)
        # minimo, massimo e quando
        mn = min(rel, key=lambda x: x[1])
        mx = max(rel, key=lambda x: x[1])
        d["min_x"] = round(mn[1], 5)
        d["min_dopo_minuti"] = round((mn[0] - inizio) / 10 / 60, 1)
        d["max_x"] = round(mx[1], 5)
        d["max_dopo_minuti"] = round((mx[0] - inizio) / 10 / 60, 1)
        # il prezzo ALLA FINE di cio' che si e' visto, e la caduta peggiore picco-valle: serve
        # per capire quanto si sarebbe sofferto tenendo, non solo dove e' arrivata.
        d["ultimo_x"] = round(rel[-1][1], 5)
        d["ultimo_dopo_minuti"] = round((rel[-1][0] - inizio) / 10 / 60, 1)
        picco = 0.0
        caduta = 1.0
        for _b, x, _den, _v in rel:
            picco = max(picco, x)
            if picco > 0:
                caduta = min(caduta, x / picco)
        d["caduta_peggiore_da_un_picco"] = round(caduta, 5)
        # LA DOMANDA CHIAVE: quanto e' scesa PRIMA del primo raddoppio?
        primo2x = next((x for x in rel if x[1] >= 2), None)
        if primo2x:
            prima = [x[1] for x in rel if x[0] <= primo2x[0]]
            d["discesa_peggiore_prima_del_2x"] = round(min(prima), 5)
            d["minuti_per_raddoppiare"] = round((primo2x[0] - inizio) / 10 / 60, 1)
            # quanto AVREBBE continuato a salire se non fossimo usciti al raddoppio: risponde
            # alla domanda «il take profit al 100% e' il migliore?» senza rileggere la chain
            dopo2x = [x[1] for x in rel if x[0] >= primo2x[0]]
            d["massimo_dopo_il_raddoppio"] = round(max(dopo2x), 5) if dopo2x else None
        else:
            d["discesa_peggiore_prima_del_2x"] = None
            d["minuti_per_raddoppiare"] = None
        # CAMPIONAMENTO ADATTIVO (9/10). Con un passo fisso di 10 e un tetto di 400 punti, una
        # moneta con 15.000 scambi (ne esistono) avrebbe il cammino solo dei primi 4.000: il
        # grafico finirebbe a meta' senza che si veda. Il passo si adatta alla lunghezza, cosi'
        # il cammino copre SEMPRE tutta la vita con circa 400 punti.
        passo = max(5, len(rel) // 400)
        d["passo_campionamento"] = passo
        # OGNI CAMPIONE PORTA GLI ESTREMI DEL SUO INTERVALLO (10/10). Prima ogni punto era
        # [blocchi, mediana]: la mediana di cinque scambi NASCONDE un tocco breve. La prova sul
        # database l'ha dimostrato — 0x9f47c581011d ha raddoppiato davvero (max 2,01) e la
        # simulazione sul cammino diceva +14%, perche' quel tocco stava fra due campioni. Uno
        # scarto di 76 punti su un caso solo, e tutte le simulazioni di stop e di uscita
        # sarebbero state sbagliate nello stesso modo invisibile.
        # Adesso il punto e' [blocchi, mediana, minimo, massimo] dell'intervallo: una soglia
        # attraversata non puo' piu' sfuggire, e il grafico resta identico (usa i primi due).
        d["cammino"] = [[rel[i][0] - inizio,
                         round(statistics.median([y[1] for y in rel[i:i+passo]]), 5),
                         round(min(y[1] for y in rel[i:i+passo]), 5),
                         round(max(y[1] for y in rel[i:i+passo]), 5)]
                        for i in range(0, len(rel) - passo + 1, passo)]
        db["monete"][tok] = d
        agg += 1
        time.sleep(0.15)
    db["aggiornato"] = int(time.time())
    db["blocco"] = bn
    json.dump(db, open(ARCH, "w"), indent=1)
    print(f"CAMMINO | aggiornate {agg} posizioni nel database", flush=True)
    if mancate:
        # UN BUCO SI DICHIARA (9/10): una posizione non aggiornata per un errore di lettura
        # resta nel database col dato VECCHIO, e fra cinque giorni sembrerebbe buona.
        print(f"CAMMINO | NON aggiornate per lettura fallita: {len(mancate)} "
              f"({', '.join(t[:10] for t in mancate[:5])}) — il giro prossimo riprova", flush=True)
    vuoti = [t for t, v in db["monete"].items() if not v.get("cammino")]
    if vuoti:
        print(f"CAMMINO | ATTENZIONE: {len(vuoti)} posizioni senza cammino", flush=True)
    # IL DATABASE SI PUBBLICA SUBITO. Vale cinque giorni di accumulo e sta su un Mac: un disco
    # pieno o una pulizia lo cancellerebbe. Lezione pagata il 25/09 perdendo un giorno di lavoro.
    try:
        import subprocess
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                     "pubblica_file.py"), ARCH],
                       capture_output=True, timeout=300)
        print("CAMMINO | database pubblicato su GitHub", flush=True)
    except Exception as e:
        print(f"CAMMINO | pubblicazione non riuscita ({str(e)[:40]}): il file resta in locale")
    # riassunto della domanda chiave, se ci sono dati
    con2x = [v for v in db["monete"].values()
             if v.get("discesa_peggiore_prima_del_2x") is not None]
    if con2x:
        disc = sorted(v["discesa_peggiore_prima_del_2x"] for v in con2x)
        print(f"CAMMINO | sulle {len(con2x)} che hanno raddoppiato, la discesa peggiore PRIMA "
              f"del raddoppio: mediana {disc[len(disc)//2]:.3f}x, peggiore {disc[0]:.3f}x")
        print(f"   (se la peggiore sta sopra 0,70 uno stop al -30% non ne avrebbe ucciso "
              f"nessuna: con {len(con2x)} casi e' un indizio, non una conclusione)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
