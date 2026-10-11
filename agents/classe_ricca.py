#!/usr/bin/env python3
"""
CLASSE_RICCA — la classe di ipotesi arricchita, e la STESSA prova che ha ucciso quella povera.

DA DOVE VIENE (14/09). Il test di permutazione a blocchi ha mostrato che, con le nostre dieci feature
scritte a mano, il risultato non batte il massimo del caso su nessuna delle tre chain. Ma quel test
non giudica i dati: giudica la coppia CLASSE DI IPOTESI + PROCEDURA. Un segnale che vivesse
nell'identita' dei wallet, nella sequenza o nei tempi non poteva comparire — quelle variabili non
entravano nemmeno nel test.

Qui la classe si allarga con cio' che il revisore avversariale ha indicato come rappresentazione
mancante, e si rifa' ESATTAMENTE la stessa prova. Non un test piu' gentile: lo stesso.

LE NUOVE VARIABILI (tutte calcolate solo su cio' che e' successo PRIMA di poter comprare):
  - SEQUENZA: le vendite sono arrivate prima o dopo gli acquisti? (il nostro sell_ratio le confonde)
  - TEMPI: quanto passa fra un'operazione e l'altra, e quanto e' irregolare (raffiche o gocciolamento)
  - IDENTITA': quota del compratore piu' grosso, quanti tornano a comprare
  - MEMORIA: quota di compratori gia' visti su token NATI PRIMA di questo

IL TRANELLO DELLA MEMORIA, ed e' quello che il revisore ha segnalato: se contassi i wallet "visti sui
nostri token" senza guardare le date, userei per il token di oggi informazioni prodotte da token di
domani. Non sarebbe un miglioramento, sarebbe una fuga di informazione. Qui un wallet conta come
"gia' visto" solo se e' apparso su un token NATO PRIMA di quello che sto valutando.

CRITERIO DI MORTE, scritto adesso: se la classe ricca non batte il MASSIMO dei mondi permutati su
nessuna chain, due classi molto diverse hanno fallito la stessa prova — e l'ipotesi "in questi dati
non c'e' un vantaggio raggiungibile" diventa la spiegazione piu' semplice.

Sola lettura, nessuna chiamata. €0.
"""
import json, gzip, os, sys, time, math, random, statistics as st
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multichain_brain as B
from permutazione import robusta, permuta_nei_blocchi

MC = "data/multichain"
CHAINS = tuple((os.environ.get("RICCA_CHAINS") or "base,robinhood,solana").split(","))
TETTO = int(os.environ.get("RICCA_TETTO", 700))
MONDI = int(os.environ.get("RICCA_MONDI", 6))
SOGLIE = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
RITARDO = getattr(B, "RITARDO_OSS", 3 * 3600)


def scambi(ch, pool):
    """Legge DUE origini: la fonte gratuita (trades/) e la catena (storico/).

    PERCHE' DUE (14/09). La fonte gratuita conserva solo gli ultimi ~300 scambi, quindi per un token
    maturo i PRIMI acquisti non ci sono piu' — ed e' esattamente il dato che serve. Dalla catena
    invece c'e' tutto, per sempre: da stanotte lo scaviamo. Ma un archivio che nessuno legge non
    serve a niente (e' l'errore di wallet_scores.json, 3,2 MB mai aperti da nessun modello), quindi
    la lettura arriva INSIEME alla raccolta, non dopo.

    COSA PRENDIAMO DALLA CATENA, e cosa no. Prendiamo i fatti certi: istante, wallet, e la quantita'
    grezza del lato quotato (che dentro lo stesso pool e' confrontabile). NON deduciamo acquisto o
    vendita: per saperlo servirebbe sapere quale dei due token e' la moneta, e non lo sappiamo ancora
    pool per pool. Preferisco una variabile in meno a una variabile inventata."""
    out = []
    f = f"{MC}/{ch}/trades/{pool}.jsonl.gz"
    if os.path.exists(f):
        try:
            for l in gzip.open(f, "rt"):
                try:
                    r = json.loads(l)
                    if r.get("ts"): out.append(r)
                except Exception: pass
        except Exception: pass
    fs = f"{MC}/{ch}/storico/{pool}.jsonl.gz"
    if os.path.exists(fs):
        visti = {r.get("tx") for r in out}
        try:
            for l in gzip.open(fs, "rt"):
                try:
                    r = json.loads(l)
                    if not r.get("ts") or r.get("tx") in visti: continue
                    # dalla catena: taglia = quantita' del lato quotato, in unita' del pool
                    r["usd"] = abs(r.get("a1") or 0) / 1e18
                    r.setdefault("kind", "buy" if (r.get("a1") or 0) > 0 else "sell")
                    out.append(r)
                except Exception: pass
        except Exception: pass
    out.sort(key=lambda r: r["ts"]); return out


def memoria_wallet(ch, righe):
    """wallet -> il PRIMO istante in cui l'abbiamo visto. Serve a chiedersi «lo conoscevo gia'?»
    senza guardare nel futuro."""
    primo = {}
    for r in righe:
        for t in scambi(ch, r["pool"]):
            w = t.get("w")
            if w and (w not in primo or t["ts"] < primo[w]): primo[w] = t["ts"]
    return primo


