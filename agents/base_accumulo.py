"""ACCUMULO DEI POOL NUOVI SU BASE: il campione si costruisce in avanti.

PERCHE' (21/10). Nei primi due minuti di vita di un pool la resa si stacca dalla propria
taratura (-0,19% di costo, +0,94% a mezz'ora) — ma sono 15 pool, e con quindici casi non si
conclude niente. Su Base nascono ~216 pool all'ora, quindi la materia prima c'e'; il nodo
pero' serve solo le ultime ~5 ore, quindi il passato non si puo' prendere: SI ACCUMULA IN
AVANTI.

Ed e' la forma piu' onesta di prova che esista: ogni pool che entra da qui in poi e' un caso
mai visto quando l'ipotesi e' stata formulata. Nessun rischio di aver scelto la soglia dopo
aver guardato.

L'IPOTESI E' CONGELATA QUI, ORA, PRIMA DI ACCUMULARE:
  entrata su una stampa di ACQUISTO entro i primi 120 secondi di vita del pool, un blocco
  dopo il segnale; uscita su una stampa di VENDITA a +30 minuti; il risultato va confrontato
  con la taratura dello stesso gruppo. Serve che la differenza resti sopra un punto.
"""
import collections, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base_rpc as B

SW = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
INIT = "0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
FUORI = "data/multichain/base/accumulo_nuovi.jsonl"
FATTE = "data/multichain/base/accumulo_fatte.json"


def _sg(x):
    v = int(x, 16)
    return v - (1 << 256) if v >= (1 << 255) else v


def main():
    t = B.testa()
    if not t:
        print("ACCUMULO | l'RPC non da la testa")
        return 1
    prof = B.profondita(t)
    da = t - prof
    fatte = set(json.load(open(FATTE))) if os.path.exists(FATTE) else set()
    nascita, per, fee = {}, collections.defaultdict(list), {}
    b = da
    while b <= t:
        f = min(b + B.FINESTRA - 1, t)
        for l in B.log_di_finestra(INIT, b, f, indirizzo=B.GESTORE_V4) or []:
            nascita[l["topics"][1]] = int(l["blockNumber"], 16)
        for l in B.log_di_finestra(SW, b, f, indirizzo=B.GESTORE_V4) or []:
            d = l["data"][2:]
            if len(d) < 384:
                continue
            a0, a1 = _sg(d[0:64]), _sg(d[64:128])
            if not (a0 and a1):
                continue
            per[l["topics"][1]].append([int(l["blockNumber"], 16), abs(a0 / a1), a0 < 0])
            fee[l["topics"][1]] = int(d[320:384], 16)
        b = f + 1
        time.sleep(0.15)
    # si salva solo chi e' NATO in questa finestra, ha abbastanza scambi, ed e' gia' vissuto
    # abbastanza perche' l'uscita a +30 minuti esista davvero: niente mezze storie.
    nuovi = 0
    os.makedirs("data/multichain/base", exist_ok=True)
    with open(FUORI, "a") as fh:
        for idp, n0 in nascita.items():
            if idp in fatte:
                continue
            P = sorted(per.get(idp, []))
            # L'AMMISSIONE DIPENDE SOLO DA CIO' CHE SI SA AL MOMENTO DI COMPRARE (21/10).
            # Chiedere «almeno 30 scambi e mezz'ora di vita» seleziona i SOPRAVVISSUTI: al
            # secondo 120 non posso sapere che il pool sara' vivo a mezz'ora. Qui si chiede
            # solo attivita' nei PRIMI DUE MINUTI (cosa osservabile), e si pretende che sia
            # passata mezz'ora di CHAIN dalla nascita — non che il pool abbia scambiato.
            # I pool morti restano dentro, ed e' giusto: sono il costo della strategia.
            primi = [x for x in P if x[0] - n0 <= 60]
            if len(primi) < 5 or t - n0 < 930:
                continue
            fh.write(json.dumps({"pool": idp, "nato": n0, "fee": fee.get(idp, 0), "s": P}) + "\n")
            fatte.add(idp)
            nuovi += 1
    json.dump(sorted(fatte), open(FATTE, "w"))
    print(f"ACCUMULO | nati in finestra {len(nascita):,}, ammessi {nuovi}, "
          f"totale in archivio {len(fatte):,}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
