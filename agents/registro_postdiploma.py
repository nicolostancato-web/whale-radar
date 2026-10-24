"""IL REGISTRO DEL POST-DIPLOMA: ogni operazione, in ordine, con chi l'ha fatta.

== PERCHE' UN REGISTRO E NON UNA TABELLA DI SOMME (19/10, correzione di Astra) ==

Il primo disegno sommava per (portafoglio, moneta): quanti nativi dentro, quanti fuori. Quella
tabella risponde a «chi ha ricevuto piu' di quanto ha speso», che NON e' «chi ha guadagnato
facendo trading» e tanto meno «chi potevamo copiare». Un totale per portafoglio-moneta nasconde
centinaia di arbitraggi atomici, le uscite parziali, l'inventario arrivato da fuori e il momento
in cui l'informazione era visibile. Le somme restano, ma come VISTA DERIVATA del registro.

== DUE INSIDIE PAGATE DA ALTRI PRIMA DI NOI ==

1. **Un trasferimento non e' uno scambio.** Un gettone si muove anche per regali, per spostamenti
   fra portafogli della stessa persona, per liquidita'. Qui uno scambio si riconosce dalla
   CONTROPARTE: su Uniswap v4 i gettoni passano dal gestore unico, quindi un trasferimento
   DAL gestore e' un acquisto e UNO VERSO il gestore e' una vendita. Tutto il resto e' etichettato
   «non-scambio» e non entra nei profitti.
2. **Il mittente dello Swap e' il router, non la persona** (misurato il 7/10: 72 indirizzi per
   1.441 scambi, i primi cinque al 67%). L'identita' sta nella controparte del trasferimento,
   non nel campo `sender`.

== PERCHE' NON SI SCARICANO LE RICEVUTE ==

Attribuire col pieno rigore vorrebbe dire leggere la ricevuta di ogni transazione: ~850.000
chiamate, mezza giornata di RPC. Qui si fa il giro economico — due chiamate per moneta, i
trasferimenti e gli Swap — e si DICHIARA quanto resta non spiegato. Se la parte non spiegata e'
grossa o e' li' che stanno i vincitori, allora e solo allora si paga il prezzo delle ricevute.

Costo: zero. RPC pubblico, filtro per indirizzo (finestre da 10M blocchi, misurato).
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as C

GESTORE_V4 = "0x8366a39cc670b4001a1121b8f6a443a643e40951"
T_TRASF = C.firma("Transfer(address,address,uint256)")
T_SWAP = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
DENTRO = "data/multichain/robinhood/manifesto_graduati.json"
FUORI = "data/multichain/robinhood/registro_postdiploma.jsonl"
FATTE = "data/multichain/robinhood/registro_postdiploma_fatte.json"
FINESTRA = 9_999_999


def _segno(v):
    return v - (1 << 256) if v >= (1 << 255) else v


def swap_per_tx(pool, da):
    """Gli Swap di questo pool, indicizzati per transazione: da li' vengono i nativi."""
    lg = C.log_di_finestra(T_SWAP, da, da + FINESTRA, indirizzo=GESTORE_V4, secondo=pool)
    if lg is None:
        return None
    per = {}
    for l in lg:
        d = l["data"][2:]
        p = [int(d[i:i + 64], 16) for i in range(0, len(d), 64)]
        if len(p) < 2:
            continue
        per.setdefault(l["transactionHash"], []).append(
            {"a0": _segno(p[0]) / 1e18, "a1": _segno(p[1]) / 1e18,
             "blocco": int(l["blockNumber"], 16)})
    return per


def righe_moneta(moneta, pool, diploma):
    """Il registro di UNA moneta: ogni movimento del gettone dopo il diploma, classificato."""
    tr = C.log_di_finestra(T_TRASF, diploma, diploma + FINESTRA, indirizzo=moneta)
    if tr is None:
        return None
    sw = swap_per_tx(pool, diploma)
    if sw is None:
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
            verso, chi = "vende", mitt
        elif mitt == GESTORE_V4:
            verso, chi = "compra", dest
        else:
            verso, chi = "non-scambio", dest
        s = sw.get(h, [])
        # UNA SOLA corrispondenza vale come certa. Con piu' swap nella stessa transazione
        # l'abbinamento non e' unico e il nativo resta ignoto: non lo invento.
        nat, cert = None, "incerto"
        if verso != "non-scambio" and len(s) == 1:
            nat = abs(s[0]["a0"])
            cert = "certo"
        out.append({"b": int(l["blockNumber"], 16), "i": int(l["logIndex"], 16), "tx": h,
                    "chi": chi, "verso": verso, "gettoni": g, "nativi": nat, "conf": cert})
    out.sort(key=lambda r: (r["b"], r["i"]))
    return out


def main():
    man = json.load(open(DENTRO))["pool"]
    fatte = json.load(open(FATTE)) if os.path.exists(FATTE) else {}
    f = open(FUORI, "a")
    n = saltate = 0
    for idp, v in man.items():
        if idp in fatte:
            continue
        r = righe_moneta(v["moneta"], idp, v["diploma"])
        if r is None:
            saltate += 1
            continue
        f.write(json.dumps({"pool": idp, "moneta": v["moneta"], "diploma": v["diploma"],
                            "righe": r}) + "\n")
        f.flush()
        fatte[idp] = len(r)
        n += 1
        if n % 25 == 0:
            json.dump(fatte, open(FATTE, "w"))
            print(f"REGISTRO | {len(fatte)}/{len(man)} monete, {sum(fatte.values()):,} righe", flush=True)
    json.dump(fatte, open(FATTE, "w"))
    print(f"REGISTRO | finito: {len(fatte)}/{len(man)} monete, {sum(fatte.values()):,} righe, "
          f"{saltate} rifiutate dall'RPC")
    return 0


if __name__ == "__main__":
    sys.exit(main())
