"""Il deposito su Cloudflare R2: dove i dati vivono senza che la loro storia ci schiacci.

PERCHE' ESISTE (26/09). Il repository era arrivato a 7,84 GB con il blocco delle scritture a 10, e
di quegli 8 GB i dati veri erano mezzo: tutto il resto era CRONOLOGIA. Git conserva ogni versione di
ogni file, e un file compresso che cambia di una riga e' per git un file nuovo da capo. Tenere dati
che cambiano ogni ora dentro una storia che non dimentica e' il difetto, non la quantita' di dati.

Qui i dati stanno senza storia: una versione, quella buona, sovrascritta.
La storia del CODICE resta su git dov'e' giusto che sia.

LA REGOLA CHE TIENE IL CONTO A ZERO — si legge prima di toccare questo file.
R2 da' 10 GB e **un milione di scritture al mese** gratis, poi $4,50 per milione.
Abbiamo centomila file di pool. Caricarli uno a uno, dodici volte al giorno, farebbe
**1,2 milioni di scritture al giorno**: il gratuito bruciato in venti ore e un conto da trenta
dollari al mese senza accorgersene. E' la stessa forma dei 77 euro di Google Places: il prezzo per
unita' sembra irrisorio finche' non lo moltiplichi per il numero di unita' vere.
QUINDI: **si caricano pochi archivi grossi, mai tanti file piccoli.** Un archivio per chain.
Con questa regola le scritture stanno sotto il migliaio al mese invece che sopra il milione.

Lo scaricamento su R2 costa ZERO, sempre: le corsie possono rileggere quanto vogliono. E' la
ragione per cui e' stato scelto lui e non Backblaze o Amazon, dove ogni lettura si paga.
"""
import io
import os
import re
import sys
import tarfile

CARTELLA_CREDENZIALI = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")


def _credenziali():
    """Dall'ambiente sul cloud, dal file sul Mac. Mai chieste, mai stampate."""
    d = {k: os.environ.get("R2_" + k) for k in
         ("ENDPOINT", "BUCKET", "ACCESS_KEY_ID", "SECRET_ACCESS_KEY")}
    if all(d.values()):
        return d
    if not os.path.exists(CARTELLA_CREDENZIALI):
        return None
    t = open(CARTELLA_CREDENZIALI, encoding="utf-8", errors="ignore").read()
    i = t.upper().find("CLOUDFLARE R2")
    if i < 0:
        return None
    b = t[i:i + 700]
    for k in d:
        m = re.search(rf"{k}\s*[:=]\s*(\S+)", b)
        if m:
            d[k] = m.group(1)
    return d if all(d.values()) else None


def cliente():
    import boto3
    c = _credenziali()
    if not c:
        print("DEPOSITO | credenziali R2 assenti", flush=True)
        return None, None
    return boto3.client("s3", endpoint_url=c["ENDPOINT"],
                        aws_access_key_id=c["ACCESS_KEY_ID"],
                        aws_secret_access_key=c["SECRET_ACCESS_KEY"],
                        region_name="auto"), c["BUCKET"]


def deposita_cartella(cartella, chiave):
    """Una cartella intera in UN SOLO oggetto compresso. Una scrittura, non centomila.

    Torna (numero di file, byte caricati) oppure None se non si e' potuto.
    """
    s3, bucket = cliente()
    if not s3:
        return None
    buf = io.BytesIO()
    n = 0
    # `w|gz` scrive in streaming: non tiene in memoria un archivio da centinaia di megabyte.
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for radice, _, files in os.walk(cartella):
            for f in sorted(files):
                p = os.path.join(radice, f)
                tar.add(p, arcname=os.path.relpath(p, cartella))
                n += 1
    dati = buf.getvalue()
    s3.put_object(Bucket=bucket, Key=chiave, Body=dati)
    print(f"DEPOSITO | {chiave}: {n} file, {len(dati)/1e6:.1f} MB, UNA scrittura", flush=True)
    return n, len(dati)


def ritira_cartella(chiave, destinazione):
    """Rimette a terra un archivio depositato. Lo scaricamento non costa niente."""
    s3, bucket = cliente()
    if not s3:
        return None
    try:
        dati = s3.get_object(Bucket=bucket, Key=chiave)["Body"].read()
    except Exception as e:
        print(f"DEPOSITO | {chiave} non ritirabile: {type(e).__name__}", flush=True)
        return None
    os.makedirs(destinazione, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(dati), mode="r:gz") as tar:
        tar.extractall(destinazione)
        n = len(tar.getnames())
    print(f"DEPOSITO | ritirato {chiave}: {n} elementi in {destinazione}", flush=True)
    return n


def elenco():
    """Cosa c'e' nel deposito, con quanto pesa. Serve a sorvegliare i 10 GB gratuiti."""
    s3, bucket = cliente()
    if not s3:
        return []
    fuori, tok = [], None
    while True:
        kw = {"Bucket": bucket}
        if tok:
            kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        fuori += [(o["Key"], o["Size"], o["LastModified"]) for o in r.get("Contents", [])]
        if not r.get("IsTruncated"):
            break
        tok = r.get("NextContinuationToken")
    return fuori


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "deposita":
        deposita_cartella(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 4 and sys.argv[1] == "ritira":
        ritira_cartella(sys.argv[2], sys.argv[3])
    else:
        tot = 0
        for k, s, q in elenco():
            print(f"   {k:50} {s/1e6:8.1f} MB  {q:%d/%m %H:%M}")
            tot += s
        print(f"   TOTALE {tot/1e9:.2f} GB su 10 GB gratuiti ({100*tot/10e9:.1f}%)")
