"""L'accesso a Base, con i limiti MISURATI invece che assunti (21/10).

Misurato oggi sui quattro RPC pubblici conosciuti:
  mainnet.base.org        -> 429 quasi subito
  base.llamarpc.com       -> 525
  base-rpc.publicnode.com -> accetta 500 blocchi, 12.378 log dentro   <- si usa questo
  1rpc.io/base            -> massimo 50 blocchi, inutilizzabile

Base fa un blocco ogni ~2 secondi: 500 blocchi sono ~17 minuti di chain, quindi sei ore
costano una ventina di chiamate. Il nostro secondo di ritardo qui vale MEZZO blocco, non
undici come su Robinhood: e' una differenza importante e va tenuta nei conti.
"""
import json, os, time, urllib.error, urllib.request

# I NODI, PROVATI UNO PER UNO IL 21/10 (non scelti a fiducia):
#   publicnode  -> veloce, ma NIENTE ricevute e NIENTE storico oltre ~5 ore
#   drpc.org    -> ricevute SI, storico SI (>=50.000 blocchi = ~28 ore)   <- principale
#   tenderly    -> ricevute SI, storico SI                                <- riserva
#   blastapi    -> ricevute si, storico no
#   meowrpc / omniatech / blockpi -> non rispondono
# Senza ricevute non si risale dal pool al gettone, e senza storico non si fa nessuna prova
# su piu' periodi: per due ore ho lavorato su un nodo che non poteva dare ne' l'una ne'
# l'altro, e il sintomo era «zero gettoni identificati», senza errori.
RPC = os.environ.get("BASE_RPC", "https://base.drpc.org")
RISERVA = "https://gateway.tenderly.co/public/base"
GESTORE_V4 = "0x498581ff718922c3f8e6a244956af099b2652b2b"
BLOCCO = 2.0
FINESTRA = 500
_H = {"Content-Type": "application/json",
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
_ERRORI = []


def chiama(metodo, par=None, tentativi=6):
    corpo = json.dumps({"jsonrpc": "2.0", "id": 1, "method": metodo,
                        "params": par if par is not None else []}).encode()
    for k in range(tentativi):
        try:
            q = urllib.request.Request(RPC, corpo, _H)
            r = json.loads(urllib.request.urlopen(q, timeout=40).read())
            if "error" in r:
                _ERRORI.append(str(r["error"])[:90])
                # un errore di merito non si ritenta all'infinito
                if "limited" in str(r["error"]).lower() or "range" in str(r["error"]).lower():
                    return None
                time.sleep(2 + 3 * k)
                continue
            return r.get("result")
        except urllib.error.HTTPError as e:
            if k == 2 and RISERVA:
                globals()["RPC"] = RISERVA     # si passa alla riserva invece di insistere
            # 403 SU QUESTO NODO VUOL DIRE «BLOCCO TROPPO VECCHIO», NON «RIPROVA» (21/10).
            # Trattarlo come guasto temporaneo costava 57s di attese per chiamata, e poi
            # log_di_finestra dimezzava e ripeteva su entrambe le meta': un blocco
            # esponenziale che ha tenuto fermo un processo per cinquanta minuti con un
            # secondo di calcolo. Un limite si riconosce e si dichiara, non si aspetta.
            _ERRORI.append(f"HTTP {e.code}")
            if e.code in (403, 404):
                return None
            time.sleep(2 + 3 * k)
        except Exception as e:
            _ERRORI.append(str(e)[:90])
            time.sleep(2 + 3 * k)
    return None


def log_di_finestra(topic, da, a, indirizzo=None, secondo=None):
    """I log fra due blocchi, dimezzando se la finestra e' troppo densa."""
    q = {"fromBlock": hex(da), "toBlock": hex(a)}
    if indirizzo:
        q["address"] = indirizzo
    t = [topic] if topic else []
    if secondo:
        t = [topic, secondo]
    if t:
        q["topics"] = t
    r = chiama("eth_getLogs", [q])
    if r is not None:
        return r
    if a - da < 20:
        return None
    mz = (da + a) // 2
    s = log_di_finestra(topic, da, mz, indirizzo, secondo)
    if s is None:
        return None
    d = log_di_finestra(topic, mz + 1, a, indirizzo, secondo)
    if d is None:
        return None
    return s + d


_PROF = {}


def profondita(t=None):
    """Quanto indietro arriva questo nodo, MISURATO (21/10): circa 3 ore, poi 403.

    Si misura invece di assumerlo, perche' il limite cambia col nodo e un limite assunto
    e' esattamente il tipo di cosa che ci ha gia' fatto perdere mezza giornata.
    """
    # SI MISURA UNA VOLTA SOLA E SI RICORDA (21/10). Chiamandola dentro la condizione di un
    # ciclo veniva rifatta a ogni giro, e quando una sonda cadeva per fretta tornava ZERO: il
    # ciclo non partiva nemmeno e il risultato era «nessun gettone trovato», in silenzio.
    # Uno zero che arriva senza errore e' sempre il piu' pericoloso.
    if _PROF.get("v"):
        return _PROF["v"]
    if t is None:
        t = testa()
    if not t:
        return 0
    basso, alto = 0, 200_000
    while alto - basso > 2_000:
        mz = (basso + alto) // 2
        r = chiama("eth_getLogs", [{"fromBlock": hex(t - mz), "toBlock": hex(t - mz + 20),
                                    "address": GESTORE_V4}])
        if r is None:
            # una sonda caduta puo' essere fretta, non profondita': si riprova una volta
            time.sleep(3)
            r = chiama("eth_getLogs", [{"fromBlock": hex(t - mz), "toBlock": hex(t - mz + 20),
                                        "address": GESTORE_V4}])
        if r is None:
            alto = mz
        else:
            basso = mz
    if basso:
        _PROF["v"] = basso
    return basso


def testa():
    bn = chiama("eth_blockNumber")
    return int(bn, 16) if bn else None
