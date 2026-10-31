"""GLI SCAMBI DEI POOL DIPLOMATI: la materia prima della prova del ritardo.

== PERCHE' SOLO GLI SCAMBI, E NON SUBITO I PORTAFOGLI (19/10, indicazione di Grok) ==

La tabella dei portafogli e' il lavoro da una settimana. Prima si fa quello da un giorno, che
puo' renderla inutile: dopo che QUALCUNO compra, resta ancora abbastanza movimento da coprire
il costo del giro? Se no, non esiste portafoglio al mondo che renda la copia redditizia,
perche' copiando possiamo prendere solo quel movimento li'. Questo file raccoglie esattamente
cio' che serve a rispondere, e nient'altro.

== IL TRACCIATO, LETTO E NON ASSUNTO (lezione pagata stamattina) ==

Swap(PoolId indexed id, address indexed sender, ...), dato a 6 parole:
  [0] amount0 CON SEGNO = il nativo, dal punto di vista del POOL (positivo = entra nel pool,
      cioe' qualcuno COMPRA gettoni)
  [1] amount1 CON SEGNO = i gettoni
  [2] sqrtPriceX96 subito DOPO lo scambio  <- il campo che rende calcolabile la copia
  [3] liquidita'    [4] tick    [5] fee, che su questi pool vale ZERO
Il costo vero non sta nel campo fee: l'hook di Pons preleva dal delta (~1%) e sopra c'e' la
tassa del creatore. Sottrarre il campo fee significa sottrarre nulla.

Costo: zero. RPC pubblico, filtro su indirizzo del gestore + id del pool nel secondo topic.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as C

GESTORE_V4 = "0x8366a39cc670b4001a1121b8f6a443a643e40951"
T_SWAP = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
DENTRO = "data/multichain/robinhood/manifesto_graduati.json"
# MAI IN CODA A UN FILE COMPRESSO (19/10, errore gia' scritto in memoria e rifatto lo stesso).
# Un .gz aperto in append diventa illeggibile PER INTERO se il processo si ferma a meta': il
# lettore muore con «ended before the end-of-stream marker». Si scrive in chiaro, che tollera
# l'interruzione riga per riga, e si comprime alla fine quando il file e' chiuso.
FUORI = "data/multichain/robinhood/scambi_postdiploma.jsonl"
FATTE = "data/multichain/robinhood/scambi_postdiploma_fatte.json"
# tre lavoratori su fette disgiunte: ognuno il suo file, si uniscono alla fine
FETTA = int(os.environ.get("FETTA", "0"))
FETTE = int(os.environ.get("FETTE", "1"))
# LA FINESTRA E' UN TAGLIO DICHIARATO (19/10, misurato non assunto). Con 10 milioni di
# blocchi un pool costa 15,2s; con 400.000 costa 5,0s e contiene gia' l'88% degli scambi
# (27.297 contro 24.000 su quattro pool a caso). 400.000 blocchi sono 10,3 ore dopo il
# diploma: dentro ci sta tutto quello che serve alla prova del ritardo, che guarda al
# massimo un'ora in avanti. Il 12% che resta fuori e' coda lontana, e va DETTO, non taciuto.
FINESTRA = int(os.environ.get("FINESTRA", "400000"))


def _segno(v):
    return v - (1 << 256) if v >= (1 << 255) else v


def scambi(idp, da):
    lg = C.log_di_finestra(T_SWAP, da, da + FINESTRA, indirizzo=GESTORE_V4, secondo=idp)
    if lg is None:
        return None
    r = []
    for l in lg:
        d = l["data"][2:]
        if len(d) < 64 * 3:
            continue
        a0 = _segno(int(d[0:64], 16)) / 1e18
        a1 = _segno(int(d[64:128], 16)) / 1e18
        sq = int(d[128:192], 16)
        r.append([int(l["blockNumber"], 16), a0, a1, sq])
    r.sort(key=lambda x: x[0])
    return r


def main():
    man = json.load(open(DENTRO))["pool"]
    # solo i pool quotati in NATIVO: sugli altri gli importi non sono confrontabili
    nativi = {k: v for k, v in man.items() if int(v["valuta"], 16) == 0}
    mia = FUORI.replace(".jsonl", f"_{FETTA}.jsonl")
    miaf = FATTE.replace(".json", f"_{FETTA}.json")
    nativi = {k: v for i, (k, v) in enumerate(nativi.items()) if i % FETTE == FETTA}
    fatte = json.load(open(miaf)) if os.path.exists(miaf) else {}
    f = open(mia, "a")
    n = vuoti = rifiutati = 0
    t0 = time.time()
    for idp, v in nativi.items():
        if idp in fatte:
            continue
        r = scambi(idp, v["diploma"])
        if r is None:
            rifiutati += 1
            # UN RIFIUTO NON E' UNO ZERO: non lo segno come fatto, si riprende al giro dopo
            continue
        if not r:
            vuoti += 1
        f.write(json.dumps({"pool": idp, "moneta": v["moneta"], "diploma": v["diploma"],
                            "s": r}) + "\n")
        fatte[idp] = len(r)
        n += 1
        if n % 50 == 0:
            f.flush()
            json.dump(fatte, open(miaf, "w"))
            vel = n / max(1e-9, time.time() - t0)
            print(f"SCAMBI | {len(fatte)}/{len(nativi)} pool, {sum(fatte.values()):,} scambi, "
                  f"{vel*60:.0f}/min, rifiutati {rifiutati}, senza scambi {vuoti}", flush=True)
        time.sleep(0.2)
    f.close()
    json.dump(fatte, open(miaf, "w"))
    print(f"SCAMBI | finito: {len(fatte)}/{len(nativi)} pool, {sum(fatte.values()):,} scambi, "
          f"{rifiutati} rifiutati, {vuoti} senza scambi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
