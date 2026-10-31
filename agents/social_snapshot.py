"""SOCIAL SNAPSHOT — l'attenzione su X, fotografata e mai piu' toccata.

LA DOMANDA (e non e' «quale coin compro»). Quando l'attenzione su X accelera su una memecoin, quella
accelerazione contiene informazione sul DOPO, oppure arriva dopo che prezzo e volume si sono gia'
mossi? Tre esiti possibili e tutti e tre interessanti:
    SOCIAL LEADS   l'attenzione accelera PRIMA del movimento
    SOCIAL FOLLOWS il movimento c'e' gia', X lo commenta
    RUMORE         nessuna relazione stabile
La distinzione conta piu' del rendimento medio: un segnale che segue non e' un segnale.

COSA NON FA. Non compra niente. Non tocca il LOOP 1. Non chiede a Grok cosa salira'. Chiede
EVIDENZA OSSERVABILE — menzioni, account distinti, quando l'accelerazione sembra iniziata, se c'e'
odore di spam — e la registra cosi' com'e'.

LO SNAPSHOT E' IMMUTABILE. Ogni rilevazione e' un file nuovo che nessuno riscrive mai, con dentro
la risposta grezza, la versione del prompt e l'identificativo del giro. Serve perche' la tentazione
di «sistemare» uno snapshot dopo aver visto come e' andata e' esattamente il modo in cui si
costruisce un risultato falso senza accorgersene. Se il prompt cambia, cambia la versione: due
snapshot di versioni diverse non si mescolano.

NIENTE SGUARDO AL FUTURO. Ogni token viene scelto SOLO con cio' che si sapeva al momento della
chiamata. Gli esiti si misurano dopo, da un altro agente, e non possono tornare indietro a
modificare quello che era stato scritto.

COSTO, verificato oggi sulle fonti ufficiali (REGOLA #0):
    oggi           X Search $5 per 1.000 CHIAMATE  -> ~$0,005 a rilevazione
    dal 21/09 12:00 PT  $5 per 1.000 POST recuperati -> ~$1 a rilevazione con 200 post
    token grok-4.20  $1,25/M in, $2,50/M out
Tre rilevazioni al giorno costano ~€8/mese adesso e ~€107/mese dopo il 21. Questo pilota sfrutta
la finestra: raccoglie a costo quasi nullo e MISURA quanti post consuma davvero una rilevazione,
cosi' la decisione del 21 si prende coi numeri veri invece che con una stima.
"""
import json
import os
import time
import urllib.parse
import urllib.request
import uuid

VERSIONE_PROMPT = "v1-2026-09-16"
MODELLO = os.environ.get("GROK_MODELLO", "grok-4.20-0309")
DIR = "data/social/snapshots"
REG = "data/social/rilevazioni.jsonl"

DOMANDA = """Cerca su X memecoin / token meme che in questo momento mostrano una crescita ANOMALA
E RECENTE dell'attenzione sociale.

NON dirmi quale token salira'. NON dirmi cosa comprare. Non mi interessa la tua opinione sul
prezzo. Mi interessa SOLO evidenza osservabile di attenzione.

Per ogni token che trovi, riporta quello che vedi davvero nei post:
- quante menzioni e da quanti account DISTINTI (se non lo sai, scrivi null)
- rispetto a prima, l'attenzione e' accelerata? di quanto?
- QUANDO sembra iniziata l'accelerazione (ora approssimativa UTC)
- la discussione sembra organica o coordinata/promozionale?
- c'e' una narrativa o un evento nuovo che la spiega?
- segni di spam, bot, account appena creati, stesso testo ripetuto

Classifica ciascun token in una di queste quattro:
  A = attenzione che sta INIZIANDO adesso
  B = attenzione GIA' ESPLOSA (il picco sembra passato)
  C = attenzione COSTANTE, nessuna accelerazione
  D = probabile SPAM o promozione artificiale

Cerco soprattutto la A. Un token famoso di cui si parla sempre non mi serve.

Rispondi SOLO con un oggetto JSON valido, senza testo attorno, in questa forma:
{"token": [{"symbol": "...", "contract": null, "chain": null, "classe": "A",
  "menzioni": null, "account_distinti": null, "accelerazione": "...",
  "inizio_accelerazione_utc": null, "organica": true, "narrativa": "...",
  "indizi_spam": "...", "evidenza": "...", "confidenza": 0.0}]}

Se un dato non lo sai, scrivi null. NON inventare numeri: un numero inventato qui rovina
l'esperimento piu' di un dato mancante."""


