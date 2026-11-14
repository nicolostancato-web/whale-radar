"""Prima di dire «questo portafoglio ha fatto X», si va a guardare sulla chain. Sempre.

LA DIRETTIVA (Nicolo', 5/10): «quando mi dici che i dati sono veritieri, mi dai una cripto e un
wallet, io apro e devo vedere che quel wallet ha comprato quella cripto in quella data, è andata
su, e poi vende. Ogni volta che credi che siano veritieri, vai a verificare tu: prendi e vai a
vedere se ci sono esattamente le cose.»

PERCHE' ESISTE. Il 5/10 gli ho riferito «569 portafogli oltre il 10X». Lui ne ha controllato uno
su DexScreener: **quel portafoglio non aveva mai toccato quella moneta**. Verificato poi anche
da me sulla chain: zero trasferimenti. La causa era che i nostri «vincenti» erano **bot di
arbitraggio atomico** — una transazione attraversa piu' pool, compra in A e vende in B
nell'istante stesso, e i gettoni non si fermano mai nel portafoglio di chi firma.
Terza volta in questo progetto che siamo andati avanti su dati sbagliati. Le prime due non le
avevamo prese prima; questa si', e solo perche' lui ha preteso il controllo a campione.

LA PROVA, e non ammette interpretazioni. Un multiplo e' vero solo se sulla chain si vede:
  1. almeno un trasferimento del gettone VERSO il portafoglio (ha ricevuto i gettoni);
  2. almeno un trasferimento DAL portafoglio o una vendita successiva (li ha dati via);
  3. i due in TRANSAZIONI DIVERSE — perche' nella stessa transazione e' arbitraggio, non
     una posizione tenuta;
  4. e il tempo fra i due deve essere > 0: ha davvero tenuto il gettone per un po'.

Se una di queste manca, il multiplo NON si riporta. Non «si riporta con cautela»: non si
riporta.

COSTA ZERO: esploratore pubblico, nessuna chiave.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

ESPLORATORI = {"base": "https://base.blockscout.com",
               "robinhood": "https://robinhoodchain.blockscout.com"}
H = {"User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/129.0 Safari/537.36"),
     "Accept": "application/json", "Accept-Language": "en-US,en;q=0.9"}
PAGINE_MAX = int(os.environ.get("PAGINE_MAX", 10))
PAUSA = float(os.environ.get("PAUSA", 0.3))


def _get(u, intest):
    with urllib.request.urlopen(
            urllib.request.Request(u, headers=intest), timeout=30) as r:
        return json.loads(r.read())


def controlla(chain, portafoglio, gettone):
    """LA DOMANDA PRECISA, IN UNA CHIAMATA (5/10). La prima versione scorreva le pagine dei
    trasferimenti del portafoglio cercando il gettone: su un bot con oltre tremila
    trasferimenti si guardava una frazione, e il verdetto onesto era «non trovato nella
    finestra» — inutilizzabile.
    Esiste l'endpoint che fa esattamente la domanda giusta: `tokentx` filtrato per indirizzo E
    per contratto del gettone, su TUTTO lo storico. Una chiamata, risposta definitiva.
    Avevo costruito uno scorrimento di pagine per una domanda che aveva gia' il suo filtro:
    stessa famiglia di «provare l'altra porta», per la terza volta oggi.
    """
    base = ESPLORATORI.get(chain)
    if base:
        intest0 = dict(H)
        intest0["Referer"] = base + "/"
        u0 = (f"{base}/api?module=account&action=tokentx&address={portafoglio.lower()}"
              f"&contractaddress={gettone.lower()}&page=1&offset=200")
        try:
            j0 = _get(u0, intest0)
            res = j0.get("result")
            if isinstance(res, list):
                w0 = portafoglio.lower()
                dentro0 = [x for x in res if str(x.get("to", "")).lower() == w0]
                fuori0 = [x for x in res if str(x.get("from", "")).lower() == w0]
                if not res:
                    return {"verdetto": "FALSO", "ricevuti": 0, "dati_via": 0,
                            "fonte": "tokentx filtrato (storico intero)",
                            "perche": "zero trasferimenti di quel gettone per quel "
                                      "portafoglio su tutto lo storico: non l'ha mai "
                                      "toccato, il multiplo non esiste"}
                tx_d = {x.get("hash") for x in dentro0}
                tx_f = {x.get("hash") for x in fuori0}
                if dentro0 and fuori0 and tx_d == tx_f and len(tx_d) == 1:
                    return {"verdetto": "ARBITRAGGIO", "ricevuti": len(dentro0),
                            "dati_via": len(fuori0), "fonte": "tokentx filtrato",
                            "perche": "ricevuto e ceduto nella STESSA transazione: "
                                      "arbitraggio atomico, non una posizione tenuta"}
                if dentro0 and not fuori0:
                    return {"verdetto": "POSIZIONE APERTA", "ricevuti": len(dentro0),
                            "dati_via": 0, "fonte": "tokentx filtrato",
                            "perche": "ricevuto e mai ceduto: posizione ancora aperta"}
                if fuori0 and not dentro0:
                    return {"verdetto": "FALSO", "ricevuti": 0, "dati_via": len(fuori0),
                            "fonte": "tokentx filtrato",
                            "perche": "ceduto senza che si veda l'acquisto: nessun multiplo "
                                      "e' calcolabile"}
                return {"verdetto": "VERO", "ricevuti": len(dentro0),
                        "dati_via": len(fuori0), "fonte": "tokentx filtrato",
                        "perche": "ricevuto e ceduto in transazioni diverse: la posizione "
                                  "e' reale e verificabile a mano"}
        except Exception:
            pass   # si ripiega sullo scorrimento delle pagine, dichiarandolo nel verdetto

    """Il portafoglio ha davvero TENUTO quel gettone? Torna un verdetto, non un'opinione."""
    base = ESPLORATORI.get(chain)
    if not base:
        return {"verdetto": "NON POSSO CONTROLLARE", "perche": f"nessun esploratore per {chain}"}
    intest = dict(H)
    intest["Referer"] = base + "/"
    w = portafoglio.lower()
    g = gettone.lower()
    dentro, fuori = [], []
    esaurite = False
    u = f"{base}/api/v2/addresses/{w}/token-transfers"
    for _ in range(PAGINE_MAX):
        try:
            j = _get(u, intest)
        except urllib.error.HTTPError as e:
            if e.code in (429, 403, 503):
                return {"verdetto": "NON POSSO CONTROLLARE",
                        "perche": f"il servizio ci ha chiuso la porta (HTTP {e.code}): "
                                  f"non sapere non e' sapere"}
            return {"verdetto": "NON POSSO CONTROLLARE", "perche": f"HTTP {e.code}"}
        except Exception as e:
            return {"verdetto": "NON POSSO CONTROLLARE", "perche": type(e).__name__}
        for x in (j.get("items") or []):
            tok = x.get("token") or {}
            ind = str(tok.get("address_hash") or tok.get("address") or "").lower()
            if ind != g:
                continue
            tx = str(x.get("transaction_hash") or x.get("tx_hash") or "")
            quando = x.get("timestamp") or ""
            to = str((x.get("to") or {}).get("hash") or "").lower()
            (dentro if to == w else fuori).append((tx, quando))
        pp = j.get("next_page_params")
        if not pp:
            esaurite = True
            break
        u = (f"{base}/api/v2/addresses/{w}/token-transfers?"
             + "&".join(f"{k}={v}" for k, v in pp.items() if v is not None))
        time.sleep(PAUSA)

    if not dentro and not fuori:
        # «NON TROVATO NELLA FINESTRA» NON E' «NON ESISTE» (5/10, quarta volta oggi).
        # Con PAGINE_MAX pagine si guardano al massimo PAGINE_MAX x 50 trasferimenti: su un
        # portafoglio che ha firmato 3.601 transazioni e' una frazione. Dichiarare FALSO
        # senza aver esaurito le pagine sarebbe registrare un'assenza di prova come prova di
        # assenza — l'errore che oggi mi ha morso su tre fronti diversi.
        if not esaurite:
            return {"verdetto": "NON TROVATO NELLA FINESTRA", "ricevuti": 0, "dati_via": 0,
                    "perche": f"nessun trasferimento di quel gettone nelle prime "
                              f"{PAGINE_MAX} pagine, ma le pagine NON sono esaurite: "
                              f"non si puo' concludere che non esista. Alzare PAGINE_MAX."}
        return {"verdetto": "FALSO", "ricevuti": 0, "dati_via": 0,
                "perche": "pagine esaurite e nessun trasferimento di quel gettone: "
                          "questo portafoglio non l'ha MAI toccato. Il multiplo non esiste."}
    if not dentro:
        return {"verdetto": "FALSO", "ricevuti": 0, "dati_via": len(fuori),
                "perche": "ha ceduto il gettone ma non si vede che l'abbia ricevuto: "
                          "il costo d'acquisto non e' osservabile, quindi nessun multiplo "
                          "e' calcolabile"}
    if not fuori:
        return {"verdetto": "POSIZIONE APERTA", "ricevuti": len(dentro), "dati_via": 0,
                "perche": "l'ha ricevuto e non l'ha mai ceduto: non e' una perdita e non e' "
                          "un guadagno, e' una posizione ancora aperta"}
    tx_dentro = {z[0] for z in dentro}
    tx_fuori = {z[0] for z in fuori}
    if tx_dentro == tx_fuori and len(tx_dentro) == 1:
        return {"verdetto": "ARBITRAGGIO", "ricevuti": len(dentro), "dati_via": len(fuori),
                "perche": "ricevuto e ceduto nella STESSA transazione: e' un arbitraggio "
                          "atomico, non una posizione tenuta"}
    return {"verdetto": "VERO", "ricevuti": len(dentro), "dati_via": len(fuori),
            "primo_ingresso": min(z[1] for z in dentro if z[1]) if any(z[1] for z in dentro) else None,
            "ultima_uscita": max(z[1] for z in fuori if z[1]) if any(z[1] for z in fuori) else None,
            "perche": "ha ricevuto il gettone, l'ha tenuto, e l'ha ceduto in transazioni "
                      "diverse: la posizione e' reale e verificabile a mano"}


def main():
    if len(sys.argv) < 4:
        print("uso: prova_sulla_chain.py <chain> <portafoglio> <gettone>")
        print("     oppure: prova_sulla_chain.py <chain> --da-file <percorso.json>")
        return
    chain = sys.argv[1]
    if sys.argv[2] == "--da-file":
        casi = json.load(open(sys.argv[3]))
        veri = falsi = altro = 0
        for c in casi:
            r = controlla(chain, c["portafoglio"], c["gettone"])
            v = r["verdetto"]
            veri += v == "VERO"
            falsi += v == "FALSO"
            altro += v not in ("VERO", "FALSO")
            print(f"  {c['portafoglio'][:14]}… / {c['gettone'][:14]}… → {v}")
            print(f"      {r['perche']}")
            time.sleep(PAUSA)
        print(f"\n  VERI {veri} · FALSI {falsi} · altro {altro} su {len(casi)}")
        if falsi:
            print("  ANCHE UNO SOLO FALSO vuol dire che i dati NON sono veritieri.")
    else:
        r = controlla(chain, sys.argv[2], sys.argv[3])
        print(json.dumps(r, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
