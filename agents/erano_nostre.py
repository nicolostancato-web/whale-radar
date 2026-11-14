#!/usr/bin/env python3
"""ERANO NELLA NOSTRA POPOLAZIONE, LE 12 CHE ABBIAMO PERSO?

Astra e Grok, il 7/11, hanno detto la stessa cosa separatamente: lo «zero
liquidabili su ~150 misure» non e' una misura di assenza di occasioni, e'
un'affermazione del nostro filtro su se stesso. Prima di comprare velocita'
o costruire modelli di probabilita', va dimostrato che quello zero e' vero.

Questa e' la versione piu' economica e piu' decisiva della prova: per ognuna
delle liquidazioni REALMENTE avvenute, il debitore era dentro la popolazione
che sorvegliamo? Se non c'era, il problema non e' la velocita' ne' il gas ne'
la mancia: e' che non la stavamo nemmeno guardando -- e tutto il lavoro sui
178 millisecondi corre su una pista dove la gara non si teneva.

LA POPOLAZIONE E' PARTE DELLA REGOLA: un «abbiamo visto tutto» misurato
sull'elenco che ci siamo costruiti noi e' una tautologia, non una verifica.
Qui il numeratore viene dalla CATENA (i registri del pool) e il denominatore
dai NOSTRI file. Mai il contrario.
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


def _chiedi(m, p):
    for u in R.FONTI:
        try:
            return R._chiedi(u, m, p)
        except Exception:
            pass
    return None


def nostre():
    """gli indirizzi che sorvegliamo, da ogni file che li elenca"""
    dove = {}
    for nome, chiave in (("lista_corta.json", None),
                         ("composizione.json", "chiavi"),
                         ("debitori.json", None),
                         ("vendite_pronte.json", None)):
        p = f"{D}/{nome}"
        if not os.path.exists(p):
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue
        ind = set()
        if isinstance(d, dict):
            ind |= {k.lower() for k in d if isinstance(k, str)
                    and k.startswith("0x") and len(k) == 42}
            for v in d.values():
                if isinstance(v, dict):
                    for c in ("indirizzo", "utente", "debitore"):
                        if isinstance(v.get(c), str):
                            ind.add(v[c].lower())
        elif isinstance(d, list):
            for v in d:
                if isinstance(v, str) and len(v) == 42:
                    ind.add(v.lower())
                elif isinstance(v, dict):
                    for c in ("indirizzo", "utente", "debitore"):
                        if isinstance(v.get(c), str):
                            ind.add(v[c].lower())
        dove[nome] = ind
    return dove


def main():
    seg = json.load(open(f"{D}/conta_segnalibro.json"))
    fonte = max(seg["fonti"].items(), key=lambda x: x[1]["fino_a"])
    hashi = fonte[1]["hash"]
    dove = nostre()
    print("popolazione che sorvegliamo, per file:")
    for n, s in dove.items():
        print(f"   {n:26s} {len(s):6d} indirizzi")
    tutti = set().union(*dove.values()) if dove else set()
    print(f"   {'UNIONE':26s} {len(tutti):6d} indirizzi\n")

    # LE RIGHE NON SONO I CASI, E CI SONO RICASCATO QUI DENTRO.
    # Il segnalibro elenca "hash:indiceLog": una transazione che chiude due
    # posizioni compare DUE volte. La prima versione, per ognuna delle due
    # righe, rileggeva TUTTI i log della ricevuta -> 16 eventi invece di 12.
    # Scritta la lezione sul contatore e rifatto lo stesso errore venti
    # minuti dopo: non basta sapere che le righe non sono i casi, va
    # abbinato l'INDICE esatto, perche' la chiave e' la coppia (tx, log).
    visti, righe, gia = {}, [], set()
    for h in hashi:
        tx, _i = h.split(":")
        if tx in visti:
            r = visti[tx]
        else:
            r = _chiedi("eth_getTransactionReceipt", [tx])
            visti[tx] = r
        if not r:
            print(f"   {tx[:12]}... ricevuta non trovata, NON concludo")
            continue
        for lg in r.get("logs", []):
            if (lg["address"].lower() != POOL.lower()
                    or lg["topics"][0].lower() != FIRMA.lower()):
                continue
            if int(lg["logIndex"], 16) != int(_i, 16):
                continue
            if (tx, _i) in gia:
                continue
            gia.add((tx, _i))
            utente = "0x" + lg["topics"][3][-40:]
            righe.append({
                "tx": tx, "blocco": int(r["blockNumber"], 16),
                "utente": utente.lower(),
                "dentro": [n for n, s in dove.items() if utente.lower() in s],
            })

    print(f"liquidazioni lette dalla CATENA: {len(righe)} eventi, "
          f"{len({x['tx'] for x in righe})} transazioni\n")
    dentro = [x for x in righe if x["dentro"]]
    for x in sorted(righe, key=lambda y: y["blocco"]):
        print("   blocco %8d  %s  %s" % (
            x["blocco"], x["utente"],
            ("DENTRO: " + ",".join(x["dentro"])) if x["dentro"]
            else ">>> MAI SORVEGLIATO <<<"))
    print(f"\n   {len(dentro)} su {len(righe)} erano nella nostra "
          f"popolazione ({100*len(dentro)/max(len(righe),1):.0f}%)")
    if len(dentro) < len(righe):
        print("   => il buco NON e' la velocita': quelle non le guardavamo.")
    fuori = f"{D}/erano_nostre.json"
    tmp = fuori + ".tmp"
    json.dump({"eventi": len(righe), "dentro": len(dentro),
               "righe": righe, "popolazione": {n: len(s)
                                               for n, s in dove.items()}},
              open(tmp, "w"), indent=1)
    os.replace(tmp, fuori)
    return 0


if __name__ == "__main__":
    sys.exit(main())
