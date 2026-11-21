"""Posizione per posizione, ma solo per i candidati vincenti.

PERCHE' SERVE (4/10). La tabella dei guadagni e' AGGREGATA: «8,4X su cinque posizioni chiuse»
puo' essere cinque volte 8X oppure quattro pareggi e un colpo da 40X. Sono due cose opposte:
la prima e' bravura ripetuta, la seconda e' fortuna. Con l'aggregato non si distinguono, e il
criterio di Nicolo' e' proprio il multiplo RIPETUTO.

Tenere il dettaglio per tutti costerebbe un file enorme (130.586 persone x decine di pool). Per
99 candidati non costa niente. Quindi: lista stretta, dettaglio pieno.

IL FILTRO DELLA DIMENSIONE, E PERCHE' (4/10). Multiplo e importo sono inversamente correlati:
su base chi ha fatto oltre 50X ha speso 4 dollari MEDIANI. Un 100X su quattro dollari fa
quattrocento dollari — non e' informazione, e' rumore, ed e' la stessa polvere delle flotte
(263-1.120$ il 3/10). Chi sa davvero AUMENTA LA POSTA. Per questo i candidati devono avere
multiplo alto E importo non-polvere E piu' di una posizione chiusa.

COSTA ZERO CHIAMATE: legge i file degli scambi che abbiamo gia'.
"""
import glob
import gzip
import json
import os
import sys
import time

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import a_fette as AF                                              # noqa: E402
import verso as V                                                 # noqa: E402

CHAIN = os.environ.get("CHAIN", "base")
BUDGET = int(os.environ.get("BUDGET_SEC", 600))
BASE = f"data/multichain/{CHAIN}"
CARTELLE = ("storico", "vivo", "trades")
LISTA = "data/candidati_vincenti.json"


