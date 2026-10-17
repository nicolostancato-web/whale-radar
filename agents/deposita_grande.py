"""Mette i file grossi fuori dal ramo, dove i file grossi stanno bene.

PERCHE' ESISTE (1/10). Il `pubblicatore` — l'unico che scrive sul ramo, quindi il collo di
bottiglia di tutto — falliva tre giri su dieci, e ogni fallimento era una email a Nicolo'. La
causa: `data/loop1/insieme_robinhood_sc5.jsonl.gz` pesa 64,4 MB e cresce ogni giorno. GitHub
avvisa a 50 MB e RIFIUTA a 100. Il 29/09 un file da 104,8 MB ha bloccato OGNI spinta per tre ore.

Il punto non e' comprimere meglio: e' che un insieme ricostruibile non ha niente da fare dentro
la storia di git. Ogni versione resta li' per sempre e il repository cresce di 64 MB al giorno,
anche quando il contenuto cambia di poco.

Qui va come allegato di una Release: fino a 2 GB, sostituibile, fuori dalla storia. Chi lo vuole
lo scarica (vedi agents/prendi_o_costruisci.py); chi non ce l'ha lo ricostruisce.

uso:  python agents/deposita_grande.py data/loop1/insieme_robinhood_sc5.jsonl.gz
"""
import json
import os
import sys
import urllib.error
import urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "nicolostancato-web/whale-radar")
TAG = os.environ.get("TAG_DEPOSITO", "insiemi")


def _chiama(url, tok, dati=None, metodo=None, tipo="application/json", tollera=()):
    """`tollera` = codici HTTP che non sono un errore per chi chiama.

    CANCELLARE CIO' CHE NON C'E' PIU' NON E' UN ERRORE (2/10). La cancellazione dell'allegato
    omonimo, prima di ricaricarlo, prendeva un 404 quando qualcun altro l'aveva gia' tolto — e
    quel 404 faceva cadere TUTTO il passo di deposito, quindi anche gli archivi che non avevano
    niente a che fare con lui. Misurato stanotte: due lavori in parallelo che depositavano gli
    stessi 48 archivi si pestavano a vicenda, e l'insieme a ingresso precoce non e' mai nato.
    """
    r = urllib.request.Request(url, data=dati, method=metodo,
                               headers={"Authorization": "token " + tok,
                                        "Accept": "application/vnd.github+json",
                                        "Content-Type": tipo})
    try:
        return urllib.request.urlopen(r, timeout=600)
    except urllib.error.HTTPError as e:
        if e.code in tollera:
            return None
        raise


def rilascio(tok):
    """Torna l'id della release col nostro tag, creandola se non c'e'."""
    try:
        return json.load(_chiama(
            f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}", tok))["id"]
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    corpo = json.dumps({"tag_name": TAG, "name": "insiemi ricostruibili",
                        "body": "Allegati rigenerabili: non stanno nel ramo perche' pesano "
                                "decine di MB e la loro storia non serve a nessuno.",
                        "prerelease": True}).encode()
    return json.load(_chiama(f"https://api.github.com/repos/{REPO}/releases", tok, corpo))["id"]


def deposita(percorso, tok=None):
    tok = tok or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not tok:
        return False, "senza token non deposito niente"
    if not os.path.exists(percorso):
        return False, f"non esiste: {percorso}"
    # UN FILE VUOTO NON SI DEPOSITA (2/10). Stanotte ho chiesto un insieme a ingresso 2; la
    # costruzione e' fallita, il fallimento e' stato inghiottito da un `|| echo`, e questo
    # depositatore ha caricato nel deposito un `insieme_base_sc2.jsonl.gz` da ZERO byte —
    # con il nome giusto, quindi credibile. E' la terza volta in un giorno che la stessa
    # famiglia si ripresenta: un segnaposto che somiglia a un risultato.
    # Soglia: 10.000 byte, la stessa che usa prendi_o_costruisci per rifiutare un download.
    taglia = os.path.getsize(percorso)
    if taglia < 10000:
        return False, (f"SOLO {taglia} byte: non lo deposito. Un archivio vuoto col nome giusto "
                       f"e' peggio di uno assente, perche' chi lo scarica crede di avere il dato.")
    nome = os.path.basename(percorso)
    rid = rilascio(tok)
    # un allegato con lo stesso nome va tolto prima: GitHub non sovrascrive, aggiunge
    for a in json.load(_chiama(f"https://api.github.com/repos/{REPO}/releases/{rid}/assets", tok)):
        if a["name"] == nome:
            _chiama(f"https://api.github.com/repos/{REPO}/releases/assets/{a['id']}",
                    tok, metodo="DELETE", tollera=(404, 422))
    dati = open(percorso, "rb").read()
    _chiama(f"https://uploads.github.com/repos/{REPO}/releases/{rid}/assets?name={nome}",
            tok, dati, tipo="application/octet-stream")
    return True, f"depositato {nome}: {len(dati)/1e6:.1f} MB, fuori dal ramo"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("uso: deposita_grande.py <file> [<file>...]")
    male = 0
    for f in sys.argv[1:]:
        ok, perche = deposita(f)
        print(f"DEPOSITO | {f}: {perche}", flush=True)
        male += 0 if ok else 1
    sys.exit(1 if male else 0)
