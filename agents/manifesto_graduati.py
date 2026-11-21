"""IL MANIFESTO DI COPERTURA: quante monete si sono davvero diplomate, e quali abbiamo.

PERCHE' ESISTE (19/10, indicazione di Astra). Avevamo tre numeri diversi per la stessa cosa —
847 pool con l'hook di Pons nel censimento, 1.983 monete nella tabella dei portafogli, 12.738
«pool graduati totali» — e nessuno sapeva quale fosse l'universo. Studiare i rendimenti prima
di sapere chi c'e' dentro significa misurare un campione scelto da come abbiamo raccolto.

Qui l'universo si legge DALLA CHAIN, non dai nostri file: ogni diploma e' un evento Initialize
del gestore v4 con l'hook di Pons. Costo zero (RPC pubblico, filtro sull'indirizzo del gestore).
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as C

GESTORE_V4 = "0x8366a39cc670b4001a1121b8f6a443a643e40951"
HOOK_PONS = "0xe5e702641ea86f4ae6cc3cdaed2b886f976be044"
T_INIT = C.firma("Initialize(bytes32,address,address,uint24,int24,address,uint160,int24)")
FUORI = "data/multichain/robinhood/manifesto_graduati.json"
PASSO = 9_000_000


def main():
    # 19/10: anche la testa va chiesta con pazienza. L'RPC pubblico da 429 quando lo si
    # incalza, e morire sulla prima chiamata butta via il giro intero.
    bn = None
    for attesa in (0, 15, 45, 90, 180):
        if attesa:
            time.sleep(attesa)
        bn = C.chiama("eth_blockNumber")
        if bn:
            break
    if not bn:
        print("MANIFESTO | l'RPC non da la testa: non invento un blocco")
        return 1
    testa = int(bn, 16)
    out, altri = {}, 0
    b = 0
    while b <= testa:
        fine = min(b + PASSO - 1, testa)
        # 19/10: una finestra rifiutata per 429 non e' un guasto, e' fretta. Si riprova con
        # pause crescenti; solo dopo si dichiara il fallimento, perche' un universo incompleto
        # dichiarato completo e' l'errore che questo file esiste per evitare.
        lg = None
        for attesa in (0, 20, 60, 120, 300):
            if attesa:
                time.sleep(attesa)
            lg = C.log_di_finestra(T_INIT, b, fine, indirizzo=GESTORE_V4)
            if lg is not None:
                break
            print(f"MANIFESTO | {b}-{fine} rifiutata, riprovo fra {attesa or 20}s", flush=True)
        if lg is None:
            print(f"MANIFESTO | l'RPC ha rifiutato {b}-{fine} cinque volte: non invento nulla")
            return 1
        for l in lg:
            # IL TRACCIATO SI LEGGE, NON SI ASSUME (19/10). Avevo scritto che le due monete
            # stavano nel dato e l'hook nella parola 5: in Uniswap v4 id, currency0 e currency1
            # sono INDICIZZATI, quindi il dato e' (fee, tickSpacing, hooks, sqrtPriceX96, tick)
            # e l'hook e' la parola 2. Con la parola 5 ogni log veniva scartato e il manifesto
            # dichiarava ZERO diplomi senza un solo errore. Verificato su un evento vero.
            d = l["data"][2:]
            p = [d[i:i + 64] for i in range(0, len(d), 64)]
            if len(p) < 3 or len(l.get("topics", [])) < 4:
                continue
            hook = "0x" + p[2][-40:]
            if hook.lower() != HOOK_PONS:
                altri += 1
                continue
            idp = l["topics"][1]
            c0, c1 = "0x" + l["topics"][2][-40:], "0x" + l["topics"][3][-40:]
            out[idp] = {"moneta": c1 if int(c0, 16) == 0 else c0,
                        "valuta": c0 if int(c0, 16) == 0 else c1,
                        "diploma": int(l["blockNumber"], 16),
                        "tx": l["transactionHash"]}
        print(f"MANIFESTO | {b}-{fine}: {len(lg)} pool aperti, con hook Pons finora {len(out):,}", flush=True)
        time.sleep(20)
        b = fine + 1
    json.dump({"acq": int(time.time()), "testa": testa, "altri_hook": altri, "pool": out},
              open(FUORI, "w"))
    nat = sum(1 for v in out.values() if int(v["valuta"], 16) == 0)
    print(f"\nMANIFESTO | diplomi di Pons: {len(out):,}  (altri pool v4 aperti: {altri:,})")
    print(f"MANIFESTO | di cui quotati in nativo: {nat:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