def main():
    if not os.path.exists(LISTA):
        raise SystemExit(f"DETTAGLIO | manca {LISTA}: la lista dei candidati la costruisce "
                         f"agents/chi_incassa.py. Senza lista non si scansiona niente.")
    # LA CORSIA DICHIARA QUALE VERSIONE DELLA LISTA HA LETTO (4/10). Ho pubblicato una lista
    # nuova (99 candidati + 300 di controllo) e lanciato la corsia due minuti dopo: la corsia
    # prende `main`, dove la lista nuova non era ancora arrivata, e ha girato sulla VECCHIA.
    # Il gruppo di controllo e' tornato a zero e per un momento ho creduto a un difetto del
    # codice. Non si vedeva perche' nessuno stampava COSA aveva letto.
    # IN POSITIVO: si stampa quanti indirizzi e l'impronta del file. Un numero che non torna
    # si vede subito, e «ha girato sulla versione sbagliata» smette di somigliare a un bug.
    import hashlib
    grezzo = open(LISTA, "rb").read()
    cand = set(x.lower() for x in json.loads(grezzo)["da"].get(CHAIN, []))
    print(f"DETTAGLIO | lista: {len(cand)} indirizzi per {CHAIN}, impronta "
          f"{hashlib.sha256(grezzo).hexdigest()[:12]}", flush=True)
    if not cand:
        print(f"DETTAGLIO | {CHAIN}: nessun candidato in lista, non c'e' niente da guardare")
        return
    p = f"{BASE}/iniziatori.json.gz"
    if not os.path.exists(p):
        raise SystemExit(f"DETTAGLIO | manca {p}: senza sapere chi ha firmato non conto niente")
    mappa = {k.lower(): v.lower() for k, v in
             json.load(gzip.open(p, "rt")).get("da", {}).items()
             if str(v).lower() in cand}
    verso = V.carica(CHAIN)
    print(f"DETTAGLIO | {CHAIN}: {len(cand)} candidati, {len(mappa):,} loro transazioni note, "
          f"{len(verso):,} pool col verso noto", flush=True)

    file_tutti = []
    for c in CARTELLE:
        file_tutti += sorted(glob.glob(os.path.join(BASE, c, "*.jsonl.gz")))
    file_tutti = AF.mia_parte(file_tutti)
    i_f, n_f = AF.quale_fetta()
    print(f"   fetta {i_f+1}/{n_f}: {len(file_tutti):,} file", flush=True)

    t0, letti, posizioni = time.time(), 0, {}
    for percorso in file_tutti:
        if time.time() - t0 >= BUDGET:
            print(f"   budget speso dopo {letti:,} file letti: salvo quello che ho",
                  flush=True)
            break
        pool = os.path.basename(percorso).split(".")[0]
        vp = V.valuta_lato(CHAIN, pool)
        if not vp:
            continue
        lato, decimali, in_dollari = vp
        # QUALE valuta e' questo pool: un rapporto ha senso solo fra quantita' della stessa cosa
        valuta_qui = V.indirizzo_valuta(CHAIN, pool, lato)
        try:
            righe = [json.loads(l) for l in gzip.open(percorso, "rt") if l.strip()]
        except Exception:
            continue
        letti += 1
        qui = {}
        for x in righe:
            chi = mappa.get(str(x.get("tx", "")).lower())
            if not chi:
                continue
            q = V.quantita_lato(x, lato)
            if q <= 0:
                continue
            dollari = (q / (10 ** decimali)) * in_dollari
            if dollari > 1_000_000:          # unita' sbagliate, non affari (3/10)
                continue
            meme = "t1" if lato == "t0" else "t0"
            gettoni = V.quantita_lato(x, meme)
            # OGNI POSIZIONE SI PORTA DIETRO LA SUA PROVA (6/10). Il cancello precedente
            # cercava i gettoni nel portafoglio e bocciava 10 casi su 10, perche' in un
            # mercato automatico il gettone va al DESTINATARIO dello scambio — un router o un
            # contratto del bot — e mai al firmatario. Un controllo che boccia tutto e' rotto.
            # La prova che funziona e' un'altra: conservare gli HASH DELLE TRANSAZIONI che
            # compongono la posizione. Allora verificare non richiede ipotesi su chi controlla
            # quale contratto: si chiede alla chain se quella transazione esiste, chi l'ha
            # firmata, e in quale pool ha scambiato. Due chiamate, nessuna interpretazione.
            # E' anche la prova che Nicolo' puo' rifare a mano senza fidarsi di noi.
            # LA QUANTITA' DI VALUTA, NON SOLO IL SUO VALORE IN DOLLARI (6/10, mandato di
            # Nicolo'). Per dire «ha messo tot e ha portato a casa tot» serve un rapporto, e un
            # rapporto fra dollari richiede un PREZZO — che oggi mi ha quasi fatto scrivere una
            # cifra sbagliata due volte (16 milioni inesistenti il 3/10, e una somma di importi
            # in 72 valute diverse stamattina).
            # Ma la curva si paga nella valuta della chain e il pool paga nella stessa valuta:
            # quindi il multiplo e' un RAPPORTO PURO fra quantita' della stessa cosa. Zero
            # prezzi, zero conversioni, zero modo di sbagliare le unita'.
            # `dollari` resta, perche' serve altrove; `vin`/`vout` sono la quantita' vera.
            quanta_valuta = q / (10 ** decimali)
            d = qui.setdefault(chi, {"compra": 0.0, "vende": 0.0, "gin": 0.0, "gout": 0.0,
                                     "vin": 0.0, "vout": 0.0,
                                     "primo": None, "ultimo": None, "scambi": 0,
                                     "tx_compra": [], "tx_vende": [],
                                     # I TEMPI SEPARATI PER LATO (6/10). Verificando a mano un
                                     # caso ho scoperto che il portafoglio aveva VENDUTO alle
                                     # 20:40 e COMPRATO alle 02:12 del giorno dopo: ha venduto
                                     # prima di comprare, quindi i gettoni venduti venivano da
                                     # altrove e il rapporto incassato/speso non e' un
                                     # rendimento. Con un solo `primo` e un solo `ultimo` quella
                                     # inversione era invisibile — e io avevo perfino stampato
                                     # le due date scambiate, credendo che `primo` fosse
                                     # l'acquisto.
                                     "t_compra": None, "t_vende": None})
            _h = str(x.get("tx", ""))
            # IL TEMPO SI LEGGE PRIMA DI USARLO (6/10). Avevo aggiunto l'uso di `tt` nei due
            # rami compra/vende, ma `tt` veniva letto QUATTRO RIGHE DOPO: il file compilava e
            # si schiantava all'esecuzione con NameError, uccidendo tutta la corsia.
            # E' la lezione che ho scritto io stesso tre ore prima, sul residuo di `atomiche`:
            # «un file che compila non e' un file che gira». Scriverla non basta: va ESEGUITA
            # almeno una volta sul percorso che si e' toccato — un controllo che non attraversa
            # il ramo modificato rassicura invece di controllare (lezione del 2/10).
            tt = x.get("ts") or x.get("t")
            if V.entra_valuta(x, lato):
                d["compra"] += dollari
                d["vin"] += quanta_valuta
                d["gin"] += gettoni
                if _h and len(d["tx_compra"]) < 3:
                    d["tx_compra"].append(_h)
                if isinstance(tt, (int, float)):
                    d["t_compra"] = tt if d["t_compra"] is None else min(d["t_compra"], tt)
            else:
                d["vende"] += dollari
                d["vout"] += quanta_valuta
                d["gout"] += gettoni
                if _h and len(d["tx_vende"]) < 3:
                    d["tx_vende"].append(_h)
                if isinstance(tt, (int, float)):
                    d["t_vende"] = tt if d["t_vende"] is None else max(d["t_vende"], tt)
            d["scambi"] += 1
            if tt:
                d["primo"] = tt if d["primo"] is None else min(d["primo"], tt)
                d["ultimo"] = tt if d["ultimo"] is None else max(d["ultimo"], tt)
        for chi, d in qui.items():
            residuo = d["gin"] - d["gout"]
            chiuso = d["gin"] > 0 and residuo <= 0.01 * d["gin"] and d["vende"] > 0
            stato = ("chiuso" if chiuso else
                     "solo_uscite" if d["compra"] <= 0 < d["vende"] else
                     "parziale" if d["vende"] > 0 else "aperto")
            posizioni.setdefault(chi, {})[pool] = {
                "stato": stato, "speso": round(d["compra"], 2),
                # la valuta in QUANTITA' e il suo nome: non si sommano mai valute diverse
                "vin": d["vin"], "vout": d["vout"], "valuta": valuta_qui,
                "incassato": round(d["vende"], 2), "scambi": d["scambi"],
                "primo": d["primo"], "ultimo": d["ultimo"],
                # il multiplo si scrive SOLO se la posizione e' chiusa: su una aperta
                # sarebbe un prezzo marginale travestito da incasso
                "multiplo": (round(d["vende"] / d["compra"], 3)
                             if chiuso and d["compra"] > 0 else None),
                # la prova, per il controllo a mano e per il cancello
                "tx_compra": d["tx_compra"], "tx_vende": d["tx_vende"],
                # i tempi per lato e i gettoni: senza questi, «ha venduto prima di comprare»
                # resta invisibile e un rapporto senza senso passa per un rendimento
                "t_compra": d["t_compra"], "t_vende": d["t_vende"],
                "gin": d["gin"], "gout": d["gout"],
                "ordine_sano": (d["t_compra"] is not None and d["t_vende"] is not None
                                and d["t_compra"] <= d["t_vende"])}
            # UN MULTIPLO ASSURDO SI METTE IN QUARANTENA, NON IN MEDIA (4/10). Nel primo
            # giro e' comparso un 3.357.362.275.439.169X: tre milioni di miliardi, dentro una
            # mediana. E' la stessa famiglia dei 16 milioni di dollari del 2/10 — un lato
            # valuta o dei decimali sbagliati — e il guardiano sui dollari per scambio non lo
            # fermava, perche' il rapporto puo' esplodere anche con due importi piccoli.
            # Oltre 1000X su una memecoin appena nata non e' un affare: e' un'unita' sbagliata.
            # Si segna e si conta a parte, cosi' chi legge sa che c'e' e non la somma.
            z = posizioni[chi][pool]
            if z["multiplo"] is not None and z["multiplo"] > 1000:
                z["sospetto"] = "multiplo oltre 1000X: unita' probabilmente sbagliata"
    pezzo = AF.nome_pezzo(BASE, "dettaglio_candidati")
    json.dump(posizioni, open(pezzo, "w"))
    chiuse = sum(1 for v in posizioni.values() for z in v.values() if z["stato"] == "chiuso")
    print(f"   {len(posizioni)} candidati trovati, {sum(len(v) for v in posizioni.values()):,} "
          f"posizioni di cui {chiuse:,} chiuse, da {letti:,} file", flush=True)


if __name__ == "__main__":
    main()
