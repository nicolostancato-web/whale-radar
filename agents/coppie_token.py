"""COPPIE DI TOKEN — chi sono i due lati di ogni pool. Condizione 6.

PERCHE' MANCAVA. Ogni record dice quanto e' entrato e quanto e' uscito (a0, a1) ma non DI COSA.
Senza la coppia, «a0 = 13497419610956700000000» e' un numero senza unita': non si sa se e' un
memecoin o la valuta con cui lo si compra, e nemmeno con quante cifre decimali va letto. La
condizione 6 chiede il 100% dei record mappati. Eravamo a ZERO, e nessun raccoglitore la prendeva.

DUE MONDI DIVERSI, perche' i pool non hanno tutti la stessa forma:

- **pool con indirizzo** (V2/V3, 42 caratteri): il contratto e' li' e risponde. Si chiedono
  `token0()` e `token1()` e si e' finito. Sono la minoranza: 300 su 1910 su base.

- **pool con id** (V4, 66 caratteri): la maggioranza. Qui il pool NON e' un contratto — vive dentro
  un contratto solo, il PoolManager, e l'identita' e' un id. Non c'e' niente da interrogare.
  L'identita' esiste in un posto solo: l'evento `Initialize` emesso alla creazione, che porta nei
  topics [firma, id, currency0, currency1]. Firma scoperta sul campo, non presa da un tutorial:
      0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438
  (trovata cercando TUTTI i log che nominassero un pool V4 noto prima del suo primo scambio.)

QUANTO COSTA. L'evento Initialize e' raro, quindi il filtro e' selettivo e il nodo regge intervalli
enormi: misurato su robinhood, **500.000 blocchi in 1,8 secondi, 6.471 pool mappati in un colpo**.
L'intera catena sta in ~128 chiamate. Base e' piu' lenta e vuole intervalli piu' stretti.

PERCHE' UNA TABELLA E NON UN CAMPO DENTRO OGNI RECORD. La coppia e' una proprieta' del POOL, non
dello scambio: e' identica per tutti i 300 scambi di quel pool. Scriverla dentro ogni record
significherebbe riscrivere 250 mila righe per ripetere 2.700 informazioni, e rifarlo a ogni
correzione. Qui sta in un posto solo, si aggiorna in un posto solo, e ogni record ci arriva dal
suo campo `pool`. Se domani scopriamo che una coppia era sbagliata, si corregge una riga.
"""
import glob as _g
import gzip
import json
import sys
import os
import time
import urllib.request

INIT = "0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
TOKEN0 = "0x0dfe1681"      # token0()
TOKEN1 = "0xd21220a7"      # token1()
# QUANTO REGGE OGNI NODO, MISURATO (16/09). Non si indovina: si prova e si scrive.
#   robinhood: 500.000 blocchi in 1,8s — 6.471 Initialize in un colpo solo
#   base     : 2.000 blocchi in 1,5s; a 5.000 risponde 413 «troppo grande». Limite netto.
# Avevo messo 100.000 anche per base: cinquanta volte oltre il suo limite. Falliva SEMPRE,
# dimezzava fino al fondo e poi saltava i tratti — ed e' per questo che base era ferma al
# 3% mentre robinhood volava. Non era il nodo lento: era una mia costante sbagliata che si
# mascherava da nodo lento.
RPC = {"base": ("https://mainnet.base.org", 2_000),
       "robinhood": ("https://rpc.mainnet.chain.robinhood.com", 500_000)}
CHAIN = os.environ.get("CHAIN", "robinhood")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chiamata as C

