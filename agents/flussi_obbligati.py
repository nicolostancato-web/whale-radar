#!/usr/bin/env python3
"""
FLUSSI_OBBLIGATI — comprare prima di chi e' COSTRETTO a comprare.

Esperimento 2 del loop sperimentale, e il primo che esce davvero dal recinto: non usa il nostro
database di memecoin, non filtra prezzi, non insegue nessuno.

L'IDEA, che non e' statistica ma meccanica:
Le nostre cinque piste morte chiedevano tutte la stessa cosa — «chi altro sta comprando?» — cioe'
seguivano l'OPINIONE di qualcuno. E l'opinione di chi ha indovinato ieri non vale domani: lo abbiamo
misurato cinque volte.
Questa chiede un'altra cosa: «chi e' COSTRETTO a comprare?». Quando una DAO vota un buyback e il
voto passa, quegli acquisti non sono una previsione: sono un appuntamento fissato con soldi gia'
stanziati. Un obbligo non cambia idea.

DOVE STA IL NOSTRO VANTAGGIO, se c'e':
Non nel sapere la notizia — i voti sono pubblici e li vedono tutti. Sta nel fatto che pochi
controllano SISTEMATICAMENTE ogni voto chiuso, ogni giorno, su centinaia di DAO. E' lavoro noioso e
continuo: esattamente cio' che una macchina fa mentre gli altri dormono.

PERCHE' CAMBIA ANCHE L'ARITMETICA DEI COSTI:
Questi non sono memecoin. Sono token scambiati su mercati profondi, dove uscire con qualche
centinaio di euro costa una frazione del 26% che paghiamo sui pool sottili. La stessa strategia,
qui, sopporta molto piu' capitale.

Fonti, entrambe gratuite e senza chiave:
  - Snapshot (hub.snapshot.org/graphql): i voti di governance, con esito e data di chiusura
  - CoinGecko: il prezzo storico del token

CRITERIO DI MORTE, scritto adesso: se il rendimento medio dopo la chiusura del voto non batte quello
dei giorni normali dello stesso token, su almeno 15 eventi, l'idea e' morta. Non si allarga la
finestra e non si cambiano le parole cercate per farla sopravvivere.

Scrive FLUSSI_OBBLIGATI.md. Sola lettura. €0.
"""
import json, os, time, urllib.request, urllib.parse, statistics as st

PAROLE = ("buyback", "buy back", "repurchase", "burn", "treasury buy")
CACHE = "data/flussi_obbligati.json"
PAUSA = 2.5              # CoinGecko free: poche richieste al minuto, si va piano
now = int(time.time())


# PERCHE' NON BASTA "None" (08/09). Il registro delle perdite diceva "il prezzo non arriva" per 22
# voti su 35, ma questa funzione inghiottiva ogni errore allo stesso modo: un id sbagliato (404) e
# un "stai chiedendo troppo in fretta" (429) tornavano entrambi None. Sono due diagnosi opposte —
# la prima e' un ponte rotto, la seconda e' solo fretta e si risolve aspettando. Un contatore che
# non distingue non e' una misura, e' una supposizione.
ERRORI = {}


