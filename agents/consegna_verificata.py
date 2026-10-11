"""Consegna verificata: il successo e' una consegna riletta, non un processo finito.

LA REGOLA VIENE DA ASTRA (10/10): «Il registro non accetta una dichiarazione "success" dal
produttore. La ricava dalla consegna.» E il protocollo obbligatorio: prima di spendere si
verifica la destinazione; si carica con chiavi immutabili; si RILEGGE e si confronta l'impronta;
si scrive una ricevuta che elenca esattamente gli oggetti verificati; solo allora si dichiara
fatto.

PERCHE' SERVIVA. Il 10/10 trenta consulenze pagate sono morte perche' la corsia diceva «success»
senza aver consegnato niente, e un allegato con sette giorni di scadenza era l'unica copia. Un
processo che termina senza errori non dimostra che il lavoro esista da qualche parte.

CHIAVI IMMUTABILI: ogni consegna ha una chiave nuova che contiene la data e l'impronta. Non si
sovrascrive mai un risultato definitivo, cosi' una consegna sbagliata non cancella quella buona.
Il puntatore «l'ultima» e' un file separato, piccolo, aggiornato SOLO dopo la verifica.
"""
import hashlib
import io
import json
import os
import sys
import tarfile
import time

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

import deposito as D                                           # noqa: E402

RICEVUTE = "data/ricevute_consegne.jsonl"


def _impronta(b):
    return hashlib.sha256(b).hexdigest()


def consegna(percorsi, nome, prefisso="archive/"):
    """Carica i file su R2, li rilegge, confronta, scrive la ricevuta.

    Torna la ricevuta se tutto combacia, None se qualcosa non torna — e in quel caso NON
    scrive la ricevuta, perche' una ricevuta che certifica una consegna non verificata e'
    peggio di nessuna ricevuta.
    """
    s3, bucket = D.cliente()
    if not s3:
        print("CONSEGNA | nessuna credenziale per il deposito: non consegno e non mento")
        return None

    esistenti = [p for p in percorsi if os.path.exists(p)]
    if not esistenti:
        print("CONSEGNA | nessuno dei file esiste: niente da consegnare")
        return None

    # un solo archivio, con dentro le impronte dei singoli file
    dentro = {}
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        for p in esistenti:
            b = open(p, "rb").read()
            dentro[p] = {"byte": len(b), "impronta": _impronta(b)}
            t.add(p, arcname=p)
    corpo = buf.getvalue()
    imp = _impronta(corpo)
    giorno = time.strftime("%Y/%m/%d", time.gmtime())
    chiave = f"{prefisso}{nome}/{giorno}/{imp[:16]}.tar.gz"

    s3.put_object(Bucket=bucket, Key=chiave, Body=corpo)

    # LA VERIFICA: si rilegge dal deposito, non si crede alla risposta della scrittura
    letto = s3.get_object(Bucket=bucket, Key=chiave)["Body"].read()
    if _impronta(letto) != imp:
        print(f"CONSEGNA | FALLITA: quello che ho riletto non combacia con quello che ho "
              f"caricato ({chiave}). Non scrivo la ricevuta.")
        return None
    with tarfile.open(fileobj=io.BytesIO(letto), mode="r:gz") as t:
        nomi = set(t.getnames())
    manca = [p for p in esistenti if p not in nomi]
    if manca:
        print(f"CONSEGNA | FALLITA: nell'archivio riletto mancano {len(manca)} file. "
              f"Non scrivo la ricevuta.")
        return None

    ric = {"quando": int(time.time()), "nome": nome, "chiave": chiave,
           "impronta_archivio": imp, "byte_archivio": len(corpo),
           "file": dentro, "verificata": True}
    with open(RICEVUTE, "a", buffering=1) as f:
        f.write(json.dumps(ric) + "\n")
    # il puntatore all'ultima, piccolo e aggiornato SOLO ora
    s3.put_object(Bucket=bucket, Key=f"{prefisso}{nome}/ultima.json",
                  Body=json.dumps({"chiave": chiave, "quando": ric["quando"],
                                   "impronta": imp}).encode())
    print(f"CONSEGNA | {len(esistenti)} file, {len(corpo)/1e6:.1f} MB -> {chiave}")
    print(f"CONSEGNA | riletta e verificata: le impronte combaciano")
    return ric


def main():
    if len(sys.argv) < 3:
        print("uso: consegna_verificata.py <nome> <file...>")
        return 1
    return 0 if consegna(sys.argv[2:], sys.argv[1]) else 1


if __name__ == "__main__":
    sys.exit(main())