def chiama(chiave, giorni_indietro=1):
    """Una sola chiamata. Torna (risposta_grezza, errore)."""
    oggi = time.strftime("%Y-%m-%d", time.gmtime())
    da = time.strftime("%Y-%m-%d", time.gmtime(time.time() - giorni_indietro * 86400))
    corpo = {
        "model": MODELLO,
        "input": [{"role": "user", "content": DOMANDA}],
        "tools": [{"type": "x_search", "from_date": da, "to_date": oggi}],
    }
    req = urllib.request.Request(
        "https://api.x.ai/v1/responses",
        data=json.dumps(corpo).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {chiave}"})
    try:
        with urllib.request.urlopen(req, timeout=300) as x:
            return json.load(x), None
    except urllib.error.HTTPError as e:
        try:
            dettaglio = e.read().decode()[:300]
        except Exception:
            dettaglio = ""
        return None, f"HTTP {e.code}: {dettaglio}"
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:200]}"


def testo_di(risposta):
    """Il testo della risposta, qualunque forma abbia l'involucro."""
    for chiave in ("output_text", "text"):
        if isinstance(risposta.get(chiave), str):
            return risposta[chiave]
    pezzi = []
    for o in risposta.get("output", []) or []:
        for c in (o.get("content") or []):
            if isinstance(c, dict) and isinstance(c.get("text"), str):
                pezzi.append(c["text"])
    return "\n".join(pezzi)


def estrai_json(testo):
    """Il JSON dentro la risposta. Se non c'e', si dice: non si indovina."""
    if not testo:
        return None
    t = testo.strip()
    if t.startswith("```"):
        t = t.split("```", 2)[1]
        if t.startswith("json"):
            t = t[4:]
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j <= i:
        return None
    try:
        return json.loads(t[i:j + 1])
    except Exception:
        return None


def risolvi(simbolo):
    """Dal simbolo al contratto, con una REGOLA DICHIARATA PRIMA di guardare i risultati.

    IL PROBLEMA, scoperto alla prima rilevazione vera. Grok restituisce quasi sempre il simbolo e
    quasi mai il contratto. Ma un simbolo non identifica un token: cercando «TRAINCAT» si trovano
    20 pool, cercando «GIGADOG» 15 — fra cui un GIGADOGE su un'altra chain e un GIGADOG con
    undici dollari di liquidita'. Scegliere il pool sbagliato non da' una misura imprecisa: da' la
    misura di un altro token.

    LA REGOLA, scritta qui e non decisa caso per caso:
      1. il simbolo deve combaciare ESATTAMENTE (ignorando maiuscole e il $ iniziale);
      2. fra quelli che combaciano, si prende il pool con piu' liquidita' AL MOMENTO DELLO SNAPSHOT;
      3. si registra QUANTI candidati c'erano e la liquidita' del secondo.
    Il punto 3 e' quello che conta davvero: se il primo e il secondo si somigliano, la scelta e'
    fragile, e chi analizza deve poter buttare via quelle righe. Una regola deterministica che
    nasconde la propria fragilita' e' peggio di una scelta dichiarata incerta.

    Nessuno sguardo al futuro: la liquidita' usata e' quella di adesso, non quella di domani.
    """
    if not simbolo:
        return None
    pulito = simbolo.strip().lstrip("$").lower()
    # SI INSISTE PRIMA DI ARRENDERSI (16/09). Alla prova, il terzo token ha preso un 429 e sarebbe
    # rimasto senza contratto per sempre — cioe' mai misurabile — per una strozzatura di pochi
    # secondi. E' lo stesso errore che oggi mi ha gia' fatto dichiarare «irrecuperabili» 3.162
    # record che bastava richiedere.
    d = None
    for k in range(4):
        try:
            r = urllib.request.Request(
                f"https://api.geckoterminal.com/api/v2/search/pools?query={urllib.parse.quote(pulito)}&page=1",
                headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=30) as x:
                d = json.load(x)
            break
        except Exception as e:
            if k < 3:
                time.sleep(5 * (k + 1))
                continue
            return {"risolto": False, "motivo": f"{type(e).__name__} {getattr(e, 'code', '')}"}
    if d is None:
        return {"risolto": False, "motivo": "nessuna risposta"}
    esatti = []
    for pool in d.get("data", []) or []:
        a = pool.get("attributes") or {}
        nome = a.get("name") or ""
        base = nome.split("/")[0].strip()
        if base.lower() != pulito:
            continue
        rel = ((pool.get("relationships") or {}).get("base_token") or {}).get("data") or {}
        pid = rel.get("id") or ""
        if "_" not in pid:
            continue
        rete, contratto = pid.split("_", 1)
        try:
            liq = float(a.get("reserve_in_usd") or 0)
        except (TypeError, ValueError):
            liq = 0.0
        esatti.append({"chain": rete, "contract": contratto, "liquidita": liq, "pool": nome})
    if not esatti:
        return {"risolto": False, "motivo": "nessun pool col simbolo esatto",
                "candidati_totali": len(d.get("data", []) or [])}
    esatti.sort(key=lambda c: -c["liquidita"])
    primo = esatti[0]
    secondo = esatti[1]["liquidita"] if len(esatti) > 1 else None
    return {"risolto": True, "chain": primo["chain"], "contract": primo["contract"],
            "liquidita_allo_snapshot": primo["liquidita"], "pool": primo["pool"],
            "candidati_esatti": len(esatti), "liquidita_secondo": secondo,
            "scelta_fragile": bool(secondo and primo["liquidita"] < secondo * 3)}


