"""L'accesso a Solana via Helius, e la lettura di uno scambio.

== COME SI LEGGE UNO SCAMBIO SU SOLANA (verificato il 22/10 su transazioni vere) ==

Niente log da decodificare come sugli EVM: si guarda quanto e' cambiato in tasca a CHI HA
FIRMATO. In una transazione vera: il firmatario spende 0,4315 SOL e riceve 442.968 gettoni,
mentre la cassa del pool ne manda esattamente altrettanti.
  - variazione SOL del firmatario   = quanto ha pagato o incassato
  - variazione del gettone di cui e' proprietario = quanto ne ha preso o dato
  - SOL in calo e gettone in salita = ha COMPRATO
Il prezzo e' il rapporto fra le due.

DUE INSIDIE, dette qui perche' non si scoprano dopo:
 1. la variazione di SOL del firmatario include la COMMISSIONE DI RETE e l'affitto dei conti:
    trascurabile su uno scambio da 0,43 SOL, non su uno da 0,001. Si scarta il minuscolo.
 2. moltissime transazioni su questi programmi FALLISCONO (bot che spammano): su pump.fun
    38 firme su 40 erano fallite. Si tengono solo quelle senza errore, e si dice quante sono.

COSTO: Helius a crediti, piano gratuito. Una lettura di transazione = ~1 credito.
"""
import json, os, re, time, urllib.request

SOL = "So11111111111111111111111111111111111111112"
_H = {"Content-Type": "application/json"}
_URL = {"v": None}


def url():
    if _URL["v"]:
        return _URL["v"]
    t = open(os.path.expanduser("~/Documents/b2b-finder-credentials.txt"),
             encoding="utf-8", errors="ignore").read()
    for k in dict.fromkeys(re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", t)):
        u = f"https://mainnet.helius-rpc.com/?api-key={k}"
        try:
            c = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "getSlot", "params": []}).encode()
            if "result" in json.loads(urllib.request.urlopen(urllib.request.Request(u, c, _H), timeout=15).read()):
                _URL["v"] = u
                return u
        except Exception:
            pass
    return None


def rpc(metodo, par, tentativi=3):
    u = url()
    if not u:
        return None
    c = json.dumps({"jsonrpc": "2.0", "id": 1, "method": metodo, "params": par}).encode()
    for k in range(tentativi):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(u, c, _H), timeout=25).read())
            if "error" in r:
                return None
            return r.get("result")
        except Exception:
            time.sleep(1 + 2 * k)
    return None


def scambio(sig):
    """(slot, prezzo in SOL per gettone, e_un_acquisto, chi, gettone) oppure None."""
    t = rpc("getTransaction", [sig, {"maxSupportedTransactionVersion": 2,
                                     "encoding": "jsonParsed", "commitment": "confirmed"}])
    if not t or t.get("meta", {}).get("err"):
        return None
    meta = t["meta"]
    chiavi = [a["pubkey"] if isinstance(a, dict) else a
              for a in t["transaction"]["message"]["accountKeys"]]
    if not chiavi:
        return None
    chi = chiavi[0]
    dsol = (meta["postBalances"][0] - meta["preBalances"][0]) / 1e9
    pre = {x["accountIndex"]: float(x["uiTokenAmount"]["uiAmount"] or 0)
           for x in meta.get("preTokenBalances", [])}
    migliore = None
    for x in meta.get("postTokenBalances", []):
        if x.get("owner") != chi or x["mint"] == SOL:
            continue
        d = float(x["uiTokenAmount"]["uiAmount"] or 0) - pre.get(x["accountIndex"], 0.0)
        if migliore is None or abs(d) > abs(migliore[1]):
            migliore = (x["mint"], d)
    if not migliore or migliore[1] == 0 or abs(dsol) < 0.002:   # sotto i ~0,30 EUR domina la commissione
        return None
    gettone, dget = migliore
    if (dsol < 0) == (dget < 0):          # devono avere segno opposto: uno entra, l'altro esce
        return None
    return (t["slot"], abs(dsol / dget), dsol < 0, chi, gettone)
