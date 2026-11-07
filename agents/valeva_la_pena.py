#!/usr/bin/env python3
"""QUANTE DELLE LIQUIDAZIONI AVVENUTE ERANO OCCASIONI PER NOI?

Nata dalla tredicesima, il 7/11. Premio lordo $0,0017, gas del suo blocco
$0,0618: il vincitore ha PERSO 6 centesimi. Non l'abbiamo persa, l'abbiamo
rifiutata, e rifiutarla era giusto.

Ma il nostro contatore la chiamava «liquidazione persa» come le altre, e
questo e' un difetto grave del DENOMINATORE: se «perse» cresce mentre il
numero di occasioni vere sta fermo, la pressione spinge ad abbassare le
guardie per inseguire eventi che ci farebbero perdere soldi. Un conteggio
che mescola «non ce l'ho fatta» con «non la volevo» non misura la nostra
bravura: misura il traffico.

LE RIGHE NON SONO I CASI, E I CASI NON SONO LE OCCASIONI. Tre livelli:
   eventi di registro  ->  transazioni  ->  OCCASIONI (netto positivo)
Ognuno col suo nome, e il terzo e' quello su cui si giudica il sistema.

Il netto si calcola col gas DEL SUO BLOCCO, non col gas di oggi: una
liquidazione a 10 gwei e una a 0,04 gwei non sono confrontabili, ed e' lo
stesso errore del metro non tarato.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registri as R
from keccak import keccak256

D = "data/liquidazioni"
POOL = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
FIRMA = "0x" + keccak256(
    b"LiquidationCall(address,address,address,uint256,uint256,address,bool)"
).hex()
GAS_NOSTRO = 1_400_000      # quanto ne usiamo noi, non il vincitore
MARGINE = 1.5               # lo stesso che pretende la guardia del pescatore


def _c(m, p):
    for u in R.FONTI:
        try:
            return R._chiedi(u, m, p)
        except Exception:
            pass
    return None


def main():
    arc = json.load(open(f"{D}/liquidazioni_viste.json"))
    seg = json.load(open(f"{D}/conta_segnalibro.json"))
    f = max(seg["fonti"].items(), key=lambda x: x[1]["fino_a"])
    pe = 2236.0
    try:
        import gas_ora as GO
        _, _p, _ = GO.leggi()
        pe = _p or pe
    except Exception:
        pass

    righe, visti = [], {}
    for h in f[1]["hash"]:
        tx, idx = h.split(":")
        r = visti.get(tx) or _c("eth_getTransactionReceipt", [tx])
        visti[tx] = r
        if not r:
            continue
        blk = _c("eth_getBlockByNumber", [r["blockNumber"], False])
        if not blk:
            continue
        bf = int(blk["baseFeePerGas"], 16) / 1e9
        costo = GAS_NOSTRO * bf * 1e-9 * pe
        premio = (arc.get(tx) or {}).get("premio_vero_usd")
        if premio is None:
            continue
        righe.append({"tx": tx, "blocco": int(r["blockNumber"], 16),
                      "premio_usd": premio, "base_fee_gwei": bf,
                      "costo_nostro_usd": costo,
                      "netto_usd": premio - costo,
                      "occasione": premio > costo * MARGINE})

    occ = [x for x in righe if x["occasione"]]
    print(f"   eventi letti dal registro:  {len(f[1]['hash'])}")
    print(f"   transazioni distinte:       {len({x['tx'] for x in righe})}")
    print(f"   OCCASIONI (netto positivo con margine {MARGINE}x): "
          f"{len(occ)}")
    print()
    print("   premio      base fee   ci costava   netto      verdetto")
    for x in sorted(righe, key=lambda y: -y["premio_usd"]):
        print("   $%9.2f  %6.2f gw  $%8.2f  $%9.2f  %s" % (
            x["premio_usd"], x["base_fee_gwei"], x["costo_nostro_usd"],
            x["netto_usd"],
            "OCCASIONE" if x["occasione"] else "il gas se la mangia"))
    print()
    print(f"   premio delle sole occasioni: "
          f"${sum(x['premio_usd'] for x in occ):,.2f}")
    print(f"   premio di quelle che rifiutiamo: "
          f"${sum(x['premio_usd'] for x in righe if not x['occasione']):,.2f}")
    tmp = f"{D}/valeva_la_pena.json.tmp"
    json.dump({"eventi": len(f[1]["hash"]),
               "transazioni": len({x["tx"] for x in righe}),
               "occasioni": len(occ), "righe": righe,
               "margine": MARGINE, "gas_nostro": GAS_NOSTRO},
              open(tmp, "w"), indent=1)
    os.replace(tmp, f"{D}/valeva_la_pena.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