BUDGET = int(os.environ.get("BUDGET_SEC", 600))
# OGNI FETTA SCRIVE IL SUO FILE (18/09). Misurato: il nodo pubblico limita per INDIRIZZO IP, non
# per connessione — un filo solo rende 0,24 pool/s, tre fili 0,22, sei fili zero. Da una macchina
# sola non si va piu' veloci, e a base restano 4.349 indirizzi: cinque ore di chiamate pure.
# Ma ogni lavoro di GitHub gira su un runner con IP proprio. Quindi la velocita' si compra in
# PARALLELO fra lavori, non in parallelo dentro un lavoro — la stessa leva gia' usata per lo scavo
# storico. Ogni fetta prende i pool il cui nome finisce in una certa classe, e scrive solo il suo
# file; l'unione la fa coppie_unisci.py.
FETTA = os.environ.get("FETTA")
N_FETTE = int(os.environ.get("N_FETTE", 4))
BASE_OUT = f"data/multichain/{CHAIN}/coppie.json"
OUT = (f"data/multichain/{CHAIN}/coppie_f{FETTA}.json" if FETTA is not None else BASE_OUT)


def mia(pool):
    """True se questo pool tocca a questa fetta. Senza fetta, tocca tutto a noi."""
    if FETTA is None:
        return True
    return int(pool[-6:], 16) % N_FETTE == int(FETTA)
t0 = time.time()