def controllo(segnalati, run_id, quanti=8):
    """Il gruppo di controllo, scelto SENZA guardare il futuro.

    PERCHE' SERVE. I memecoin salgono e crollano comunque: se i token segnalati facessero +30% in
    media, da solo quel numero non direbbe niente, perche' non sapremmo cosa avrebbe fatto un
    memecoin qualunque nelle stesse ore. Il controllo e' l'unica cosa che trasforma un rendimento
    in una risposta.

    COME SI SCEGLIE, e qui si vince o si perde l'esperimento: si prendono pool recenti dalla stessa
    fonte pubblica, nello stesso momento, ESCLUDENDO quelli che Grok ha segnalato. La scelta e'
    deterministica a partire dall'identificativo del giro, quindi chiunque puo' rifarla e ottenere
    gli stessi token. Nessun criterio guarda cosa e' successo dopo — e non potrebbe, perche' «dopo»
    non e' ancora accaduto quando questa riga gira.
    """
    import hashlib
    try:
        r = urllib.request.Request(
            "https://api.geckoterminal.com/api/v2/networks/solana/new_pools?page=1",
            headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(r, timeout=30) as x:
            d = json.load(x)
    except Exception as e:
        return [], f"{type(e).__name__} {getattr(e, 'code', '')}"
    esclusi = {(s or "").lower().lstrip("$") for s in segnalati}
    cand = []
    for pool in d.get("data", []) or []:
        a = pool.get("attributes") or {}
        nome = (a.get("name") or "")
        sym = nome.split("/")[0].strip().lower()
        if sym in esclusi:
            continue
        rel = ((pool.get("relationships") or {}).get("base_token") or {}).get("data") or {}
        cid = (rel.get("id") or "").split("_", 1)[-1]
        if not cid:
            continue
        def num(v):
            try:
                return float(v)
            except (TypeError, ValueError):
                return None
        cand.append({"symbol": nome.split("/")[0].strip(), "contract": cid, "chain": "solana",
                     "prezzo_allo_snapshot": num(a.get("base_token_price_usd")),
                     "liquidita_allo_snapshot": num(a.get("reserve_in_usd")),
                     "creato": a.get("pool_created_at"), "fonte": "new_pools solana"})
    if not cand:
        return [], "nessun candidato"
    # ordine deterministico dal run_id: riproducibile, e non scelto da me
    cand.sort(key=lambda c: hashlib.sha256((run_id + c["contract"]).encode()).hexdigest())
    return cand[:quanti], None


def main():
    chiave = os.environ.get("XAI_API_KEY")
    if not chiave:
        print("SOCIAL | manca XAI_API_KEY nell'ambiente. Non chiedo il valore in chat: "
              "va messo come segreto del repo.", flush=True)
        return 1
    os.makedirs(DIR, exist_ok=True)
    # LA CADENZA SE LA REGOLA DA SOLA (16/09). La corsia gira ogni dieci minuti perche' la finestra
    # T+5m va misurata subito; ma la rilevazione su X costa e ne vogliamo tre al giorno, non 144.
    # Affidarlo a tre cron separati sarebbe fragile: GitHub salta i cron quando il repo e' occupato
    # — ci e' gia' costato cinque ore su un'altra corsia oggi. Qui invece si guarda l'orologio dei
    # FATTI: se l'ultima rilevazione riuscita e' di meno di sei ore fa, non se ne fa un'altra.
    # Cosi' un giro saltato non salta la rilevazione: la sposta, e basta.
    minimo = int(os.environ.get("MIN_INTERVALLO_S", 6 * 3600))
    if minimo > 0 and os.path.exists(REG):
        ultima = 0
        try:
            for l in open(REG):
                if l.strip():
                    r = json.loads(l)
                    if r.get("esito") == "ok" and r.get("ts", 0) > ultima:
                        ultima = r["ts"]
        except Exception:
            pass
        manca = minimo - (time.time() - ultima)
        if ultima and manca > 0:
            print(f"SOCIAL | ultima rilevazione {int((time.time()-ultima)/60)} min fa: "
                  f"aspetto altri {int(manca/60)} min (tre al giorno, non di piu')", flush=True)
            return 0
    run_id = uuid.uuid4().hex[:12]
    t_chiamata = int(time.time())

    risposta, errore = chiama(chiave)
    if errore:
        # UNA RILEVAZIONE FALLITA SI SCRIVE (16/09). Se il buco non si registra, fra un mese
        # sembrera' che in quelle ore non ci fosse attenzione su niente — ed e' una conclusione
        # falsa costruita da un silenzio.
        riga = {"run_id": run_id, "ts": t_chiamata, "versione_prompt": VERSIONE_PROMPT,
                "modello": MODELLO, "esito": "FALLITA", "errore": errore, "n_token": 0}
        with open(REG, "a") as f:
            f.write(json.dumps(riga) + "\n")
        print(f"SOCIAL | rilevazione FALLITA e registrata: {errore}", flush=True)
        return 1

    testo = testo_di(risposta)
    parsato = estrai_json(testo)
    token = (parsato or {}).get("token") or []
    uso = risposta.get("usage") or {}

    snap = {
        "run_id": run_id,
        "ts": t_chiamata,
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_chiamata)),
        "versione_prompt": VERSIONE_PROMPT,
        "modello": MODELLO,
        "domanda": DOMANDA,
        "risposta_grezza": risposta,       # tutto, senza potature: e' la prova
        "testo": testo,
        "token": token,
        "uso": uso,
    }
    # SI RISOLVE ORA, NON DOPO: la liquidita' che decide la scelta dev'essere quella di adesso
    for tk in token:
        if tk.get("contract"):
            tk["risoluzione"] = {"risolto": True, "fonte": "grok"}
            continue
        r = risolvi(tk.get("symbol"))
        tk["risoluzione"] = r
        if r and r.get("risolto"):
            tk["contract"] = r["contract"]
            tk["chain"] = r["chain"]
            tk["liquidita_allo_snapshot"] = r.get("liquidita_allo_snapshot")
        time.sleep(1.2)
    ctrl, err_ctrl = controllo([t.get("symbol") for t in token], run_id)
    snap["controllo"] = ctrl
    snap["controllo_errore"] = err_ctrl
    p = f"{DIR}/{snap['ts_utc'].replace(':', '')}_{run_id}.json"
    if os.path.exists(p):
        print(f"SOCIAL | esiste gia' {p}: non sovrascrivo uno snapshot.", flush=True)
        return 1
    with open(p, "w") as f:
        json.dump(snap, f, ensure_ascii=False, indent=1)

    classi = {}
    for t in token:
        classi[t.get("classe", "?")] = classi.get(t.get("classe", "?"), 0) + 1
    riga = {"run_id": run_id, "ts": t_chiamata, "versione_prompt": VERSIONE_PROMPT,
            "modello": MODELLO, "esito": "ok", "n_token": len(token),
            "classi": classi, "file": p, "uso": uso,
            "json_valido": parsato is not None}
    with open(REG, "a") as f:
        f.write(json.dumps(riga) + "\n")

    print(f"SOCIAL | {run_id}: {len(token)} token, classi {classi or '-'}, "
          f"json valido: {parsato is not None} | uso {uso}", flush=True)
    if parsato is None and testo:
        print(f"SOCIAL | ATTENZIONE: la risposta non era JSON valido. Salvata comunque grezza, "
              f"cosi' si puo' recuperare a mano: {p}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
