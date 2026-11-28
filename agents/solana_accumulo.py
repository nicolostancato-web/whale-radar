"""IL RACCOGLITORE DI SOLANA: scambi, con dentro CHI li ha fatti.

== PERCHE' SOLANA E' IL TERRENO GIUSTO PER LA DOMANDA SUI PORTAFOGLI ==

Sugli EVM sapere CHI ha comprato costa il doppio del lavoro: il mittente dello scambio e' il
router, l'identita' va ricostruita incrociando i trasferimenti, e su Base quel pezzo e'
proprio il muro contro cui ci siamo fermati. Su Solana chi ha firmato e' nel dato, insieme al
prezzo: identita' e prezzo arrivano nella stessa lettura.

== L'UNIVERSO SI RICONOSCE DALL'INDIRIZZO (verificato il 22/10) ==

I gettoni nati su pump.fun hanno l'indirizzo che finisce per «pump»: su 10 gettoni visti in
scambi veri, 8 finivano cosi' e gli altri due erano USDC e un gettone esterno. Niente
decodifica di istruzioni, niente lettura della fabbrica: tre caratteri.

== COSA SI SALVA, E PERCHE' ==

Per ogni scambio: slot, prezzo, verso, CHI, gettone. Da qui si ricavano sia le serie di prezzo
(per la taratura e le rese) sia il registro dei portafogli, senza una seconda raccolta.

COSTO: ~1 credito Helius per transazione. Il programma stampa il consumo reale a ogni giro.
"""
import collections, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import solana_rpc as S

PUMP = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
FUORI = "data/multichain/solana/scambi.jsonl"
VISTE = "data/multichain/solana/firme_viste.json"
QUANTE = int(os.environ.get("QUANTE", "400"))


def main():
    if not S.url():
        print("ACCUMULO SOL | nessuna chiave Helius valida")
        return 1
    viste = set(json.load(open(VISTE))) if os.path.exists(VISTE) else set()
    r = S.rpc("getSignaturesForAddress", [PUMP, {"limit": 1000}]) or []
    ok = [x for x in r if not x.get("err") and x["signature"] not in viste]
    print(f"ACCUMULO SOL | {len(r)} firme, {sum(1 for x in r if not x.get('err'))} riuscite, "
          f"{len(ok)} nuove", flush=True)
    nuovi = pump = costo = 0
    os.makedirs("data/multichain/solana", exist_ok=True)
    with open(FUORI, "a") as fh:
        for x in ok[:QUANTE]:
            e = S.scambio(x["signature"])
            costo += 1
            viste.add(x["signature"])
            if not e:
                continue
            slot, prezzo, compra, chi, gettone = e
            # solo i gettoni di pump.fun: gli altri sono USDC e simili, rumore
            if not gettone.endswith("pump"):
                continue
            fh.write(json.dumps({"slot": slot, "p": prezzo, "c": compra,
                                 "chi": chi, "g": gettone}) + "\n")
            nuovi += 1
            pump += 1
            if nuovi % 100 == 0:
                fh.flush()
            time.sleep(0.02)
    json.dump(sorted(viste)[-200000:], open(VISTE, "w"))
    tot = sum(1 for _ in open(FUORI)) if os.path.exists(FUORI) else 0
    print(f"ACCUMULO SOL | salvati {nuovi} scambi nuovi su gettoni pump.fun "
          f"| in archivio {tot:,} | costo ~{costo:,} crediti")
    return 0


if __name__ == "__main__":
    sys.exit(main())