def rpc(url, metodo, params, tentativi=3, to=120):
    b = json.dumps({"jsonrpc": "2.0", "method": metodo, "params": params, "id": 1}).encode()
    attesa = 3
    for k in range(tentativi):
        try:
            r = urllib.request.Request(url, data=b, headers={"Content-Type": "application/json",
                                                             "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=to) as x:
                d = json.load(x)
            if "error" in d:
                return None, str(d["error"])[:70]
            return d.get("result"), None
        except Exception as e:
            if k < tentativi - 1:
                time.sleep(attesa)
                attesa *= 2
                continue
            return None, f"{type(e).__name__} {getattr(e, 'code', '')}"
    return None, "tentativi esauriti"


def main():
    url, ampiezza = RPC.get(CHAIN, (None, None))
    if not url:
        print(f"COPPIE | {CHAIN}: nessun nodo", flush=True)
        return
    rf = f"data/multichain/{CHAIN}/righe.json"
    if not os.path.exists(rf):
        print(f"COPPIE | {CHAIN}: manca righe.json", flush=True)
        return
    voluti = {k.lower() for k in json.load(open(rf)).get("pool", {})}
    # ANCHE I POOL DEL CENSIMENTO, NON SOLO I NOSTRI (18/09). La definizione proposta di «cosa
    # stiamo studiando» ha bisogno della coppia di token per decidere se un pool entra: una valuta
    # di base da un lato, un token qualunque dall'altro. Ma la coppia la conoscevamo solo per il
    # NOSTRO registro — 333 pool su 7.458 attivi, il 4%. Con quel 4% la definizione si puo'
    # scrivere e non usare.
    # Il censimento e' il denominatore vero: e' li' che serve sapere cosa c'e' dentro. Si prendono
    # i pool con almeno SOGLIA scambi, perche' degli altri (il 45% ha un solo scambio) non
    # importa a nessuno.
    soglia = int(os.environ.get("SOGLIA_SCAMBI", 20))
    cf = f"data/multichain/{CHAIN}/censimento.jsonl.gz"
    dal_censimento = 0
    if os.path.exists(cf):
        try:
            for l in gzip.open(cf, "rt"):
                if not l.strip():
                    continue
                d0 = json.loads(l)
                if d0.get("scambi", 0) >= soglia and d0.get("pool"):
                    p_ = d0["pool"].lower()
                    if p_ not in voluti:
                        voluti.add(p_)
                        dal_censimento += 1
        except Exception:
            pass
    if dal_censimento:
        print(f"COPPIE | {CHAIN}: +{dal_censimento} pool dal censimento (>={soglia} scambi)",
              flush=True)
    note = {}
    if os.path.exists(OUT):
        try:
            note = json.load(open(OUT)).get("coppie", {})
        except Exception:
            note = {}
    # I GIA' NOTI SI LEGGONO DA TUTTE LE FETTE (18/09), altrimenti ogni fetta rifarebbe il lavoro
    # delle altre appena l'unione torna indietro.
    for _f in _g.glob(f"data/multichain/{CHAIN}/coppie*.json"):
        if os.path.abspath(_f) == os.path.abspath(OUT):
            continue
        try:
            for _k, _v in (json.load(open(_f)).get("coppie", {}) or {}).items():
                note.setdefault(_k, _v)
        except Exception:
            pass
    manca = {p for p in (voluti - set(note)) if mia(p)}
    v4 = {p for p in manca if len(p) == 66}
    ind = {p for p in manca if len(p) == 42}
    print(f"COPPIE | {CHAIN}: {len(voluti)} pool, {len(note)} gia' noti, "
          f"mancano {len(manca)} ({len(v4)} con id, {len(ind)} con indirizzo)", flush=True)
    if not manca:
        return

    # PRIMA SI GUARDA IN CASA (16/09). Lo scopritore, girando alla punta, registra gia' `t0` e `t1`
    # di ogni pool che nasce: sono nello stesso evento Initialize che leggerebbe questo raccoglitore.
    # Riscansionare la catena per un dato che abbiamo gia' su disco e' lavoro pagato due volte — ed
    # e' il motivo per cui base era ferma al 3%: il suo nodo e' lento e la scansione non arrivava
    # mai abbastanza indietro, mentre l'universo era li' pieno di risposte.
    uni = f"data/multichain/{CHAIN}/universo.jsonl.gz"
    da_casa = 0
    if os.path.exists(uni):
        try:
            for l in gzip.open(uni, "rt"):
                if not l.strip():
                    continue
                try:
                    d0 = json.loads(l)
                except Exception:
                    continue
                pid = (d0.get("pool") or "").lower()
                if pid in manca and pid not in note and d0.get("t0") and d0.get("t1"):
                    note[pid] = {"t0": d0["t0"], "t1": d0["t1"], "dex": 4,
                                 "nato": d0.get("nato"), "acq": int(time.time()),
                                 "fonte": "universo"}
                    da_casa += 1
        except Exception:
            pass
    if da_casa:
        manca = manca - set(note)
        v4 = {p for p in manca if len(p) == 66}
        ind = {p for p in manca if len(p) == 42}
        print(f"COPPIE | {CHAIN}: {da_casa} prese dall'universo senza chiamare nessuno, "
              f"ne restano {len(manca)}", flush=True)
        if not manca:
            _mio = {k: v for k, v in note.items() if mia(k)} if FETTA is not None else note
            json.dump({"acq": int(time.time()), "n": len(_mio), "coppie": _mio}, open(OUT, "w"))
            print(f"COPPIE | {CHAIN}: 100% mappato", flush=True)
            return

    punta, _e = rpc(url, "eth_blockNumber", [])
    if not punta:
        print(f"COPPIE | {CHAIN}: il nodo non risponde", flush=True)
        return
    punta = int(punta, 16)
    trovati = 0

    # --- i pool con id: si leggono dall'evento di creazione, a grandi fette ---
    if v4:
        # IL SEGNALIBRO, ALTRIMENTI SI RIFA' SEMPRE LO STESSO PEZZO (16/09). La scansione
        # all'indietro ripartiva dalla punta a ogni giro: rifaceva i blocchi recenti — dove i pool
        # che ci mancano NON sono, perche' quelli recenti li abbiamo gia' — e non scendeva mai piu'
        # in fondo. Robinhood era piantato al 51% mentre base saliva, e sembrava un problema di
        # chain: era il mio cursore che tornava a casa ogni sera.
        ckf = f"data/multichain/{CHAIN}/coppie_ckpt.json"
        ck = {}
        if os.path.exists(ckf):
            try:
                ck = json.load(open(ckf))
            except Exception:
                ck = {}
        cur = int(ck.get("cur") or punta)
        if cur > punta or cur < 1:
            cur = punta
        # LA QUOTA VA A CHI HA PIU' LAVORO (18/09). Era fissa al 75% per la scansione V4, decisa
        # quando i pool con id erano la maggioranza. Col censimento il rapporto si e' ribaltato: su
        # base restano 1.882 id contro 4.296 indirizzi, e i tre quarti del tempo andavano alla meta'
        # piu' piccola del problema. Adesso ognuna delle due strade riceve in proporzione a quanto
        # le manca, entro limiti che impediscono a una di azzerare l'altra.
        _tot = len(v4) + len(ind)
        _quota = 0.75 if not _tot else min(0.75, max(0.25, len(v4) / _tot))
        while cur > 1 and time.time() - t0 < BUDGET * _quota:
            da = max(1, cur - ampiezza)
            log, err = rpc(url, "eth_getLogs", [{"fromBlock": hex(da), "toBlock": hex(cur),
                                                 "topics": [INIT]}])
            if log is None:
                if ampiezza > 400:
                    ampiezza //= 2       # troppo denso: si stringe, non si salta
                    continue
                print(f"COPPIE | blocchi {da}-{cur} illeggibili: LI STO SALTANDO ({err})", flush=True)
                cur = da - 1
                continue
            for l in log:
                tp = l.get("topics") or []
                if len(tp) < 4:
                    continue
                pid = tp[1].lower()
                if pid not in v4 or pid in note:
                    continue
                note[pid] = {"t0": "0x" + tp[2][-40:], "t1": "0x" + tp[3][-40:],
                             "dex": 4, "nato": int(l["blockNumber"], 16),
                             "acq": int(time.time()), "fonte": "evento-creazione"}
                trovati += 1
            cur = da - 1
            try:
                json.dump({"cur": cur, "acq": int(time.time())}, open(ckf, "w"))
            except Exception:
                pass
            if len(note) >= len(voluti):
                break

    # --- i pool con indirizzo: il contratto risponde da solo, UNO ALLA VOLTA ---
    # HO PROVATO I LOTTI E RENDONO ZERO (18/09). Il JSON-RPC accetta un array di richieste, e il
    # nodo di base lo accetta senza protestare — ma a 40 domande ne risponde TRE, troncando il resto
    # in silenzio. Misurato sugli STESSI 20 indirizzi: a lotti 0 su 20, una alla volta con riprove
    # 18 su 20. Avevo pubblicato i lotti come acceleratore qualche ora prima, e producevano niente.
    # Le riprove servono per un difetto diverso e dimostrato: il nodo risponde "0x" a una eth_call
    # valida quando e' sotto carico, senza segnalare errore. Una domanda sola non basta.
    for p in sorted(ind):
        if time.time() - t0 > BUDGET:
            break
        a, sa = C.eth_call(url, p, TOKEN0, tentativi=3, pausa=0.5, timeout=30)
        b, sb = C.eth_call(url, p, TOKEN1, tentativi=3, pausa=0.5, timeout=30)
        if sa != "ok" or sb != "ok" or len(a) < 42 or len(b) < 42:
            continue                      # non risolto adesso: si riprova al giro prossimo
        note[p] = {"t0": "0x" + a[-40:], "t1": "0x" + b[-40:], "dex": 23,
                   "acq": int(time.time()), "fonte": "contratto"}
        trovati += 1

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # UNA FETTA SCRIVE SOLO I SUOI (18/09): altrimenti ogni file conterrebbe anche il
    # lavoro delle altre, e quattro fette produrrebbero quattro copie dello stesso megabyte.
    _mio = {k: v for k, v in note.items() if mia(k)} if FETTA is not None else note
    json.dump({"acq": int(time.time()), "n": len(_mio), "coppie": _mio,
               "fetta": FETTA}, open(OUT, "w"))
    resta = len(voluti - set(note))
    print(f"COPPIE | {CHAIN}: +{trovati} nuove, {len(note)} note in totale, "
          f"ne mancano {resta} ({100 * (len(voluti) - resta) / max(1, len(voluti)):.0f}% mappato)",
          flush=True)


if __name__ == "__main__":
    main()
