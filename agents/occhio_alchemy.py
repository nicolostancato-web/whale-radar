#!/usr/bin/env python3
"""IL SECONDO OCCHIO SULLA GARA, e il primo che ci manda SOLO cio' che serve.

Perche' esiste (misurato il 7/11). Censimento di 30 indirizzi websocket
gratuiti col criterio giusto -- consegna un dizionario col campo `input`? --
ne passa UNO SOLO: publicnode. drpc accetta la richiesta di transazioni
intere, non da' errore, e manda hash (25.333 messaggi in 34 minuti, zero
utili); tenderly era muta. E il secondo nome di publicnode risolve agli
stessi due indirizzi IP, quindi era UN fornitore, non due.
Un fornitore solo, caduto 2 volte in 5 ore, sull'unica cosa che decide se
vinciamo.

Alchemy fa una cosa che nessuna porta gratuita fa: filtra **lato server** per
indirizzo di destinazione. Cambia tre cose insieme:
  1. e' un secondo fornitore indipendente;
  2. ci manda ~35 messaggi l'ora invece di ~43.000, quindi togliamo dal
     processo il lavoro che gli stava mangiando il filo caldo (e' la stessa
     causa che faceva costare 84-304 ms la composizione di un pacchetto);
  3. arriva gia' filtrato, quindi non c'e' niente da scartare.

=========================  LE TRE REGOLE  =========================
Non sono precauzioni: sono la differenza fra €0 e €780 al mese.

1. IL FILTRO `toAddress` E' OBBLIGATORIO.
   Senza filtro il piano gratuito salta di seicento volte: 12 messaggi al
   secondo = ~31 milioni al mese x 40 CU = 1,24 MILIARDI di CU, cioe'
   ~$640/mese (~€780 con IVA) a $0,52 per milione.
   E' identico allo schema dei €77,51 di Google Places: un "gratis fino a
   tanto" dove un parametro dimenticato moltiplica il consumo.
   Percio' qui non c'e' un ramo che possa girare senza filtro: se la lista
   degli indirizzi e' vuota, questo modulo SI RIFIUTA di sottoscrivere.
   Non e' un ripiego, e' un rifiuto -- un ripiego silenzioso su una cosa che
   costa soldi e' esattamente come si bruciano €77.

2. NESSUNA CARTA sull'account, cosi' il tetto e' fisico e non una promessa.

3. SI CONTA QUELLO CHE SI CONSUMA, a byte, e si urla al 50% del gratuito.
   Un consumo che non si misura e' un addebito che si scopre a fine mese.
===================================================================
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chiavi
from occhio_ws import Ws

D = "data/liquidazioni"
CONSUMO = f"{D}/consumo_alchemy.json"
CU_PER_BYTE = 0.04          # tariffa ufficiale verificata il 7/11/2026
GRATUITO_CU_MESE = 30_000_000
ALLARME = 0.50              # si urla a meta' del gratuito


def destinatari():
    """gli indirizzi a cui arrivano le campanelle, dal NOSTRO registro.
    Non si indovinano e non si scrivono a mano: si leggono da cio' che
    abbiamo visto arrivare davvero."""
    import collections
    c = collections.Counter()
    try:
        for riga in open(f"{D}/sentinella.jsonl"):
            try:
                d = json.loads(riga)
            except ValueError:
                continue
            if d.get("verso"):
                c[str(d["verso"]).lower()] += 1
    except OSError:
        return []
    return [a for a, _ in c.most_common()]


def _leggi_consumo():
    try:
        return json.load(open(CONSUMO))
    except Exception:
        return {"mese": time.strftime("%Y-%m"), "byte": 0, "messaggi": 0}


def _salva_consumo(c):
    try:
        t = CONSUMO + ".tmp"
        json.dump(c, open(t, "w"), indent=1)
        os.replace(t, CONSUMO)
    except Exception:
        pass


def stato_consumo():
    """(cu_consumate, frazione_del_gratuito, messaggi) nel mese corrente."""
    c = _leggi_consumo()
    if c.get("mese") != time.strftime("%Y-%m"):
        return 0.0, 0.0, 0
    cu = c.get("byte", 0) * CU_PER_BYTE
    return cu, cu / GRATUITO_CU_MESE, c.get("messaggi", 0)


def ascolta(quando_senti, ferma=None, indirizzi=None):
    """Apre la sottoscrizione FILTRATA e chiama quando_senti(tx, 'alchemy').

    Si rifiuta di partire senza chiave o senza indirizzi: vedi regola 1.
    """
    k = chiavi.alchemy()
    if not k:
        raise OSError("chiave Alchemy assente nel file delle credenziali "
                      "(sezione === ALCHEMY ===): non sottoscrivo")
    ind = indirizzi if indirizzi is not None else destinatari()
    if not ind:
        raise OSError("NESSUN indirizzo da filtrare: mi RIFIUTO di "
                      "sottoscrivere senza filtro, perche' il mempool intero "
                      "costerebbe ~$640 al mese invece di zero")
    attesa = 2
    while not (ferma and ferma()):
        w = None
        try:
            w = Ws(f"wss://eth-mainnet.g.alchemy.com/v2/{k}")
            w.manda(json.dumps({
                "jsonrpc": "2.0", "id": 1, "method": "eth_subscribe",
                "params": ["alchemy_pendingTransactions",
                           {"toAddress": ind, "hashesOnly": False}]}))
            vissuto = time.time()
            c = _leggi_consumo()
            if c.get("mese") != time.strftime("%Y-%m"):
                c = {"mese": time.strftime("%Y-%m"), "byte": 0,
                     "messaggi": 0}
            ultimo_salvataggio = 0.0
            while not (ferma and ferma()):
                try:
                    m = w.ricevi()
                except TimeoutError:
                    continue                 # le campanelle sono rare
                if not m:
                    continue
                c["byte"] += len(m)
                c["messaggi"] += 1
                if time.time() - ultimo_salvataggio > 30:
                    _salva_consumo(c)
                    ultimo_salvataggio = time.time()
                try:
                    r = json.loads(m)
                except ValueError:
                    continue
                if r.get("id") == 1:
                    if r.get("error"):
                        raise OSError(str(r["error"])[:140])
                    continue
                tx = (r.get("params") or {}).get("result")
                if not isinstance(tx, dict) or "input" not in tx:
                    continue
                quando_senti(tx, "alchemy")
                if time.time() - vissuto > 120:
                    attesa = 2
        except Exception as e:
            print(f"   ALCHEMY CADUTA: {str(e)[:90]}")
            time.sleep(attesa)
            attesa = min(300, attesa * 2)
        finally:
            if w:
                try:
                    w.chiudi()
                except Exception:
                    pass


if __name__ == "__main__":
    cu, fr, msg = stato_consumo()
    ind = destinatari()
    print(f"   indirizzi nel filtro: {len(ind)}")
    print(f"   chiave Alchemy: "
          f"{'presente' if chiavi.alchemy() else 'ASSENTE'}")
    print(f"   consumo del mese: {cu:,.0f} CU su {GRATUITO_CU_MESE:,} "
          f"({fr*100:.2f}% del gratuito), {msg} messaggi")
    if fr >= ALLARME:
        print("   <<< OLTRE META' DEL GRATUITO: controllare prima di "
              "arrivare al tetto")
    secondi = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    if secondi:
        t0 = time.time()
        visti = []
        ascolta(lambda tx, _p: visti.append(tx),
                ferma=lambda: time.time() - t0 > secondi or len(visti) >= 5)
        print(f"   in {time.time()-t0:.0f}s: {len(visti)} campanelle")
