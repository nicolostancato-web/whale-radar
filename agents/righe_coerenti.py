"""LEGGERE UN FILE A RIGHE RIFIUTANDO LE VERSIONI MESCOLATE.

== PERCHE' ESISTE (7/10/2026, a caro prezzo) ==

I file a righe si scrivono in aggiunta, giro dopo giro. Quando il codice cambia significato, il
file si ritrova righe di due formati diversi, e **sembra pieno**: nessun errore, nessun segnale.

Il 7/10 il 27,4% delle righe era in formato vecchio, senza la distinzione fra una vendita e un
travaso. I miei conti le sommavano alle nuove, e ne e' uscito un «guadagno di 7.740 dollari» dove
la chain dice **3,36**. Sbagliato di 2.300 volte. L'ha trovato Nicolo' aprendo il portafoglio su
un sito e vedendo che conteneva 11 euro.

Avevo gia' riconosciuto questa classe di errore nella notte e avevo messo un marcatore di versione
sul CONTATORE. Non bastava: quello butta il file della fetta in lavorazione, ma chi legge l'unione
di piu' fette aggiornate in momenti diversi vede la mescolanza. **La protezione era applicata a
meta'.**

== LA REGOLA ==

Chi legge NON decide cosa fare con le righe vecchie: le **rifiuta**, e lo dice. Perche' la
decisione «uso solo le nuove» sembra prudente ma non lo e': se metà del file e' vecchio, il
sottoinsieme nuovo puo' essere una fetta storta della realta' (per esempio solo le monete
rielaborate di recente).
"""
import gzip
import json
import os
import sys


def leggi(modelli, versione_attesa, chiave="v"):
    """Le righe di uno o piu' file, SOLO se sono tutte della versione attesa.

    Torna (righe, diagnosi). Se ci sono versioni mescolate, `righe` e' vuota e la diagnosi dice
    perche': chi chiama deve fermarsi, non scegliere.
    """
    import glob
    conta = {}
    righe = []
    for p in sorted(sum((glob.glob(m, recursive=True) for m in modelli), [])):
        ap = gzip.open if p.endswith(".gz") else open
        try:
            for ln in ap(p, "rt"):
                if not ln.strip():
                    continue
                x = json.loads(ln)
                v = x.get(chiave, "senza versione")
                conta[v] = conta.get(v, 0) + 1
                righe.append(x)
        except Exception as e:
            return [], {"errore": f"{os.path.basename(p)} illeggibile: {str(e)[:60]}"}
    if not conta:
        return [], {"vuoto": True}
    sole = set(conta)
    if sole != {versione_attesa}:
        return [], {"versioni_mescolate": conta, "attesa": versione_attesa,
                    "perche": ("righe di versioni diverse nello stesso insieme: sommarle "
                               "mescola due significati. Rifiuto, non scelgo.")}
    return righe, {"versione": versione_attesa, "righe": len(righe)}


def main():
    """A mano: dice che versioni ci sono in un insieme di file."""
    if len(sys.argv) < 2:
        print("uso: righe_coerenti.py <modello di file> [versione attesa]")
        return 1
    att = int(sys.argv[2]) if len(sys.argv) > 2 else -1
    r, d = leggi([sys.argv[1]], att)
    print(f"RIGHE | {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
