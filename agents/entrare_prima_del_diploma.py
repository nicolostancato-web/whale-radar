"""Entrare sulla curva a 3,6 ETH e tenerla fino al mercato: quante X, davvero.

LA TESI DI NICOLO' (11/10): «se la prendi prima della promozione, appena entra nel mercato c'e'
euforia: come fai a non fare almeno un 3 o un 4? Il capitale prima della promozione e' cosi'
basso che e' impossibile.»

E' una tesi precisa e si misura sulle NOSTRE monete, che e' la cosa che nessuna analisi aveva
fatto: le 31 posizioni chiuse della prova in avanti sono monete che si sono diplomate DAVVERO, e
di loro conosciamo tutto il cammino DOPO. Qui si aggiunge il pezzo PRIMA: si torna sulla curva,
si accumula la valuta incassata, si trova il prezzo nel momento in cui la curva arriva a 3,6 ETH,
e da quel prezzo si misura il moltiplicatore fino al mercato.

IL CANCELLO. La documentazione dice che il diploma arriva a 12,25x dal prezzo di apertura, e la
nostra misura indipendente diceva 11,79x di mediana. Se qui la salita dal primo prezzo al diploma
non esce intorno a 11-12x, sto leggendo i prezzi male e **non si guarda nient'altro**: due misure
in due unita' diverse danno un moltiplicatore inventato, e sarebbe il quinto numero ritirato in
due giorni.
"""
import json
import os
import statistics
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

import curva_pons as CP                                        # noqa: E402
import archivio as AR                                          # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
PROVA = f"{BASE}/prova_in_avanti.json"
CAMMINO = f"{BASE}/cammino_posizioni.json"
ARCH = f"{BASE}/entrare_prima_del_diploma.json"
SOGLIA_ETH = float(os.environ.get("SOGLIA_ETH", "3.6"))
QUANTE = int(os.environ.get("QUANTE", "12"))


ASSETS = {}


def curva_di_una_moneta(tok, lanci, bn):
    """Gli acquisti sulla curva, in ordine, con la valuta cumulata e il prezzo di ognuno."""
    L = lanci.get(tok.lower())
    if not L:
        return None, "non trovo il lancio di questa moneta"
    curva = L["curva"].lower()
    dec = (ASSETS.get((L.get("quote") or "").lower()) or {}).get("decimali", 18)
    log = CP.log_di_finestra(CP.T_COMPRA, L["blocco"], min(bn, L["blocco"] + 9_999_999),
                             indirizzo=curva)
    if log is None:
        return None, "la chain non ha risposto"
    righe = []
    for x in log:
        # decimali 18: la quota di queste monete e' nativa. Dove non lo fosse, il prezzo
        # risulterebbe fuori scala e il cancello sotto lo farebbe cadere — che e' il punto.
        # I DECIMALI VENGONO DALLA CURVA, NON DA UNA COSTANTE (11/10, lezione violata da me
        # il giorno stesso in cui l'ho riletta in testa a curva_pons). Tre monete davano 0,000
        # ETH incassati su centinaia di acquisti: la loro valuta non ha 18 decimali, e dividere
        # per 10**18 un importo a 6 decimali lo sottostima di mille miliardi di volte.
        r = CP._riga(x, "compra", {curva: (None, dec)})
        if not r or r["gettoni"] <= 0 or r["valuta"] <= 0:
            continue
        righe.append((r["blocco"], r["ordine"], r["valuta"], r["gettoni"]))
    righe.sort()
    if len(righe) < 5:
        return None, f"solo {len(righe)} acquisti leggibili sulla curva"
    cum = 0.0
    fuori = []
    for b, o, val, get in righe:
        cum += val
        fuori.append({"blocco": b, "cumulato": cum, "prezzo": val / get})
    return fuori, None


