#!/usr/bin/env python3
"""UNA CADUTA PER DERIVA NON E' UNA CADUTA PER ORACOLO.

Errore mio del 7/11 mattina, e di conseguenza una strategia costruita su una
classificazione che non distingueva due cose diversissime.

Avevo misurato, per ognuna delle liquidazioni perse, la salute al blocco
PRECEDENTE, trovata sopra 1 in 10 casi su 12, e concluso: «cadono dentro il
blocco insieme all'aggiornamento Chainlink, quindi il polling non puo'
vincere e non esiste una corsia lenta».
La misura era giusta. La CONCLUSIONE no, perche' quella misura non distingue:

  - ORACOLO: la salute sta tranquilla sopra 1 e crolla di colpo quando entra
    un prezzo nuovo. Imprevedibile. Si vince solo decodificando la
    transazione d'oracolo in attesa, in 80-250 ms.
  - DERIVA: la salute scende DA SOLA, per gli interessi che maturano, di una
    quantita' quasi costante a ogni blocco. Attraversa l'1 in un blocco che
    si puo' CALCOLARE con ore di anticipo. Nessuna gara.

Entrambe mostrano «salute sopra 1 al blocco prima». Una e' una gara di
millisecondi, l'altra e' un appuntamento.

La quattordicesima (blocco 26362964, premio 141,12 $, garanzia e debito
nello stesso gettone quindi senza nemmeno vendere) era del secondo tipo: la
salute scendeva di 3,5 miliardi per blocco, lineare su 300 blocchi, e al
blocco prima stava 1,2 miliardi sopra l'uno. Attraversava con CERTEZZA nel
blocco dopo, e noi stavamo aspettando di VEDERLA scendere.

Come si distinguono, qui: si leggono le salute a -30, -10, -3, -1 e si
guarda se la discesa e' lineare. Se l'estrapolazione lineare da -10 a -1
prevede l'attraversamento entro pochi blocchi, e' DERIVA. Se la salute era
stabile e poi e' caduta di colpo, e' ORACOLO.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registri as R

D = "data/liquidazioni"
POOL = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
UNO = 10 ** 18
FONTI = [u for u in R.FONTI if "publicnode" not in u]   # servono l'archivio


def salute(utente, blocco):
    for u in FONTI:
        try:
            v = R._chiedi(u, "eth_call",
                          [{"to": POOL,
                            "data": "0xbf92857c" + utente[2:].zfill(64)},
                           hex(blocco)])
            if isinstance(v, str) and len(v) >= 2 + 64 * 6:
                return int(v[2:][320:384], 16)
        except Exception:
            pass
    return None


def classifica(utente, blocco):
    """-> (tipo, dettaglio). tipo in DERIVA / ORACOLO / NON LO SO."""
    letture = {}
    for d in (-60, -30, -10, -3, -1):
        letture[d] = salute(utente, blocco + d)
    if letture[-1] is None or letture[-10] is None:
        return "NON LO SO", "salute storiche non leggibili"
    s1, s10 = letture[-1], letture[-10]
    sopra = s1 - UNO
    if sopra <= 0:
        return "GIA' SOTTO", f"al blocco prima era gia' {s1/1e18:.9f}"
    passo = (s10 - s1) / 9.0            # quanto scende per blocco
    if passo <= 0:
        return "ORACOLO", ("la salute NON stava scendendo da sola "
                           f"(da {s10/1e18:.9f} a {s1/1e18:.9f})")
    blocchi = sopra / passo
    # la deriva e' credibile solo se e' anche LINEARE piu' indietro
    lineare = None
    if letture[-30] is not None:
        passo30 = (letture[-30] - s1) / 29.0
        lineare = passo30 > 0 and abs(passo30 - passo) / passo < 0.25
    if blocchi <= 3 and lineare:
        return "DERIVA", (f"scendeva di {passo:.3g} per blocco, lineare; "
                          f"era a {sopra:.3g} sopra l'uno = "
                          f"{blocchi:.1f} blocchi dall'attraversamento")
    if lineare:
        return "ORACOLO", (f"scendeva da sola di {passo:.3g}/blocco ma "
                           f"servivano {blocchi:.0f} blocchi: l'ha fatta "
                           f"cadere il prezzo")
    return "ORACOLO", (f"discesa non lineare: l'ha fatta cadere il prezzo "
                       f"(a -1 era {s1/1e18:.9f})")


def main():
    seg = json.load(open(f"{D}/conta_segnalibro.json"))
    f = max(seg["fonti"].items(), key=lambda x: x[1]["fino_a"])
    arc = json.load(open(f"{D}/liquidazioni_viste.json"))
    from keccak import keccak256
    FIRMA = "0x" + keccak256(
        b"LiquidationCall(address,address,address,uint256,uint256,"
        b"address,bool)").hex()
    ric = {}
    try:
        ric = json.load(open(f"{D}/ricevute.json"))
    except Exception:
        pass
    righe = []
    visti = set()
    for h in f[1]["hash"]:
        tx, idx = h.split(":")
        r = ric.get(tx)
        if not r:
            for u in R.FONTI:
                try:
                    r = R._chiedi(u, "eth_getTransactionReceipt", [tx])
                    break
                except Exception:
                    pass
        if not r:
            continue
        for lg in r.get("logs", []):
            if (lg["address"].lower() != POOL.lower()
                    or lg["topics"][0].lower() != FIRMA.lower()):
                continue
            if int(lg["logIndex"], 16) != int(idx, 16):
                continue
            u = ("0x" + lg["topics"][3][-40:]).lower()
            b = int(r["blockNumber"], 16)
            if (u, b) in visti:
                continue
            visti.add((u, b))
            tipo, det = classifica(u, b)
            righe.append({"tx": tx, "blocco": b, "utente": u,
                          "premio_usd": (arc.get(tx) or {}).get(
                              "premio_vero_usd"),
                          "tipo": tipo, "dettaglio": det})
    righe.sort(key=lambda x: -(x["premio_usd"] or 0))
    print("  premio      blocco    tipo         perche'")
    for x in righe:
        print("  $%9s  %8d  %-11s %s" % (
            f"{x['premio_usd']:,.2f}" if x["premio_usd"] is not None else "?",
            x["blocco"], x["tipo"], x["dettaglio"][:78]))
    da_deriva = [x for x in righe if x["tipo"] in ("DERIVA", "GIA' SOTTO")]
    print(f"\n  CORSIA LENTA (deriva o gia' sotto): {len(da_deriva)} su "
          f"{len(righe)}, premio "
          f"${sum(x['premio_usd'] or 0 for x in da_deriva):,.2f}")
    da_gara = [x for x in righe if x["tipo"] == "ORACOLO"]
    print(f"  GARA (oracolo): {len(da_gara)} su {len(righe)}, premio "
          f"${sum(x['premio_usd'] or 0 for x in da_gara):,.2f}")
    t = f"{D}/deriva_o_oracolo.json.tmp"
    json.dump({"righe": righe}, open(t, "w"), indent=1)
    os.replace(t, f"{D}/deriva_o_oracolo.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
