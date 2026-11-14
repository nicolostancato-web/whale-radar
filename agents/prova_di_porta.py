"""Ci includono, o ci ignorano? La prova che non ha bisogno di una caduta.

L'IDEA E' DI ASTRA (consulenza del 5/11, punto 1 e 4), ed e' l'unica che
non avevo considerato: dodicimila pacchetti accettati dai relay e zero
inclusi e' compatibile con un FILTRO DI REPUTAZIONE sul mittente. In quel
caso il problema non e' l'offerta, e' la porta -- e nessuna taratura della
mancia lo risolverebbe.

Il modo di saperlo senza aspettare una liquidazione: un pacchetto che non
fa NIENTE se non portare valore a chi costruisce. Nessun conflitto con
altri searcher, nessuna dipendenza dal mercato. Se un pacchetto cosi' non
entra, non e' questione di quanto offriamo.

Lo strumento piu' semplice che non richiede un contratto nuovo: una
transazione da noi a noi, 21.000 gas, con una priority fee alta. Per chi
costruisce il blocco quel valore e' reale e immediato.

COSTO: si paga SOLO se entra -- ed e' esattamente il risultato che
vogliamo comprare. A 30 gwei su 21.000 di gas sono 0,00063 ETH, circa
1,50 $. Se non entra, zero.
"""
import json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pescatore as P
from invia_pacchetto import a_tutte_le_porte

D = "data/liquidazioni"
FUORI = f"{D}/prova_di_porta.json"
PADRONE = "0x4355962379c779009f833d81bd8d2912773749a0"
GWEI_OFFERTA = 30          # la priority che offriamo in questa prova
BLOCCHI_AVANTI = 3         # per quanti blocchi la proponiamo


def _firma(nonce, blocco_base):
    """Una transazione da noi a noi, vuota, con l'offerta alta."""
    chiave = subprocess.run(
        ["grep", "-oE", "Private key wallet 1 0x[a-fA-F0-9]{64}",
         os.path.expanduser("~/Documents/b2b-finder-credentials.txt")],
        capture_output=True, text=True).stdout.strip().split()[-1]
    F = P.FOUNDRY
    r = subprocess.run([f"{F}/cast", "mktx", PADRONE,
                        "--value", "0",
                        "--priority-gas-price", str(GWEI_OFFERTA * 10**9),
                        "--gas-price", str((GWEI_OFFERTA + 2) * 10**9),
                        "--gas-limit", "21000",
                        "--nonce", str(nonce),
                        "--rpc-url", P.U,
                        "--private-key", chiave],
                       capture_output=True, text=True)
    out = r.stdout.strip()
    return out if out.startswith("0x") else None


def prova():
    testa = int(P.rpc("eth_blockNumber", []), 16)
    nonce = int(P.rpc("eth_getTransactionCount", [PADRONE, "latest"]), 16)
    raw = _firma(nonce, testa)
    if not raw:
        print("   FERMO: non ho potuto firmare la transazione di prova")
        return None
    costo_eth = 21000 * GWEI_OFFERTA * 1e-9
    print(f"   offerta {GWEI_OFFERTA} gwei su 21.000 gas = {costo_eth:.6f} ETH "
          f"(si paga SOLO se entra)")
    esiti = {}
    for d in range(1, BLOCCHI_AVANTI + 1):
        corpo = {"txs": [raw], "blockNumber": hex(testa + d)}
        es = a_tutte_le_porte("eth_sendBundle", [corpo])
        esiti[testa + d] = {k: bool(v[0]) for k, v in es.items()}
        print(f"   blocco {testa+d}: " +
              ", ".join(f"{k}={'si' if v[0] else 'no'}" for k, v in es.items()))
    out = {"quando": time.time(), "nonce": nonce, "da_blocco": testa + 1,
           "gwei": GWEI_OFFERTA, "accettata_da": esiti, "inclusa": None}
    json.dump(out, open(FUORI, "w"), indent=1)
    return out


def guarda_se_e_entrata():
    """Si controlla il NONCE: se e' avanzato, la transazione e' entrata."""
    try:
        o = json.load(open(FUORI))
    except FileNotFoundError:
        return None
    n = int(P.rpc("eth_getTransactionCount", [PADRONE, "latest"]), 16)
    entrata = n > o["nonce"]
    o["inclusa"] = entrata
    o["nonce_ora"] = n
    json.dump(o, open(FUORI, "w"), indent=1)
    print(f"   nonce era {o['nonce']}, ora {n} -> "
          + ("ENTRATA: i costruttori ci includono"
             if entrata else "NON entrata"))
    return o


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "guarda":
        guarda_se_e_entrata()
    else:
        prova()
