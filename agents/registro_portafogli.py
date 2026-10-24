"""CHI ha fatto ogni operazione sui pool diplomati: il registro, non le somme.

== COME SI RICONOSCE LA PERSONA (19/10, disegno di Astra e Grok) ==

Lo Swap dice QUANTO e A CHE PREZZO, ma il suo campo `sender` e' il ROUTER, non la persona
(misurato: 72 indirizzi per 1.441 scambi, i primi cinque al 67%). L'identita' sta nel
trasferimento del gettone: su Uniswap v4 i gettoni passano dal gestore unico, quindi
  - trasferimento DAL gestore  -> quell'indirizzo ha COMPRATO
  - trasferimento VERSO il gestore -> quell'indirizzo ha VENDUTO
  - tutto il resto -> NON e' uno scambio: e' inventario che si sposta, e va tenuto a parte
    perche' altrimenti una vendita di gettoni regalati sembra bravura.

I due flussi si uniscono per HASH DI TRANSAZIONE, mai per blocco o per importo simile.
Quando in una transazione c'e' piu' di uno Swap di quel pool l'abbinamento non e' unico: la
riga resta, ma marcata «incerto», e non entrera' in nessun profitto. Non si impone una
classificazione a un caso ambiguo.

== COSA SI SALVA PER OGNI RIGA ==

blocco, posizione nel blocco, hash, chi, verso, gettoni, nativi, prezzo del pool DOPO
l'operazione (sqrtPriceX96), confidenza. Il prezzo dopo e' il campo che rende calcolabile la
copia: senza, si costruisce una classifica che non si puo' tradurre in un ordine.

Costo: zero. Due chiamate per moneta sull'RPC pubblico.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as C

GESTORE_V4 = "0x8366a39cc670b4001a1121b8f6a443a643e40951"
T_TRASF = C.firma("Transfer(address,address,uint256)")
T_SWAP = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
DENTRO = "data/multichain/robinhood/manifesto_graduati.json"
FUORI = "data/multichain/robinhood/registro_portafogli.jsonl"
FATTE = "data/multichain/robinhood/registro_portafogli_fatte.json"
FINESTRA = int(os.environ.get("FINESTRA", "400000"))     # stesso taglio dichiarato degli scambi
FETTA = int(os.environ.get("FETTA", "0"))
FETTE = int(os.environ.get("FETTE", "1"))


def _segno(v):
    return v - (1 << 256) if v >= (1 << 255) else v


def righe(moneta, idp, diploma):
    sw = C.log_di_finestra(T_SWAP, diploma, diploma + FINESTRA, indirizzo=GESTORE_V4, secondo=idp)
    if sw is None:
        return None
    per_tx = {}
    for l in sw:
        d = l["data"][2:]
        if len(d) < 192:
            continue
        per_tx.setdefault(l["transactionHash"], []).append(
            (_segno(int(d[0:64], 16)) / 1e18, _segno(int(d[64:128], 16)) / 1e18, int(d[128:192], 16)))
    tr = C.log_di_finestra(T_TRASF, diploma, diploma + FINESTRA, indirizzo=moneta)
    if tr is None:
        return None
    out = []
    for l in tr:
        if len(l.get("topics", [])) < 3:
            continue
        mitt = "0x" + l["topics"][1][-40:]
        dest = "0x" + l["topics"][2][-40:]
        g = int(l["data"], 16) / 1e18
        h = l["transactionHash"]
        if dest == GESTORE_V4:
            verso, chi = "v", mitt
        elif mitt == GESTORE_V4:
            verso, chi = "c", dest
        else:
            verso, chi = "x", dest          # x = non e' uno scambio: inventario che si muove
        s = per_tx.get(h, [])
        nat = sq = None
        conf = "i"                           # i = incerto
        if verso != "x" and len(s) == 1:
            nat, sq, conf = abs(s[0][0]), s[0][2], "c"
        out.append([int(l["blockNumber"], 16), int(l["logIndex"], 16), h, chi, verso,
                    round(g, 6), nat, sq, conf])
    out.sort(key=lambda r: (r[0], r[1]))
    return out


def main():
    man = json.load(open(DENTRO))["pool"]
    nativi = {k: v for k, v in man.items() if int(v["valuta"], 16) == 0}
    nativi = {k: v for i, (k, v) in enumerate(nativi.items()) if i % FETTE == FETTA}
    mia = FUORI.replace(".jsonl", f"_{FETTA}.jsonl")
    miaf = FATTE.replace(".json", f"_{FETTA}.json")
    fatte = json.load(open(miaf)) if os.path.exists(miaf) else {}
    f = open(mia, "a")
    n = rifiutati = 0
    t0 = time.time()
    for idp, v in nativi.items():
        if idp in fatte:
            continue
        r = righe(v["moneta"], idp, v["diploma"])
        if r is None:
            rifiutati += 1
            continue
        f.write(json.dumps({"pool": idp, "moneta": v["moneta"], "diploma": v["diploma"], "r": r}) + "\n")
        fatte[idp] = len(r)
        n += 1
        if n % 25 == 0:
            f.flush()
            json.dump(fatte, open(miaf, "w"))
            print(f"PORTAFOGLI | {len(fatte)}/{len(nativi)} monete, {sum(fatte.values()):,} righe, "
                  f"{n/max(1e-9,time.time()-t0)*60:.0f}/min, rifiutati {rifiutati}", flush=True)
        time.sleep(0.2)
    f.close()
    json.dump(fatte, open(miaf, "w"))
    print(f"PORTAFOGLI | finito: {len(fatte)}/{len(nativi)}, {sum(fatte.values()):,} righe, {rifiutati} rifiutati")
    return 0


if __name__ == "__main__":
    sys.exit(main())
