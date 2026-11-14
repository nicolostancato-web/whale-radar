#!/usr/bin/env python3
"""UN PREVENTIVO SI CONFRONTA COL VALORE GIUSTO, NON SI ACCETTA.

La causa, trovata il 7/11 e non prima. La nostra unica prova completa
fallisce da giorni con `GuadagnoInsufficiente(61.009, 164.662)`: chiudiamo
161.540 $ di debito, prendiamo 76,57 WETH (171.199 $) e dopo la vendita in
cassa ne restano 61.009. Una perdita del 64% sulla coppia piu' liquida di
Ethereum -- mentre la pool Uniswap v3 allo 0,05% su quella stessa taglia
rende il 100,27%, verificato col quoter in catena.

Non era il mercato. Erano due cose nostre che si sommavano:
  1. chiediamo la rotta a Paraswap con SCIVOLAMENTO_BP = 9000, cioe' il 90%
     di tolleranza. La scelta era deliberata e il ragionamento giusto -- la
     difesa vera sta nel contratto, e un pacchetto annullato non costa --
     ma nessuno aveva visto il costo: con quella tolleranza accettiamo
     QUALUNQUE esecuzione, anche una che perde due terzi.
  2. non confrontavamo MAI la risposta col valore giusto. Una rotta che
     rende il 36% e una che rende il 100% ci sembravano la stessa cosa.
E il risultato peggiore non e' perdere soldi -- la guardia del contratto ci
salva -- e' RIFIUTARE l'occasione intera invece di perdere due punti. Il modo
piu' stupido di perdere: la macchina funziona e si dice no da sola.

LA REGOLA, scritta qui perche' qui si decide: un preventivo si misura contro
il pari valore dell'oracolo, e se recupera meno della soglia si CERCA
ALTROVE invece di accettarlo. Tre fonti, si prende la migliore.

Non stringo lo scivolamento: gli scambi si annullerebbero e perderemmo in un
altro modo. Si cambia SEDE, non tolleranza.
"""
import json, os, sys, urllib.error, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

D = "data/liquidazioni"
SOGLIA_RECUPERO = 0.97      # sotto questo si cerca altrove
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
_PREZZI = {"quando": 0.0, "d": {}}
# CHI HA VINTO, E QUANTO RENDE. Lo registra chi SCEGLIE, non chi quota.
# Errore mio del 7/11, dentro il controllo che avevo appena scritto per non
# ripeterlo: leggevo la resa dal registro di vendita_uniswap mentre la sede
# scelta era 1inch, e il controllo diceva "rende 0,01%" su una rotta che
# rende il 99,67%. Misurare lo stadio sbagliato e' la mia famiglia di errori
# piu' frequente, e ci ricasco anche negli strumenti che la sorvegliano.
# Un numero porta il nome di CHI lo ha prodotto, sempre.
ULTIMA_SCELTA = {"chi": None, "uscita": None, "recupero": None}


def segna_scelta(chi, src, dst, q, uscita):
    ULTIMA_SCELTA.update({"chi": chi, "uscita": uscita,
                          "recupero": recupero(src, dst, q, uscita)})


def _prezzi():
    """i prezzi dell'oracolo, ricaricati se il file e' cambiato"""
    try:
        m = os.path.getmtime(f"{D}/prezzi_oracolo.json")
        if m != _PREZZI["quando"]:
            _PREZZI["d"] = json.load(open(f"{D}/prezzi_oracolo.json"))
            _PREZZI["quando"] = m
    except Exception:
        pass
    return _PREZZI["d"]


def pari_valore(src, dst, q):
    """quanto dovremmo ottenere ai prezzi dell'oracolo, in unita' di dst.
    None se non sappiamo un prezzo: allora NON si giudica la rotta, perche'
    un giudizio senza metro e' peggio di nessun giudizio."""
    p = _prezzi()
    a = p.get(src.lower())
    b = p.get(dst.lower())
    if not a or not b or not a.get("prezzo_usd") or not b.get("prezzo_usd"):
        return None
    usd = q / 10 ** a["decimali"] * a["prezzo_usd"]
    return int(usd / b["prezzo_usd"] * 10 ** b["decimali"])


def recupero(src, dst, q, uscita):
    """la frazione del pari valore che quella rotta ci rende. None se non
    si puo' misurare."""
    pv = pari_valore(src, dst, q)
    if not pv or not uscita:
        return None
    return uscita / pv


def da_1inch(src, dst, q, destinatario, scivolamento_pct=1.0):
    """(sede, calldata, uscita_attesa) da 1inch, oppure (None, motivo, None).

    Chiede /swap e non /quote, perche' serve la calldata eseguibile. Usa
    `disableEstimate` perche' il nostro contratto non possiede ancora i
    gettoni nel momento in cui chiediamo.
    NB: serve l'intestazione da browser, altrimenti Cloudflare risponde 1010
    e sembra un problema di chiave (misurato il 7/11).
    """
    try:
        import chiavi
        k = chiavi.uno_inch()
    except Exception:
        k = None
    if not k:
        return None, "nessuna chiave 1inch", None
    u = (f"https://api.1inch.dev/swap/v6.0/1/swap?src={src}&dst={dst}"
         f"&amount={q}&from={destinatario}&origin={destinatario}"
         f"&slippage={scivolamento_pct}&disableEstimate=true")
    try:
        r = urllib.request.urlopen(urllib.request.Request(
            u, headers={"Authorization": f"Bearer {k}",
                        "accept": "application/json",
                        "User-Agent": UA}), timeout=12)
        d = json.load(r)
        tx = d.get("tx") or {}
        return tx.get("to"), tx.get("data"), int(d.get("dstAmount") or 0)
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}", None
    except Exception as e:
        return None, str(e)[:60], None


def giudica(src, dst, q, uscita, chi):
    """stampa e ritorna il verdetto su una rotta. Serve a NON far passare in
    silenzio una rotta che perde: il silenzio e' come l'abbiamo perso."""
    rec = recupero(src, dst, q, uscita)
    if rec is None:
        return None, f"{chi}: recupero non misurabile (prezzo mancante)"
    return rec, f"{chi}: recupera {rec*100:.2f}%"


if __name__ == "__main__":
    WETH = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
    USDT = "0xdac17f958d2ee523a2206206994597c13d831ec7"
    C = "0xF76ec682dd8271788755117e83A1F681b84a43be"
    q = 76_710_673_322_427_744_256
    print("   il caso che faceva fallire la prova: 76,71 WETH -> USDT")
    pv = pari_valore(WETH, USDT, q)
    print(f"   pari valore all'oracolo: {pv/1e6:,.0f} USDT")
    sede, dati, uscita = da_1inch(WETH, USDT, q, C)
    if sede:
        rec, msg = giudica(WETH, USDT, q, uscita, "1inch")
        print(f"   1inch: sede {sede[:12]}, uscita {uscita/1e6:,.0f} USDT, "
              f"{msg}")
    else:
        print(f"   1inch non ha risposto: {dati}")
    print(f"   quello che facevamo noi: 61.009 USDT = "
          f"{61_009/(pv/1e6)*100:.2f}%")
