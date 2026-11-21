"""I GETTONI RICEVUTI INVECE CHE COMPRATI: quanto vale quel canale, su Base.

L'ultima strada della lista: non comprare, ma farsi dare i gettoni (pre-sale, airdrop,
distribuzioni) e venderli. Si misura senza ipotesi: per ogni gettone attivo si guarda chi
VENDE al pool, e si controlla se quell'indirizzo aveva mai COMPRATO dal pool prima.

  - ha comprato prima  -> e' un trader, gia' misurato altrove
  - non ha mai comprato -> quei gettoni gli sono arrivati da fuori: e' il canale «regalati»

Due numeri interessano: quanto pesa quel canale (quota delle vendite) e quanto incassa.
E una terza cosa, che e' quella che decide: i nostri indirizzi potrebbero riceverli?
"""
import collections, json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base_rpc as B

SW = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
INIT = "0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
TRASF = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


def _sg(x):
    v = int(x, 16)
    return v - (1 << 256) if v >= (1 << 255) else v


def main():
    t = B.testa()
    da = t - B.profondita(t)
    attivi = json.load(open("data/multichain/base/pool_attivi.json"))["pool_attivi"][:10]
    print(f"REGALATI | {len(attivi)} pool attivi, finestra {t-da:,} blocchi", flush=True)
    # IL GETTONE SI TROVA DALLA RICEVUTA, NON DAL LANCIO (21/10). Cercare l'Initialize
    # funziona solo dentro le ~5 ore che il nodo serve, e i pool attivi sono quasi tutti piu'
    # vecchi: su dieci ne trovavo uno. Invece: si prende UNA transazione di scambio di quel
    # pool e nella sua ricevuta si cerca il trasferimento che ha il gestore come controparte.
    # Una chiamata per pool, e funziona a qualunque eta'.
    tok_di = {}
    for idp in attivi:
        lg = None
        b = t - 2000
        limite = t - B.profondita(t)
        while b > limite and not lg:
            lg = B.log_di_finestra(SW, b, min(b + 1999, t), indirizzo=B.GESTORE_V4, secondo=idp)
            b -= 2000
        if not lg:
            continue
        r = B.chiama("eth_getTransactionReceipt", [lg[0]["transactionHash"]])
        for x in (r or {}).get("logs", []):
            tp = x.get("topics") or []
            if len(tp) >= 3 and tp[0] == TRASF:
                mitt, dest = "0x" + tp[1][-40:], "0x" + tp[2][-40:]
                if B.GESTORE_V4 in (mitt, dest):
                    tok_di[idp] = x["address"].lower()
                    break
        time.sleep(0.2)
    print(f"REGALATI | gettoni identificati: {len(tok_di)}", flush=True)
    tot_v = reg_v = 0
    quote = []
    for idp, tok in tok_di.items():
        comprato, venduto, ricevuto = set(), collections.Counter(), collections.Counter()
        b = da
        while b <= t:
            f = min(b + B.FINESTRA - 1, t)
            for l in B.log_di_finestra(TRASF, b, f, indirizzo=tok) or []:
                if len(l.get("topics", [])) < 3:
                    continue
                mitt, dest = "0x" + l["topics"][1][-40:], "0x" + l["topics"][2][-40:]
                try:
                    g = int(l["data"], 16) / 1e18
                except Exception:
                    continue
                if mitt == B.GESTORE_V4:
                    comprato.add(dest)
                elif dest == B.GESTORE_V4:
                    venduto[mitt] += g
                else:
                    ricevuto[dest] += g
            b = f + 1
            time.sleep(0.1)
        if not venduto:
            continue
        tv = sum(venduto.values())
        rv = sum(g for w, g in venduto.items() if w not in comprato)
        tot_v += tv
        reg_v += rv
        quote.append(rv / tv if tv else 0)
        print(f"   {idp[:12]}: venditori {len(venduto):,}, di cui MAI compratori "
              f"{sum(1 for w in venduto if w not in comprato):,}  "
              f"| quota dei gettoni venduti senza averli comprati: {rv/tv*100:.0f}%", flush=True)
    if quote:
        print(f"\nREGALATI | quota mediana dei gettoni venduti da chi non li ha mai comprati: "
              f"{statistics.median(quote)*100:.0f}%")
        print(f"REGALATI | sul totale dei pool guardati: {reg_v/max(1e-9,tot_v)*100:.0f}%")
        print("\n   NB: questo dice quanto PESA il canale, non che sia accessibile a noi.")
        print("   Riceverli richiede di essere stati idonei: attivita' passata o capitale a rischio.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