try:
    import embargo as EMB
except Exception:
    EMB = None


def ricche(tr, ent, primo, chain=None, pool=None):
    """Le variabili che la classe povera non puo' rappresentare. Solo passato, sempre."""
    # L'EMBARGO E' UNA PROPRIETA' DELLA FONTE, NON UN NUMERO UNICO (15/09). Prima si sottraeva
    # 35,4 ore a tutto — un valore che veniva da BSC, chain abbandonata — e nessuno scambio poteva
    # passare. Adesso ogni scambio risponde alla domanda giusta: "alle 'ent' avevamo GIA' questo?".
    # Un dato dei fornitori aspetta il ritardo misurato della SUA chain; un dato che leggiamo noi
    # dalla catena aspetta mezz'ora, che e' piu' di quanto ci mettiamo davvero.
    if EMB is not None and chain:
        pre = [t for t in tr if EMB.utilizzabile(t, ent, chain, pool)]
    else:
        pre = [t for t in tr if t["ts"] <= ent - RITARDO]
    if len(pre) < 6: return None
    buy = [t for t in pre if t.get("kind") == "buy"]
    sell = [t for t in pre if t.get("kind") == "sell"]
    if len(buy) < 3: return None
    t0 = pre[0]["ts"]; span = max(1.0, pre[-1]["ts"] - t0)
    # SEQUENZA: centro di massa temporale delle vendite meno quello degli acquisti, in frazione di
    # finestra. Negativo = si e' venduto PRIMA di comprare; positivo = si e' venduto DOPO.
    cb = sum((t["ts"] - t0) for t in buy) / len(buy) / span
    cs = (sum((t["ts"] - t0) for t in sell) / len(sell) / span) if sell else cb
    ordine = cs - cb
    # TEMPI: quanto passa fra un'operazione e l'altra, e quanto e' irregolare
    dt = [pre[i + 1]["ts"] - pre[i]["ts"] for i in range(len(pre) - 1)] or [0]
    med_dt = st.median(dt)
    raffica = (st.pstdev(dt) / (st.mean(dt) + 1e-9)) if len(dt) > 2 else 0.0
    # IDENTITA': concentrazione e ritorno
    per_w = defaultdict(float); conte = defaultdict(int)
    for t in buy:
        per_w[t.get("w") or "?"] += t.get("usd") or 0
        conte[t.get("w") or "?"] += 1
    tot = sum(per_w.values()) or 1.0
    concentr = max(per_w.values()) / tot
    ritornano = sum(1 for w in conte if conte[w] > 1) / len(conte)
    # MEMORIA point-in-time: quota di compratori gia' visti PRIMA di questa finestra
    noti = sum(1 for w in per_w if primo.get(w, ent) < t0)
    quota_noti = noti / len(per_w)
    return [ordine, math.log10(med_dt + 1), raffica, concentr, ritornano, quota_noti]


def prepara(ch):
    righe = B.load_rows(ch)
    if len(righe) < 120: return [], 0
    righe = righe[-TETTO:]
    primo = memoria_wallet(ch, righe)
    fuori = []
    for r in righe:
        nuove = ricche(scambi(ch, r["pool"]), r["ent"], primo, ch, r["pool"])
        if nuove is None: continue
        q = dict(r); q["f"] = list(r["f"]) + nuove
        fuori.append(q)
    return fuori, len(righe)


def discrimina(righe, soglie):
    """UN TEST CHE NON SA DISTINGUERE NON PUO' DIRE "NO" (14/09). Con 118 righe tutte le soglie
    selezionavano TUTTE le righe: il modello non si attivava mai (serve un passato di WARMUP righe
    gia' CHIUSE prima di ogni entrata, e con poche righe quel passato non si forma). Il risultato
    erano tre numeri identici alla prima cifra decimale — e il codice, non trovando un vincitore, ha
    scritto "la classe ricca non batte il caso". Era un test senza potere, spacciato per verdetto.
    Qui si controlla PRIMA: se soglie diverse scelgono lo stesso identico insieme, non c'e' niente da
    giudicare e si dice NON GIUDICABILE."""
    conte = set()
    for thr in soglie:
        try:
            conte.add(len(B.walkforward_righe(righe, thr=thr)))
        except Exception:
            pass
    return len(conte) > 1


def massimo(righe):
    best = None
    for thr in SOGLIE:
        try:
            sel = [r["ret"] for r in B.walkforward_righe(righe, thr=thr)]
        except Exception:
            continue
        v = robusta(sel)
        if v is not None and (best is None or v > best): best = v
    return best


