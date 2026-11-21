#!/usr/bin/env python3
"""QUANTE LIQUIDAZIONI FA OGNI MERCATO, non solo il nostro.

Domanda di Nicolo' il 7/11, e la risposta sul perche' non lo guardavamo e'
scomoda: non e' stata una decisione, e' stata un'omissione mia. Il progetto
e' nato su Aave v3 Core e ho continuato a ottimizzare dentro quel laghetto
senza mai misurare quanto fosse grande. Misurato oggi: 14 liquidazioni in
53 ore, cioe' SEI AL GIORNO, e le vediamo tutte. Il collo di bottiglia non
e' la nostra soglia: e' la dimensione del lago.

La meccanica e' la stessa su tutti i mercati di prestito: un oracolo pubblica
un prezzo, una posizione scende sotto la soglia, chiunque puo' chiuderla
pagando il debito e prendendo la garanzia con un bonus. Cambiano il nome
dell'evento, la firma della chiamata e i dettagli del bonus -- non il
mestiere.

Qui si CONTA soltanto, sulla stessa finestra di blocchi, perche' prima di
scrivere una riga di codice per un mercato nuovo va saputo se ne vale la
pena. Nessuna stima: eventi veri dai registri.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registri as R
from keccak import keccak256

D = "data/liquidazioni"


def firma(testo):
    return "0x" + keccak256(testo.encode()).hex()


# nome, indirizzo del mercato, firma dell'evento di liquidazione
MERCATI = [
    ("Aave v3 Core", "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
     firma("LiquidationCall(address,address,address,uint256,uint256,"
           "address,bool)")),
    ("Aave v3 Prime", "0x4e033931ad43597d96D6bcc25c280717730B58B1",
     firma("LiquidationCall(address,address,address,uint256,uint256,"
           "address,bool)")),
    ("Aave v2", "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",
     firma("LiquidationCall(address,address,address,uint256,uint256,"
           "address,bool)")),
    ("Spark", "0xC13e21B648A5Ee794902342038FF3aDAB66BE987",
     firma("LiquidationCall(address,address,address,uint256,uint256,"
           "address,bool)")),
    ("Morpho Blue", "0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb",
     firma("Liquidate(bytes32,address,address,uint256,uint256,uint256,"
           "uint256,uint256)")),
    ("Compound v2", "0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B",
     firma("LiquidateBorrow(address,address,uint256,address,uint256)")),
    ("Compound v3 USDC", "0xc3d688B66703497DAA19211EEdff47f25384cdc3",
     firma("AbsorbCollateral(address,address,address,uint256,uint256)")),
    ("Compound v3 WETH", "0xA17581A9E3356d9A858b789D68B4d866e593aE94",
     firma("AbsorbCollateral(address,address,address,uint256,uint256)")),
    ("Euler v2 EVK", None,
     firma("Liquidate(address,address,address,uint256,uint256)")),
    ("Fluid", "0x52Aa899454998Be5b000Ad077a46Bbe360F4e497",
     firma("LogLiquidate(address,uint256,uint256,int256)")),
]


def conta(indirizzo, firma_ev, da, a):
    """eventi nella finestra, UNA chiamata a publicnode (accetta la finestra
    intera) con una pausa fra i mercati per non bruciare la fonte.

    Due strade provate e scartate, e vanno scritte perche' sono un pezzo di
    sapere:
    1. a pezzi da 800 blocchi sulle fonti pubbliche: 200 richieste per dieci
       mercati, strozzato subito, dieci «NON LO SO» di fila.
    2. UNA chiamata ad Alchemy: RIFIUTATA. Il piano gratuito limita
       `eth_getLogs` a DIECI BLOCCHI per richiesta (non diecimila: dieci).
       Quindi Alchemy chiude i problemi di limite sulle letture di stato e
       sul mempool filtrato, ma NON sui registri storici. Correzione a quello
       che avevo creduto stamattina.
    """
    p = {"topics": [firma_ev], "fromBlock": hex(da), "toBlock": hex(a)}
    if indirizzo:
        p["address"] = indirizzo
    for u in ("https://ethereum-rpc.publicnode.com",
              "https://ethereum.publicnode.com"):
        for tentativo in range(3):
            try:
                r = R._chiedi(u, "eth_getLogs", [p])
                if isinstance(r, list):
                    return len(r), 0
            except Exception as e:
                if "429" in str(e) or "many" in str(e).lower():
                    time.sleep(6 * (tentativo + 1))   # non si insiste
                    continue
                return None, f"{type(e).__name__}: {str(e)[:40]}"
    return None, "nessuna risposta"


def main():
    import conta_sicuro as CS
    d = json.load(open(f"{D}/conta_sicuro.json"))
    da, a = CS.DA_BLOCCO, d["fino_al_blocco"]
    ore = (a - da) * 12 / 3600.0
    print(f"   finestra: {a-da} blocchi = {ore:.1f} ore\n")
    print("   mercato              eventi   al giorno   rispetto ad Aave v3")
    fuori = []
    base = None
    for nome, ind, fev in MERCATI:
        n, persi = conta(ind, fev, da, a)
        time.sleep(3)      # UNA PAUSA FRA I MERCATI: la fonte e' gratuita
        if n is None:
            print(f"   {nome:20s} NON LO SO ({persi})")
            fuori.append({"mercato": nome, "eventi": None})
            continue
        gg = n / ore * 24
        if nome == "Aave v3 Core":
            base = gg
        rap = (f"{gg/base:.1f}x" if base and base > 0 and nome != "Aave v3 Core"
               else ("-" if nome == "Aave v3 Core" else "?"))
        print(f"   {nome:20s} {n:6d}   {gg:8.1f}   {rap}")
        fuori.append({"mercato": nome, "indirizzo": ind, "eventi": n,
                      "al_giorno": round(gg, 1)})
    buoni = [x for x in fuori if x.get("eventi")]
    tot = sum(x["eventi"] for x in buoni)
    print(f"\n   TOTALE misurato: {tot} eventi in {ore:.0f} ore = "
          f"{tot/ore*24:.1f} al giorno")
    if base:
        print(f"   il nostro lago e' il {base/(tot/ore*24)*100:.0f}% "
              f"di quello che abbiamo misurato")
    t = f"{D}/quanto_e_grande_il_lago.json.tmp"
    json.dump({"quando": time.time(), "da": da, "a": a, "ore": ore,
               "mercati": fuori}, open(t, "w"), indent=1)
    os.replace(t, f"{D}/quanto_e_grande_il_lago.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