def http(u, body=None, tentativi=4):
    r = urllib.request.Request(u, data=body,
                               headers={"User-Agent": "wr", "Accept": "application/json",
                                        **({"Content-Type": "application/json"} if body else {})})
    attesa = 15
    for k in range(tentativi):
        try:
            with urllib.request.urlopen(r, timeout=25) as x: return json.loads(x.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and k < tentativi - 1:
                ERRORI["429 rallentato"] = ERRORI.get("429 rallentato", 0) + 1
                time.sleep(attesa); attesa *= 2      # aspettare e' gratis, perdere un evento no
                continue
            ERRORI["http %d" % e.code] = ERRORI.get("http %d" % e.code, 0) + 1
            return None
        except Exception as e:
            ERRORI[type(e).__name__] = ERRORI.get(type(e).__name__, 0) + 1
            return None
    return None


def simbolo_dello_spazio(spazi):
    """Lo spazio Snapshot dichiara il token con cui si vota: e' il ponte fra il voto e il prezzo."""
    out = {}
    for i in range(0, len(spazi), 20):
        ids = json.dumps(spazi[i:i + 20])
        q = ('{ spaces(first:20, where:{id_in:%s}){ id name symbol '
             'strategies{ params } } }' % ids)
        d = http("https://hub.snapshot.org/graphql", json.dumps({"query": q}).encode())
        for sp in ((d or {}).get("data") or {}).get("spaces") or []:
            addr = None
            for stg in sp.get("strategies") or []:
                a = (stg.get("params") or {}).get("address")
                if a: addr = a; break
            out[sp["id"]] = {"simbolo": (sp.get("symbol") or "").upper(),
                             "nome": sp.get("name") or sp["id"], "addr": addr}
        time.sleep(0.5)
    return out


def id_da_contratto(addr, cache={}):
    """Dal contratto del token di voto al suo identificativo nei prezzi. E' il ponte migliore: un
    indirizzo e' univoco, un simbolo no — ci sono decine di token chiamati FOX."""
    if not addr: return None
    a = addr.lower()
    if a in cache: return cache[a]
    for rete in ("ethereum", "arbitrum-one", "base", "polygon-pos"):
        d = http(f"https://api.coingecko.com/api/v3/coins/{rete}/contract/{a}")
        time.sleep(PAUSA)
        if d and d.get("id"):
            cache[a] = d["id"]; return d["id"]
    cache[a] = None
    return None


def id_da_nome(nome, cache={}):
    """Ripiego: la ricerca per nome della DAO. Funziona sorprendentemente bene ("shapeshift" ->
    shapeshift-fox-token) ma e' meno sicura del contratto, quindi si usa solo se quello manca."""
    if not nome: return None
    k = nome.lower()
    if k in cache: return cache[k]
    d = http(f"https://api.coingecko.com/api/v3/search?query={urllib.parse.quote(k[:40])}")
    time.sleep(PAUSA)
    c = ((d or {}).get("coins") or [])
    cache[k] = c[0]["id"] if c else None
    return cache[k]


def id_coingecko(simbolo, cache={}):
    """dal simbolo del token all'identificativo usato dai prezzi. Si tiene in cache: la lista completa
    e' grande e non cambia spesso."""
    if not cache:
        d = http("https://api.coingecko.com/api/v3/coins/list")
        for c in (d or []):
            s = (c.get("symbol") or "").upper()
            if s and s not in cache: cache[s] = c["id"]
        time.sleep(PAUSA)
    return cache.get(simbolo.upper())


def rendimento_dopo(prezzi_lista, quando, giorni=7):
    """Quanto ha reso il token nei giorni DOPO la chiusura del voto, e quanto rendeva normalmente.
    Il confronto e' con se stesso: un token che sale sempre non prova niente."""
    if len(prezzi_lista) < 20: return None
    dopo = [p for t, p in prezzi_lista if quando <= t <= quando + giorni * 86400]
    if len(dopo) < 2: return None
    ev = dopo[-1] / dopo[0] - 1
    # i giorni "normali": tutte le altre finestre della stessa lunghezza
    normali = []
    for i in range(0, len(prezzi_lista) - giorni, giorni):
        a, b = prezzi_lista[i][1], prezzi_lista[i + giorni][1]
        if a and not (quando <= prezzi_lista[i][0] <= quando + giorni * 86400):
            normali.append(b / a - 1)
    if len(normali) < 3: return None
    return ev, st.median(normali)


def voti_che_impegnano(quanti=4000):
    """I voti CHIUSI che impegnano a comprare o bruciare. Solo quelli PASSATI: un voto respinto non
    obbliga nessuno, ed e' la meta' del punto."""
    # SI SCAVA INDIETRO (08/09). Con le sole ultime 400 proposte uscivano 8 eventi: non abbastanza
    # per un verdetto. Scendendo a 4.000 diventano 36. Gli eventi rari si trovano guardando piu'
    # lontano, non aspettando che accadano.
    grezze = []
    for skip in range(0, quanti, 1000):
        q = ('{ proposals(first:1000, skip:%d, where:{state:"closed"}, orderBy:"created", '
             'orderDirection:desc){ id title created end scores scores_total space{ id name } } }' % skip)
        d = http("https://hub.snapshot.org/graphql", json.dumps({"query": q}).encode())
        pezzo = ((d or {}).get("data") or {}).get("proposals") or []
        if not pezzo: break
        grezze += pezzo
        time.sleep(0.8)
    out = []
    for p in grezze:
        t = (p.get("title") or "").lower()
        if not any(w in t for w in PAROLE): continue
        sc = p.get("scores") or []
        if not sc or max(sc) != sc[0]: continue        # non passata: nessun obbligo
        if (p.get("scores_total") or 0) <= 0: continue
        out.append({"spazio": p["space"]["id"], "nome": p["space"]["name"],
                    "titolo": p["title"][:90], "chiuso": int(p["end"])})
    return out


def prezzi(coin_id, giorni=90):
    d = http(f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
             f"?vs_currency=usd&days={giorni}&interval=daily")
    return [(int(t / 1000), float(p)) for t, p in ((d or {}).get("prices") or [])]


def main():
    voti = voti_che_impegnano()
    L = ["# ⛓️ COMPRARE PRIMA DI CHI È COSTRETTO A COMPRARE",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · voti di governance + prezzi, "
         f"entrambi gratuiti · €0*", "",
         "> **Le nostre cinque piste morte chiedevano tutte la stessa cosa**: «chi altro sta",
         "> comprando?». Cioè seguivano l'opinione di qualcuno — e l'opinione di chi ha indovinato",
         "> ieri non vale domani. L'abbiamo misurato cinque volte.", "",
         "> Questa chiede un'altra cosa: **«chi è costretto a comprare?»**. Quando una DAO vota un",
         "> buyback e il voto passa, quegli acquisti non sono una previsione: sono **un appuntamento",
         "> fissato con soldi già stanziati**. Un obbligo non cambia idea.", "",
         f"**Voti trovati che impegnano a comprare o bruciare, e sono passati: {len(voti)}**", ""]
    if voti:
        L += ["| DAO | quando | cosa |", "|---|---|---|"]
        for v in voti[:12]:
            L.append(f"| {v['nome'][:18]} | {time.strftime('%d/%m', time.gmtime(v['chiuso']))} | "
                     f"{v['titolo'][:56]} |")
        L += [""]
    # --- LA MISURA: il token e' salito piu' del solito dopo il voto? ---
    simboli = simbolo_dello_spazio(list({v["spazio"] for v in voti})[:60]) if voti else {}
    esiti = []
    # REGISTRO DELLE PERDITE (08/09). Prima si vedeva solo "5 eventi su 35" e non DOVE finivano gli
    # altri 30: e' la differenza tra "il fenomeno e' raro" e "non lo sto guardando". Senza questo
    # registro non si sa se allargare la ricerca o riparare il ponte verso il prezzo.
    perse = {"nessun token collegato": 0, "voto troppo vecchio per i prezzi gratis": 0,
             "voto troppo recente (7 giorni non ancora passati)": 0,
             "il prezzo non arriva (id sbagliato)": 0,
             "prezzo c'e' ma la finestra dopo il voto e' vuota": 0}
    for v in voti:
        info = simboli.get(v["spazio"]) or {}
        # tre vie in ordine di affidabilita': il contratto e' univoco, il nome e' l'ultima spiaggia
        cid = id_da_contratto(info.get("addr")) \
              or (id_coingecko(info["simbolo"]) if info.get("simbolo") else None) \
              or id_da_nome(info.get("nome"))
        if not cid:
            perse["nessun token collegato"] += 1; continue
        giorni_fa = int((now - v["chiuso"]) / 86400) + 20
        if giorni_fa > 360:
            perse["voto troppo vecchio per i prezzi gratis"] += 1; continue
        if giorni_fa < 10:
            perse["voto troppo recente (7 giorni non ancora passati)"] += 1; continue
        pl = prezzi(cid, min(360, giorni_fa))
        time.sleep(PAUSA)
        # "storico insufficiente" era una voce sola e teneva insieme due diagnosi opposte:
        # il prezzo NON ARRIVA (id sbagliato, ponte rotto: colpa mia, si ripara) oppure ARRIVA ma
        # la finestra dopo il voto e' vuota (il token e' troppo giovane: e' il mondo, non un bug).
        if not pl:
            perse["il prezzo non arriva (id sbagliato)"] += 1; continue
        r = rendimento_dopo(pl, v["chiuso"])
        if r: esiti.append((v["nome"], cid, r[0], r[1]))
        else: perse["prezzo c'e' ma la finestra dopo il voto e' vuota"] += 1
    L += ["## Dove si perdono gli altri voti", "",
          f"Su **{len(voti)}** voti passati che impegnano a comprare, ne arrivano al prezzo "
          f"**{len(esiti)}**. Gli altri:", "", "| motivo | quanti |", "|---|---|"]
    L += [f"| {k} | {n} |" for k, n in sorted(perse.items(), key=lambda x: -x[1]) if n]
    if ERRORI:
        L += ["", "*Errori di rete visti mentre chiedevo i prezzi: "
              + ", ".join("%s ×%d" % (k, n) for k, n in sorted(ERRORI.items(), key=lambda x: -x[1]))
              + ".*"]
    L += ["", "> Serve a distinguere **«il fenomeno è raro»** da **«non lo sto guardando»**: se la",
          "> voce più grossa è il ponte verso il token, il problema è mio e si ripara; se è il numero",
          "> di voti, allora si scava più indietro nel tempo.", ""]

    if esiti:
        ev = [e[2] for e in esiti]; nor = [e[3] for e in esiti]
        diff = [a - b for a, b in zip(ev, nor)]
        L += [f"## La misura: {len(esiti)} eventi con prezzo verificabile", "",
              "*Il confronto è del token **con se stesso**: un token che sale sempre non prova niente.*", "",
              "| | dopo il voto | giorni normali | differenza |", "|---|---|---|---|",
              f"| media | **{st.mean(ev)*100:+.1f}%** | {st.mean(nor)*100:+.1f}% | "
              f"**{st.mean(diff)*100:+.1f}%** |",
              f"| mediana | **{st.median(ev)*100:+.1f}%** | {st.median(nor)*100:+.1f}% | "
              f"**{st.median(diff)*100:+.1f}%** |",
              f"| quante volte meglio del solito | {sum(1 for d in diff if d>0)}/{len(diff)} | | |", ""]
        if len(esiti) >= 15:
            ok = st.mean(diff) > 0 and st.median(diff) > 0
            L += ["## Verdetto", ""]
            L += ([f"> ✅ **Il segnale c'è**: dopo un voto che obbliga a comprare il token rende",
                   f"> **{st.mean(diff)*100:+.1f}%** in più dei suoi giorni normali, con media e mediana",
                   "> concordi. Prossimo passo: misurare quanto dura il vantaggio e se sopravvive ai costi."]
                  if ok else
                  ["> ❌ **Nessun vantaggio**: dopo il voto il token non rende più dei suoi giorni",
                   "> normali. **Criterio di morte scattato**, scritto prima di guardare: non si allarga",
                   "> la finestra né si cambiano le parole cercate."])
        else:
            L += [f"> ⏸️ Solo {len(esiti)} eventi con prezzo verificabile su {len(voti)} voti: sotto i 15",
                  "> del criterio. La raccolta continua a ogni giro."]
        L += [""]

    if len(voti) < 15:
        L += ["## ⏸️ Non ancora giudicabile", "",
              f"Servono almeno 15 eventi per un verdetto onesto: ne abbiamo **{len(voti)}** guardando",
              "le ultime centinaia di proposte. La raccolta continua a ogni giro e si accumula.", "",
              "> **Il criterio di morte è già scritto**: se il rendimento dopo la chiusura del voto non",
              "> batte i giorni normali dello stesso token su almeno 15 eventi, l'idea muore. Non si",
              "> allarga la finestra e non si cambiano le parole cercate per salvarla."]
    json.dump({"ts": now, "voti": voti}, open(CACHE, "w"))
    L += ["", "## Perché questa idea cambia anche i conti", "",
          "Questi non sono memecoin: sono token su mercati profondi, dove uscire con qualche centinaio",
          "di euro costa **una frazione** del 26% che paghiamo sui pool sottili. La stessa strategia,",
          "qui, sopporta molto più capitale — e risolve l'aritmetica per cui su €100 anche vincere",
          "rende pochi euro.", "",
          "> Dove starebbe il vantaggio: **non** nel sapere la notizia — i voti sono pubblici. Sta nel",
          "> controllare **sistematicamente ogni voto chiuso, ogni giorno, su centinaia di DAO**. È",
          "> lavoro noioso e continuo: esattamente ciò che una macchina fa mentre gli altri dormono."]
    open("FLUSSI_OBBLIGATI.md", "w").write("\n".join(L))
    print(f"FLUSSI_OBBLIGATI | {len(voti)} voti che impegnano a comprare, passati", flush=True)


if __name__ == "__main__":
    main()
