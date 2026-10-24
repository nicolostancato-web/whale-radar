"""Chi ha lanciato ogni moneta: l'UNICO attributo noto PRIMA di comprare.

PERCHE' ESISTE (19/10). La convergenza dei capofila e' reale ma vive dentro il secondo
successivo al segnale, e noi quel secondo non lo possediamo (vedi
LA_CONVERGENZA_NON_E_RAGGIUNGIBILE_19OTT.md). Restano solo i filtri leggibili ALLA NASCITA,
dove la latenza non toglie nulla: la tassa del creatore (gia' in tassa_zero.jsonl) e
l'identita' del creatore, che sta nel topic[3] di TokenLaunched e non l'avevamo mai estratta
per l'intero insieme.

COSTO: zero. RPC pubblico, con filtro di indirizzo sulla fabbrica (fino a 10M blocchi per
chiamata, misurato il 6/10).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as C

FUORI = "data/multichain/robinhood/creatori.json"
PASSO = 9_000_000

def main():
    testa = int(C.chiama("eth_blockNumber"), 16)
    out = {}
    b = 0
    while b <= testa:
        fine = min(b + PASSO - 1, testa)
        lg = C.log_di_finestra(C.T_LANCIO, b, fine, indirizzo=C.FABBRICA)
        if lg is None:
            raise SystemExit(f"CREATORI | l'RPC ha rifiutato {b}-{fine}: non invento nulla")
        for l in lg:
            t = l["topics"]
            # 19/10: il PRIMO campo del dato e' la moneta di conto della curva. Zero = nativa.
            # Serve perche' solo 6 lanci su 400 presi a caso sono nativi: misurare in 1e18 tutto
            # il registro gonfiava il volume di un creatore fino a 278 milioni di euro su 10
            # acquisti. La nativita' ora si legge gratis dall'evento, per tutti i lanci.
            d0 = l["data"][2:66]
            out["0x" + t[2][-40:]] = {          # topic[2] = curva (chiave di tutto il resto)
                "gettone": "0x" + t[1][-40:],
                "creatore": "0x" + t[3][-40:],
                "nascita": int(l["blockNumber"], 16),
                "nativa": int(d0, 16) == 0 if d0 else None,
            }
        print(f"CREATORI | {b}-{fine}: {len(lg)} lanci, totale {len(out)}", flush=True)
        b = fine + 1
    json.dump(out, open(FUORI, "w"))
    print(f"CREATORI | scritte {len(out)} curve in {FUORI}")

if __name__ == "__main__":
    main()
