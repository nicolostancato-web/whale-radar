"""Lanciare una moneta sulla fabbrica Pons. DI PROVA finche' non si passa --vero.

PERCHE' (19/10). Tutto il lato creatore e' misurato tranne una cosa: dove finisce la tassa del
campo [3] di CurveBuy. Il nodo non ha tracciamento ne' storico, quindi l'unica risposta e' un
lancio vero da 1,50 EUR di tariffa + ~0,70 di gas. Questo file prepara e PROVA la chiamata
senza spendere: con eth_call la fabbrica esegue davvero il codice e dice se la codifica e'
giusta, a costo zero.

LA FORMA DELLA CHIAMATA, ricavata da lanci diretti veri (selettore 0xa72101af verso la
fabbrica), non da una ABI trovata online:
   arg0 = tupla (nome, simbolo, uri, descrizione, 5 stringhe social vuote, creatore,
                 uint 0, uint 0, bytes32 costante, bytes32 seme)
   arg1 = 0, arg2 = 0, arg3 = bytes vuoti
   valore allegato: esattamente 0.0005 nativi in TUTTI i lanci diretti visti.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bot_curva as B
import curva_pons as C

SEL = "0xa72101af"
COSTANTE = "a9fc75d4203a33fe660e8fa32c74c3aa41c1fda4bf23d3a39b6bc22a1f8b1ca7"
TARIFFA = 500_000_000_000_000          # 0.0005 nativi, misurato su tutti i lanci diretti


def parola(x):
    return f"{x:064x}"


def stringa(s):
    b = s.encode()
    pezzi = (len(b) + 31) // 32 or 1
    return parola(len(b)) + b.hex().ljust(pezzi * 64, "0")


def dati(nome, simbolo, uri, descrizione, creatore, seme):
    social = parola(160) + parola(192) + parola(224) + parola(256) + parola(288) + parola(0) * 5
    corpi = [stringa(nome), stringa(simbolo), stringa(uri), stringa(descrizione), social]
    # le teste della tupla sono 10 parole: 5 scostamenti + creatore + 2 zeri + 2 bytes32
    base = 10 * 32
    sco, acc = [], base
    for c in corpi:
        sco.append(acc)
        acc += len(c) // 2
    tup = "".join(parola(x) for x in sco)
    tup += parola(int(creatore, 16)) + parola(0) + parola(0) + COSTANTE + seme
    tup += "".join(corpi)
    testa = parola(128) + parola(0) + parola(0) + parola(128 + len(tup) // 2)
    return SEL + testa + tup + parola(0)


def main():
    vero = "--vero" in sys.argv
    conti = B.chiavi()
    if not conti:
        print("LANCIA | nessun portafoglio: non invento una chiave")
        return 1
    from eth_account import Account
    c = Account.from_key(conti[0])
    seme = f"{int(time.time()):064x}"
    d = dati("CRAFT", "CRAFT", "ipfs://", "test", c.address, seme)
    print(f"LANCIA | mittente {c.address[:10]}... | tariffa {TARIFFA/1e18*3000:.2f} EUR | dati {len(d)//2} byte")
    r = C.chiama("eth_call", [{"from": c.address, "to": C.FABBRICA,
                               "data": d, "value": hex(TARIFFA)}, "latest"])
    if r is None:
        print("LANCIA | la PROVA e' stata rifiutata: la codifica non va ancora bene, non mando nulla")
        return 1
    print(f"LANCIA | PROVA superata, la fabbrica accetta la chiamata -> {str(r)[:80]}")
    if not vero:
        print("LANCIA | nessuna transazione mandata (serve --vero, e il permesso di Nicolo')")
        return 0
    print("LANCIA | --vero non e' ancora abilitato in questo file: si abilita quando si decide")
    return 0


if __name__ == "__main__":
    sys.exit(main())
