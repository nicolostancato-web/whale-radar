"""RACCOLTA PER GETTONE, non per rivolo di firme.

PERCHE' IL PRIMO DISEGNO ERA SBAGLIATO (22/10). Leggevo il flusso di firme del programma
pump.fun e salvavo gli scambi che capitavano: 400 crediti per 120 righe SPARSE, di gettoni
diversi. Ma per misurare qualsiasi cosa serve la SERIE COMPLETA di un gettone — senza, non si
puo' calcolare ne' la taratura ne' una resa, perche' non si sa cosa e' successo in mezzo.

Qui si fa il contrario: si scoprono i gettoni nuovi dal flusso (poche chiamate), e poi di
ognuno si legge TUTTA la storia. Stesso costo, dati utilizzabili.

Ogni riga porta prezzo E chi l'ha fatto: serie di prezzo e registro dei portafogli nascono
dalla stessa lettura, che sugli EVM erano due lavori distinti.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import solana_rpc as S

PUMP = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
FUORI = "data/multichain/solana/gettoni.jsonl"
FATTI = "data/multichain/solana/gettoni_fatti.json"
QUANTI = int(os.environ.get("QUANTI", "6"))
PER_GETTONE = int(os.environ.get("PER_GETTONE", "400"))


def main():
    if not S.url():
        print("GETTONI SOL | nessuna chiave valida")
        return 1
    fatti = set(json.load(open(FATTI))) if os.path.exists(FATTI) else set()
    costo = 0
    # 1) scoprire gettoni nuovi: poche letture del flusso bastano
    r = S.rpc("getSignaturesForAddress", [PUMP, {"limit": 300}]) or []
    ok = [x["signature"] for x in r if not x.get("err")]
    nuovi = []
    for s in ok:
        if len(nuovi) >= QUANTI:
            break
        e = S.scambio(s)
        costo += 1
        # 22/10: lo stesso gettone si scopre da piu' firme e finiva due volte
        # nell'archivio, raddoppiando il costo e falsando i conteggi.
        if e and e[4].endswith("pump") and e[4] not in fatti and e[4] not in nuovi:
            nuovi.append(e[4])
        time.sleep(0.02)
    print(f"GETTONI SOL | scoperti {len(nuovi)} gettoni nuovi ({costo} crediti)", flush=True)
    # 2) di ognuno, TUTTA la storia
    os.makedirs("data/multichain/solana", exist_ok=True)
    with open(FUORI, "a") as fh:
        for g in nuovi:
            sig = S.rpc("getSignaturesForAddress", [g, {"limit": PER_GETTONE}]) or []
            serie = []
            for x in sig:
                if x.get("err"):
                    continue
                e = S.scambio(x["signature"])
                costo += 1
                if e and e[4] == g:
                    serie.append([e[0], e[1], e[2], e[3]])
                time.sleep(0.02)
            serie.sort()
            if len(serie) >= 20:
                fh.write(json.dumps({"g": g, "n": len(serie), "s": serie}) + "\n")
                fh.flush()
            fatti.add(g)
            print(f"   {g[:14]}: {len(serie)} scambi {'salvato' if len(serie)>=20 else '(pochi, scartato)'}",
                  flush=True)
    json.dump(sorted(fatti), open(FATTI, "w"))
    tot = sum(1 for _ in open(FUORI)) if os.path.exists(FUORI) else 0
    print(f"GETTONI SOL | gettoni in archivio {tot} | costo del giro ~{costo:,} crediti")
    return 0


if __name__ == "__main__":
    sys.exit(main())
