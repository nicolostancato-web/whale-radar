"""Una sola libreria per leggere gli archivi, qualunque sia il loro formato.

PERCHE' ESISTE (10/10, prescrizione di Astra): «Eliminare l'oggetto monolitico; partizionare per
entita' e finestra temporale. Dare ai dieci script UNA SOLA libreria di lettura. La migrazione
viene DOPO aver introdotto la libreria comune: dieci migrazioni indipendenti produrrebbero dieci
interpretazioni incompatibili.»

Il caso concreto: `curva_lanci.json.gz` e' un dizionario unico da 52 MB con 675.145 voci sotto la
chiave `da`, piu' sei campi di intestazione. Per aggiungere un lancio si riscrive tutto, e ogni
riscrittura entra INTERA nella storia di git. Dieci script lo leggono con
`json.load(gzip.open(...))` e poi prendono `dl["da"]`.

Questa libreria espone quello che gli script usano davvero — intestazione e mappa delle voci — e
nasconde DOVE e COME stanno. Cosi' la conversione a righe e' una riga di codice qui, non dieci
migrazioni la' fuori.

LE DUE FORME, lette senza che il chiamante sappia quale c'e':
  vecchia:  <nome>.json.gz        un oggetto solo: {..., "da": {chiave: valore}}
  nuova:    <nome>.meta.json      la sola intestazione
            <nome>.voci.jsonl     una voce per riga: {"k": chiave, "v": valore}
La nuova si aggiunge in coda: scrivere un lancio costa la sua riga, non 52 MB.
"""
import gzip
import json
import os
import sys

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"


def _strade(nome):
    return (f"{BASE}/{nome}.json.gz", f"{BASE}/{nome}.meta.json", f"{BASE}/{nome}.voci.jsonl")


def sorgente(nome):
    """Quale forma esiste oggi per questo archivio. Serve a dirlo nei referti."""
    v, m, r = _strade(nome)
    if os.path.exists(m) and os.path.exists(r):
        return "a righe"
    if os.path.exists(v):
        return "un pezzo compresso"
    if os.path.exists(f"{BASE}/{nome}.json"):
        return "un pezzo non compresso"
    return "assente"


def esiste(nome):
    v, m, r = _strade(nome)
    return os.path.exists(v) or (os.path.exists(m) and os.path.exists(r))


def leggi(nome, chiave_voci="da"):
    """(intestazione, voci). L'intestazione e' un dizionario, le voci una mappa chiave->valore."""
    vecchio, meta, righe = _strade(nome)
    if os.path.exists(meta) and os.path.exists(righe):
        test = json.load(open(meta))
        voci = {}
        with open(righe, errors="replace") as f:
            for r in f:
                r = r.strip()
                if not r:
                    continue
                try:
                    o = json.loads(r)
                except json.JSONDecodeError:
                    continue      # una riga troncata non deve rendere illeggibile tutto il resto
                voci[o["k"]] = o["v"]
        return test, voci
    if os.path.exists(vecchio):
        d = json.load(gzip.open(vecchio, "rt"))
        voci = d.pop(chiave_voci, {})
        return d, voci
    semplice = f"{BASE}/{nome}.json"
    if os.path.exists(semplice):
        # ALCUNI ARCHIVI NON HANNO INTESTAZIONE: tutto il dizionario sono le voci (coppie.json,
        # 69.697 chiavi). Si legge con `chiave_voci=None`, e l'intestazione torna vuota: cosi'
        # la libreria copre entrambe le forme senza che il chiamante debba sapere quale sia.
        d = json.load(open(semplice, errors="replace"))
        if chiave_voci and isinstance(d, dict) and chiave_voci in d:
            voci = d.pop(chiave_voci)
            return d, voci
        return {}, d
    raise FileNotFoundError(f"{nome}: non c'e' ne' la forma vecchia ne' quella nuova")


def aggiungi(nome, nuove, chiave_voci="da"):
    """Scrive SOLO le voci nuove, in coda. E' il motivo per cui esiste la forma a righe."""
    vecchio, meta, righe = _strade(nome)
    if not os.path.exists(meta):
        raise FileNotFoundError(f"{nome}: non e' ancora convertito a righe (manca {meta})")
    with open(righe, "a", buffering=1) as f:
        for k, v in nuove.items():
            f.write(json.dumps({"k": k, "v": v}) + "\n")
    return len(nuove)


def converti(nome, chiave_voci="da"):
    """Dalla forma vecchia a quella a righe, verificando che il contenuto sia IDENTICO.

    La verifica non e' un lusso: se la conversione perdesse una voce su mille, dieci script
    comincerebbero a dare risposte leggermente diverse e nessuno saprebbe perche'.
    """
    vecchio, meta, righe = _strade(nome)
    test, voci = leggi(nome, chiave_voci)
    json.dump(test, open(meta, "w"), indent=1)
    with open(righe, "w", buffering=1) as f:
        for k, v in voci.items():
            f.write(json.dumps({"k": k, "v": v}) + "\n")
    t2, v2 = leggi(nome, chiave_voci)
    if len(v2) != len(voci):
        print(f"ARCHIVIO | CONVERSIONE FALLITA: {len(voci)} voci prima, {len(v2)} dopo")
        return False
    diversi = [k for k in voci if v2.get(k) != voci[k]]
    if diversi:
        print(f"ARCHIVIO | CONVERSIONE FALLITA: {len(diversi)} voci cambiate di contenuto")
        return False
    if t2 != test:
        print("ARCHIVIO | CONVERSIONE FALLITA: l'intestazione non combacia")
        return False
    a = (os.path.getsize(vecchio) if os.path.exists(vecchio)
         else (os.path.getsize(f"{BASE}/{nome}.json")
               if os.path.exists(f"{BASE}/{nome}.json") else 0))
    b = os.path.getsize(meta) + os.path.getsize(righe)
    print(f"ARCHIVIO | {nome}: {len(voci):,} voci verificate una per una, identiche")
    print(f"ARCHIVIO | {a/1e6:.1f} MB in un pezzo  ->  {b/1e6:.1f} MB a righe "
          f"(ma ora un'aggiunta costa UNA RIGA, non {a/1e6:.0f} MB)")
    return True


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "converti":
        return 0 if converti(sys.argv[2]) else 1
    nome = sys.argv[1] if len(sys.argv) > 1 else "curva_lanci"
    test, voci = leggi(nome)
    print(f"ARCHIVIO | {nome}: intestazione {sorted(test)}, {len(voci):,} voci")
    return 0


if __name__ == "__main__":
    sys.exit(main())
