"""IL CANCELLO: nessun verdetto esce se non ha superato la prova sulla chain.

== PERCHE' ESISTE (7/10/2026) ==

Il difetto non e' stato un errore di calcolo: e' stato **l'ordine delle operazioni**. Producevo un
numero, lo comunicavo, e lo verificavo dopo — quando lo chiedeva Nicolo'.

Il 7/10 ho detto che un portafoglio aveva trasformato 3,36 dollari in 7.740. Lui ha aperto il
portafoglio su un sito: conteneva **11 euro**. La chain dice che quella vendita ha incassato
**3,36 dollari**: aveva chiuso in pari. Sbagliato di 2.300 volte, e il controllo costava due
minuti.

Parole sue: *«non darmi risultati a caso se non è sicuro, fai dei double check»*.

Quindi l'ordine si inverte, e non per buona volonta': **questo file e' un cancello.** Chi produce
un verdetto gli passa i suoi casi migliori; se anche uno solo non combacia con la chain, il
verdetto NON si scrive.

== COME VERIFICA ==

Per ogni caso: la transazione esiste, e' riuscita, e **l'importo che diciamo combacia con quello
che la chain dice** entro una tolleranza. Non si controlla il saldo del portafoglio (i soldi si
spostano): si controlla **lo scambio**, che e' un fatto.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from curva_pons import chiama, _numeri          # noqa: E402
import curva_pons as CP                          # noqa: E402

SWAP_V4 = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
SWAP_V2 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
SWAP_V3 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
TOLLERANZA = float(os.environ.get("TOLLERANZA", "0.10"))     # 10%


def _con_segno(v):
    return v - (1 << 256) if v >= (1 << 255) else v


def importi_dello_scambio(tx, decimali=18):
    """Gli importi dello scambio in quella transazione, letti dalla chain. (None se non c'e'.)

    LEGGE ANCHE LA CURVA (7/10, pomeriggio). All'inizio cercavo solo gli scambi nei pool
    (Uniswap v2/v3/v4), e su un acquisto sulla curva rispondevo «NON TROVATA» — che chi legge
    capisce come «la transazione non esiste», mentre voleva dire «non la so leggere». E' un
    falso negativo, cioe' il mio stesso peccato al contrario: un'ignoranza travestita da fatto.
    Una transazione con 9 CurveBuy mi faceva bocciare un caso che era sano.
    """
    r = chiama("eth_getTransactionReceipt", [tx])
    if not r:
        return None
    if int(r.get("status", "0x0"), 16) != 1:
        return "fallita"
    fuori = []
    for l in r.get("logs", []):
        t = (l.get("topics") or [None])[0]
        if t in (SWAP_V4, SWAP_V2, SWAP_V3):
            n = _numeri(l.get("data", "0x"))
            if len(n) >= 2:
                div = 10 ** int(decimali)
                fuori.append((_con_segno(n[0]) / div, _con_segno(n[1]) / div))
        elif t in (CP.T_COMPRA, CP.T_VENDE):
            # sulla curva i campi sono invertiti fra acquisto e vendita (verificato il 6/10):
            # CurveBuy campo 0 = valuta che entra; CurveSell campo 1 = valuta che esce.
            n = _numeri(l.get("data", "0x"))
            if len(n) >= 2:
                fuori.append((n[0] / (10 ** int(decimali)), n[1] / (10 ** int(decimali))))
    return fuori or None


def prova(casi, decimali=None):
    """casi = [{"tx":…, "valuta_attesa":…}]. Torna (passa, referto).

    `valuta_attesa` e' in unita' intere della valuta (es. ETH). Si confronta col lato dello
    scambio piu' vicino, perche' quale dei due sia la valuta dipende dal pool: se NESSUNO dei
    due combacia, il caso NON passa.
    """
    ref = []
    for c in casi:
        # LA SCALA NON SI INDOVINA (7/10 sera). Prima dividevo tutto per 10**18. Su un asset a
        # 9 decimali questo ha fatto bocciare un dato GIUSTO, e il verdetto si e' fermato per
        # colpa del controllo invece che del dato. Se i decimali non sono dichiarati non dico
        # «non combacia»: dico che non so leggere, perche' sono due cose diverse.
        dec = c.get("decimali", decimali)
        if dec is None:
            ref.append({"tx": c["tx"], "esito": "DECIMALI NON DICHIARATI (non so leggere)"})
            continue
        im = importi_dello_scambio(c["tx"], dec)
        if im is None:
            ref.append({"tx": c["tx"], "esito": "NON TROVATA"})
            continue
        if im == "fallita":
            ref.append({"tx": c["tx"], "esito": "TRANSAZIONE FALLITA"})
            continue
        att = abs(float(c["valuta_attesa"]))
        meglio, quale = None, None
        for a0, a1 in im:
            for v in (abs(a0), abs(a1)):
                if v <= 0:
                    continue
                err = abs(v - att) / max(att, 1e-18)
                if meglio is None or err < meglio:
                    meglio, quale = err, v
        ok = meglio is not None and meglio <= TOLLERANZA
        ref.append({"tx": c["tx"], "esito": "ok" if ok else "NON COMBACIA",
                    "atteso": att, "sulla_chain": quale,
                    "scarto_pct": None if meglio is None else round(100 * meglio, 1)})
    # un caso che non so leggere non e' un caso che non combacia: si contano a parte, e il
    # verdetto esce solo se TUTTI i leggibili combaciano e ce n'e' almeno uno.
    leggibili = [x for x in ref if not x["esito"].startswith("DECIMALI")]
    passa = bool(leggibili) and all(x["esito"] == "ok" for x in leggibili)
    return passa, ref


def stampa(passa, ref):
    print(f"PROVA | {sum(1 for x in ref if x['esito']=='ok')}/{len(ref)} casi combaciano "
          f"con la chain (tolleranza {int(TOLLERANZA*100)}%)", flush=True)
    for x in ref:
        if x["esito"] != "ok":
            print(f"   {x['esito']}: {x['tx'][:24]}…  atteso {x.get('atteso')}, "
                  f"sulla chain {x.get('sulla_chain')} (scarto {x.get('scarto_pct')}%)", flush=True)
    if not passa:
        print("PROVA | IL VERDETTO NON SI SCRIVE. Un solo caso che non combacia basta: "
              "il 7/10 un numero sbagliato di 2.300 volte e' uscito perche' la verifica "
              "veniva dopo.", flush=True)
    return passa


if __name__ == "__main__":
    # a mano: prima_la_prova.py <tx> <valuta attesa>
    if len(sys.argv) < 3:
        print("uso: prima_la_prova.py <hash> <valuta attesa>")
        sys.exit(1)
    p, r = prova([{"tx": sys.argv[1], "valuta_attesa": sys.argv[2]}])
    sys.exit(0 if stampa(p, r) else 1)