def main():
    st = json.load(open(PROVA))
    cam = json.load(open(CAMMINO))["monete"]
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    chiuse = [(t, p) for t, p in st["posizioni"].items() if p["stato"] == "chiusa"]
    _t, lanci = AR.leggi("curva_lanci")
    global ASSETS
    ASSETS = _t.get("assets") or {}
    # L'ARCHIVIO DEI LANCI E' FERMO (11/10): si e' interrotto quando ho spento le corsie, al
    # blocco 81.568.070, e le monete della demo sono nate quattro milioni di blocchi dopo. Le
    # loro curve non sono nell'archivio, quindi si leggono DIRETTAMENTE dalla fabbrica, solo per
    # la finestra che serve. Costa qualche chiamata e vale una misura: l'alternativa era
    # concludere «non misurabile» per un file vecchio.
    primi = min(p["primo_blocco"] for _, p in chiuse)
    recenti, b = {}, primi - 400_000
    while b < bn:
        fine = min(bn, b + 9_999_999)
        lg = CP.log_di_finestra(CP.T_LANCIO, b, fine, indirizzo=CP.FABBRICA)
        if lg is None:
            print(f"   lanci {b:,}-{fine:,}: la chain non ha risposto", flush=True)
            b = fine + 1
            continue
        for ev in lg:
            ind = [CP._indirizzo(t) for t in ev["topics"][1:]]
            if len(ind) < 2:
                continue
            d = ev.get("data", "0x")[2:]
            recenti[ind[0]] = {"curva": ind[1],
                               "creatore": ind[2] if len(ind) > 2 else None,
                               "blocco": int(ev["blockNumber"], 16),
                               "quote": ("0x" + d[24:64]) if len(d) >= 64 else None}
        b = fine + 1
    print(f"   letti {len(recenti):,} lanci recenti dalla fabbrica", flush=True)
    lanci = dict(lanci)
    lanci.update(recenti)
    print(f"PRIMA DEL DIPLOMA | {len(chiuse)} monete diplomate da guardare, "
          f"soglia {SOGLIA_ETH} ETH", flush=True)

    db = json.load(open(ARCH)) if os.path.exists(ARCH) else {"monete": {}}
    fatte = 0
    for tok, p in chiuse:
        if tok in db["monete"] or fatte >= QUANTE:
            continue
        righe, err = curva_di_una_moneta(tok, lanci, bn)
        if righe is None:
            # SI SALVA ANCHE QUANDO NON SI MISURA (bug mio, 11/10): il `continue` saltava il
            # salvataggio in fondo al ciclo, quindi di 31 monete non misurabili non restava
            # traccia e il referto diceva «nessuna misura» senza dire perche'.
            db["monete"][tok] = {"non_misurabile": err}
            fatte += 1
            json.dump(db, open(ARCH, "w"), indent=1)
            continue
        primo = righe[0]["prezzo"]
        ultimo = righe[-1]["prezzo"]
        oltre = [r for r in righe if r["cumulato"] >= SOGLIA_ETH]
        d = {"acquisti_sulla_curva": len(righe),
             "incassato_in_tutto": round(righe[-1]["cumulato"], 4),
             "primo_prezzo": primo,
             "prezzo_al_diploma": ultimo,
             "salita_sulla_curva": round(ultimo / primo, 3) if primo else None,
             "entrata_demo": p.get("entrata"),
             "apertura_pool_su_chiusura_curva": round(p["entrata"] / ultimo, 3) if ultimo else None}
        if oltre:
            p36 = oltre[0]["prezzo"]
            c = cam.get(tok) or {}
            d.update({"prezzo_a_soglia": p36,
                      "resta_fino_al_diploma": round(ultimo / p36, 3),
                      "x_totale_al_massimo_del_mercato":
                          round(p["entrata"] * (c.get("max_x") or 1) / p36, 3)
                          if c.get("max_x") else None,
                      "x_totale_uscendo_al_2x_della_demo":
                          round(p["entrata"] * 2 / p36, 3),
                      "x_totale_come_e_andata_davvero":
                          round(p["entrata"] * (1 + ((p.get("esito") or {}).get("rendimento") or 0))
                                / p36, 3)})
        else:
            d["mai_arrivata_a_soglia"] = True
        db["monete"][tok] = d
        fatte += 1
        json.dump(db, open(ARCH, "w"), indent=1)

    # IL CANCELLO
    sal = [v["salita_sulla_curva"] for v in db["monete"].values()
           if v.get("salita_sulla_curva")]
    print(f"\nCANCELLO | salita dal primo prezzo al diploma, su {len(sal)} monete: "
          f"mediana {statistics.median(sal):.2f}x" if sal else "CANCELLO | nessuna misura")
    if not sal or not (9.0 <= statistics.median(sal) <= 14.0):
        print("CANCELLO | NON e' fra 9x e 14x: sto leggendo i prezzi in due unita' diverse, "
              "e qualunque moltiplicatore sotto sarebbe inventato. Non stampo altro.")
        return 1
    print("CANCELLO | coerente con il 12,25x delle regole e con il nostro 11,79x: i prezzi "
          "sono nella stessa unita', si puo' leggere il resto.\n")

    inc = [v["incassato_in_tutto"] for v in db["monete"].values()
           if v.get("incassato_in_tutto")]
    if inc:
        inc.sort()
        print(f"NOTA | le diplomate hanno incassato, nel MIO conteggio, "
              f"{statistics.median(inc):.2f} ETH di mediana (min {inc[0]:.2f}, max {inc[-1]:.2f}): "
              f"non 4,2. Quindi «3,8 su 4,2 = secchio pieno al 90%» NON vale qui: la soglia e' un "
              f"PREDITTORE osservabile, non una misura di quanto manca al diploma (11/10).\n")
    buone = [v for v in db["monete"].values() if v.get("prezzo_a_soglia")]
    print(f"monete che hanno superato {SOGLIA_ETH} ETH: {len(buone)} su {len(db['monete'])}")
    for nome, chiave in (("resta dalla soglia al diploma", "resta_fino_al_diploma"),
                         ("il pool apre / chiude la curva", "apertura_pool_su_chiusura_curva"),
                         ("X TOTALE al massimo del mercato", "x_totale_al_massimo_del_mercato"),
                         ("X TOTALE uscendo al 2x", "x_totale_uscendo_al_2x_della_demo"),
                         ("X TOTALE come e' andata davvero", "x_totale_come_e_andata_davvero")):
        v = [b[chiave] for b in buone if b.get(chiave)]
        if not v:
            continue
        v.sort()
        print(f"   {nome:<34} mediana {statistics.median(v):>6.2f}x   "
              f"min {v[0]:>5.2f}x   max {v[-1]:>6.2f}x   "
              f"sopra 3x: {sum(1 for x in v if x >= 3)}/{len(v)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