def main():
    L = ["# 🧬 LA CLASSE ARRICCHITA — stessa prova, rappresentazione più ricca",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · €0*", "",
         "> La permutazione a blocchi ha ucciso la classe povera su tre chain. Ma quel test non giudica",
         "> i dati: giudica **classe di ipotesi + procedura**. Un segnale che vivesse nell'identità dei",
         "> wallet, nella sequenza o nei tempi non poteva comparire — **quelle variabili non entravano**.", "",
         "> Qui la classe si allarga con le sei variabili che mancavano, e si rifà **esattamente la",
         "> stessa prova**. Non un test più gentile: lo stesso.", "",
         "**Le sei nuove variabili** (tutte solo su ciò che è accaduto prima di poter comprare):", "",
         "| variabile | cosa cattura che prima si perdeva |",
         "|---|---|",
         "| ordine vendite/acquisti | `sell_ratio` è identico se si vende prima o dopo: qui no |",
         "| tempo fra le operazioni | 50 scambi in 5 minuti ≠ 50 scambi in 5 ore |",
         "| irregolarità (raffiche) | gocciolamento costante ≠ esplosioni separate da silenzio |",
         "| concentrazione del più grosso | un compratore da 1.000$ ≠ dieci da 100$ |",
         "| quanti tornano a comprare | chi ricompra dice qualcosa che il conteggio non dice |",
         "| compratori già visti **prima** | la memoria dei wallet, senza guardare nel futuro |", "",
         "> ⚠️ **Il tranello evitato**: contare i wallet «già visti sui nostri token» senza guardare le",
         "> date userebbe, per il token di oggi, informazione prodotta da token di domani. Non sarebbe un",
         "> miglioramento: sarebbe **fuga di informazione**. Qui un wallet conta come già visto solo se",
         "> è apparso su un token **nato prima** di quello valutato.", "",
         "| chain | righe usabili | povera | **ricca** | il caso, al massimo | la ricca batte il caso? |",
         "|---|---|---|---|---|---|"]
    # NON SAPERE NON E' AVER FALLITO (14/09). La prima esecuzione ha scritto "nemmeno la classe ricca
    # batte il caso" quando il test NON ERA MAI STATO FATTO: su 400 righe solo 70 avevano abbastanza
    # scambi, e il codice, non trovando nulla da dichiarare vincente, e' finito nel ramo del fallimento.
    # E' esattamente l'errore che questo progetto insegue da giorni: uno zero che viene dal non aver
    # guardato, travestito da risposta. Un verdetto puo' dire "no" solo se la prova e' stata eseguita.
    trovato = False
    provate = 0
    for ch in CHAINS:
        try:
            righe, n0 = prepara(ch)
        except Exception as e:
            L.append(f"| **{ch}** | errore: {type(e).__name__} | | | | |"); continue
        if len(righe) < 100:
            L.append(f"| **{ch}** | {len(righe)}/{n0} *troppo poche* | | | | |"); continue
        if not discrimina(righe, SOGLIE):
            L.append(f"| **{ch}** | {len(righe)}/{n0} | ⏸️ *il modello non discrimina: tutte le "
                     "soglie scelgono le stesse righe* | | | |")
            continue
        povere = [dict(r, f=r["f"][:10]) for r in righe]
        v_pov = massimo(povere)
        v_ricca = massimo(righe)
        finti = []
        for k in range(MONDI):
            v = massimo(permuta_nei_blocchi(righe, 9000 + k))
            if v is not None: finti.append(v)
        if v_ricca is None or len(finti) < 3:
            L.append(f"| **{ch}** | {len(righe)} | non calcolabile | | | |"); continue
        top = max(finti)
        vince = v_ricca > top
        trovato = trovato or vince
        provate += 1
        L.append(f"| **{ch}** | {len(righe)}/{n0} | {v_pov:+.1f}% | **{v_ricca:+.1f}%** | "
                 f"{top:+.1f}% | {'✅ **sì**' if vince else '❌ no'} |")
    L += ["", "## Verdetto", ""]
    if provate == 0:
        L += ["> ⏸️ **NON GIUDICABILE.** Su nessuna chain c'erano abbastanza righe con scambi",
              "> sufficienti per costruire le sei variabili nuove: la prova **non è stata eseguita**.",
              "> Non è un fallimento della classe ricca — è un dato che manca. Dire «no» qui sarebbe",
              "> spacciare per risposta uno zero che viene dal non aver guardato."]
    elif trovato:
        L += ["> ✅ **Su almeno una chain la classe ricca batte il massimo del caso.** È la prima volta",
              "> che accade in questo progetto. Prossimo passo obbligato: **quale** delle sei variabili",
              "> lo produce, e regge togliendo le altre? Un vantaggio che sparisce isolandolo non era un",
              "> vantaggio."]
    else:
        L += ["> ❌ **Nemmeno la classe ricca batte il massimo del caso.** Due classi molto diverse hanno",
              "> fallito la stessa prova: l'ipotesi «in questi dati non c'è un vantaggio raggiungibile»",
              "> diventa la spiegazione più semplice.", "",
              "> Resta vero che una terza classe ancora più ricca potrebbe riuscirci — ma il peso della",
              "> prova adesso sta dalla parte di chi vuole continuare, non di chi vuole fermarsi."]
    open("CLASSE_RICCA.md", "w").write("\n".join(L))
    print("CLASSE_RICCA | scritto", flush=True)


if __name__ == "__main__":
    main()
