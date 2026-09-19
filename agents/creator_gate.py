#!/usr/bin/env python3
"""
CREATOR_GATE — la pista che la consulenza esterna mette al primo posto, e per una ragione precisa:

    «Un grafico non causa un rug. Una persona sì.»

Tutto quello che abbiamo cercato finora era una correlazione: un pattern di prezzo, un wallet
fortunato, un volume. Qui invece c'e' un meccanismo economico vero: chi ha gia' creato token
diventati honeypot, con tasse assurde, o morti subito, ha un comportamento che si ripete — perche'
e' il suo mestiere. Non stiamo indovinando il futuro: stiamo riconoscendo la controparte.

Due avvertimenti della consulenza, rispettati qui:
  1. Va usato come CANCELLO (evita i disastri), non come predittore di vincitori. Un ottimo
     rilevatore di rug non deve saper riconoscere i vincenti: sono due mestieri diversi.
  2. «Non chiamare edge una macchina che passa da -40% a -10%.» Ridurre le perdite non e'
     guadagnare. Per questo qui si misurano gli EVENTI TERMINALI, non il rendimento medio.

NO-LOOKAHEAD: la reputazione di un creator al tempo T usa solo i token che ha creato PRIMA di T
e che erano gia' finiti. Confronto contro controlli appaiati per eta' e liquidita'.

CRITERIO DI MORTE, fissato adesso: se il cancello non riduce gli eventi terminali in modo
apprezzabile, oppure li riduce ma scarta cosi' tanti token da lasciare meno occasioni utili di
quante ne toglie, la pista si chiude. Non si inventano nuove categorie di creator per salvarla.

Scrive CREATOR_GATE.md. Sola lettura. €0.
"""
import json, os, glob, time, sys, statistics as st
from collections import defaultdict
sys.path.insert(0, "agents")
import controlli as C

CHAIN = os.environ.get("CHAIN", "bsc")
MAX_TOKEN = int(os.environ.get("MAX_TOKEN", 900))
CROLLO = 0.90            # "evento terminale": ha perso il 90% dal massimo e non e' tornato
now = int(time.time())


def sicurezza(chain):
    out = {}
    p = f"data/sicurezza/{chain}.jsonl"
    if not os.path.exists(p): return out
    for l in open(p):
        try:
            d = json.loads(l)
            if d.get("token"): out[d["token"].lower()] = d
        except Exception: pass
    # arricchimenti raccolti a parte (es. il creator di Solana via Helius): file separati, un solo
    # scrittore ciascuno — la lezione del 4/9, quando due processi sullo stesso file si distruggevano
    # l'archivio a vicenda.
    for extra in glob.glob(f"data/sicurezza/{chain}_*.jsonl"):
        for l in open(extra):
            try:
                d = json.loads(l)
                tk = (d.get("token") or "").lower()
                if tk: out.setdefault(tk, {}).update({k: v for k, v in d.items() if v is not None})
            except Exception: pass
    return out


def mappa_pool_token(chain):
    """i nostri file sono indicizzati per POOL, la sicurezza per TOKEN: qui si uniscono."""
    m = {}
    for p in (f"data/multichain/{chain}/token_map.json", "data/token_map.json"):
        if os.path.exists(p):
            try:
                d = json.load(open(p))
                for k, v in d.items():
                    t = v.get("tk") if isinstance(v, dict) else v
                    # minuscolo su ENTRAMBI i lati (02/09): la rubrica salva gli indirizzi EVM nella
                    # forma con le maiuscole di controllo, i file delle candele in minuscolo. Erano due
                    # scritture dello stesso indirizzo che non si riconoscevano: su BSC si agganciavano
                    # ZERO token su 265 censiti, e la pista del creator sembrava senza dati.
                    if t: m[k.lower()] = t.lower()
            except Exception: pass
    return m


def terminale(cs):
    """il token e' finito male? (crollo >=90% dal massimo, misurato sui MINIMI non sulle chiusure:
    se collassa dentro la candela, sei uscito li', non al prezzo di fine ora)"""
    p = [c[4] for c in cs if c[4]]
    if len(p) < 4: return None
    picco = max(p[: max(2, len(p) // 2)])
    basso = min(c[3] or c[4] for c in cs[len(cs) // 2:] if (c[3] or c[4]))
    return basso <= picco * (1 - CROLLO)


def main():
    U = C.Universo(CHAIN, limite=MAX_TOKEN)
    sec = sicurezza(CHAIN); pt = mappa_pool_token(CHAIN)
    if not sec:
        print(f"CREATOR_GATE | {CHAIN}: nessun dato di sicurezza", flush=True); return

    # token -> (creator, nascita, finito male?)
    #
    # BIAS DEI SOPRAVVISSUTI (corretto 03/09). Prima si partiva dai token CON una serie di prezzi, e si
    # chiamava "finito male" solo chi era crollato del 90%. Risultato: l'1% di disastri, contro il 12-24%
    # di mortalita' che misura MORTALITA.md. I due numeri non potevano essere entrambi veri.
    # Non lo erano: i token spariti senza lasciare un prezzo — i peggiori di tutti — non entravano nel
    # conto, perche' per entrarci bisognava avere un prezzo. Il cancello giudicava i creator solo sui
    # loro token sopravvissuti, cioe' esattamente quelli su cui NON serve un cancello.
    # Ora si parte dai token CENSITI: chi non ha mai prodotto una serie utilizzabile e' il caso peggiore,
    # non un caso mancante.
    inv = {}
    for pool, tk in pt.items():
        inv.setdefault(tk, pool)
    try: potati = set(json.load(open("data/potati.json")))
    except Exception: potati = set()
    info = {}
    morti_senza_prezzo = 0; saltati_potati = 0
    for tk, s in sec.items():
        if not s.get("creator"): continue
        pool = inv.get(tk)
        cs = U.cs.get(pool) if pool else None
        if cs is not None:
            t = terminale(cs)
            if t is None: continue
            info[pool or tk] = (s["creator"].lower(), U.nasce[pool], U.muore[pool], t, s)
        elif (pool or "").lower() in potati or tk in potati:
            # POTATO DA NOI (03/09): il GC lo ha rimosso perche' aveva poche candele. Non sappiamo come
            # sia finito, e chiamarlo "morto" gonfierebbe i disastri con un buco nostro. Fuori dal conto.
            saltati_potati += 1
        else:
            ts = int(s.get("ts") or 0)
            if not ts: continue
            info[tk] = (s["creator"].lower(), ts, ts, True, s)      # nessun prezzo mai = morto davvero
            morti_senza_prezzo += 1
    if len(info) < 40:
        print(f"CREATOR_GATE | {CHAIN}: solo {len(info)} token con creator e esito", flush=True)
        open("CREATOR_GATE.md", "w").write(
            f"# 🧑‍💻 REPUTAZIONE DEL CREATOR ({CHAIN})\n\n*Solo {len(info)} token hanno insieme il creator "
            f"e un esito misurabile: troppo pochi. La copertura del campo `creator` è il collo di "
            f"bottiglia, non il metodo.*\n"); return

    # reputazione al tempo T: SOLO i token gia' finiti prima di T
    per_creator = defaultdict(list)
    for pool, (cr, nasce, muore, male, s) in info.items():
        per_creator[cr].append((muore, male))
    pulito, sporco, ignoto = [], [], []
    for pool, (cr, nasce, muore, male, s) in sorted(info.items(), key=lambda kv: kv[1][1]):
        passato = [m for (fine, m) in per_creator[cr] if fine < nasce]
        # GoPlus sa gia' se quel creator ha prodotto honeypot ALTROVE, su tutta la chain: e' una
        # memoria molto piu' lunga della nostra finestra di poche centinaia di token, ed e' gratis
        # nella stessa risposta che chiediamo gia'. Senza questo, quasi ogni creator risultava
        # "mai visto prima" e la pista sembrava senza dati quando invece i dati c'erano.
        marchio = s.get("creator_gia_honeypot")
        marchio = str(marchio) if marchio is not None else None
        if marchio == "1" or any(passato): sporco.append((pool, male))
        elif marchio == "0" or (passato and not any(passato)):
            # "0" NON e' assenza di informazione: e' GoPlus che ha guardato la storia di quel creator
            # e non ha trovato honeypot. Trattarlo come "ignoto" svuotava il gruppo di confronto, e un
            # cancello senza il gruppo pulito non puo' dire niente: si confrontava con il nulla.
            pulito.append((pool, male))
        else: ignoto.append((pool, male))

    def quota(v): return (sum(1 for _, m in v if m) / len(v) * 100) if v else 0.0
    L = [f"# 🧑‍💻 REPUTAZIONE DEL CREATOR ({CHAIN})",
         "",
         "> ⛔ **PISTA CHIUSA il 04/09/2026.** Su 840 creator puliti contro 73 marchiati la differenza",
         "> era di 8 punti, dentro il rumore, e il criterio di morte era scritto prima (DECISIONS.md).",
         "> Questo verbale continua a girare per tenere il dato aggiornato, **non** perché la pista sia",
         "> viva: se un giorno tornasse a separare in modo netto sarebbe una notizia da riesaminare da",
         "> capo, non una conferma. Chi legge non deve poterlo scambiare per una pista aperta.",
         "",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · {len(info)} token con creator noto "
         f"e esito misurabile · {len(per_creator)} creator distinti · di cui {morti_senza_prezzo} "
         f"spariti senza lasciare un prezzo, {saltati_potati} esclusi perché potati da noi*", "",
         "> **Perché questa pista viene prima delle altre**: un grafico non causa un rug, una persona sì.",
         "> Non cerchiamo una correlazione: riconosciamo la controparte che controlla il gioco.", "",
         "> La reputazione ha due fonti: **i token che quel creator aveva già chiuso prima** nei nostri",
         "> dati (mai il futuro), e il marchio che **GoPlus** assegna a chi ha già prodotto honeypot",
         "> altrove sulla chain — una memoria molto più lunga della nostra.", "",
         "| chi ha creato il token | token finiti male | token |", "|---|---|---|",
         f"| creator **con precedenti puliti** | **{quota(pulito):.0f}%** | {len(pulito)} |",
         f"| creator **con almeno un disastro alle spalle** | **{quota(sporco):.0f}%** | {len(sporco)} |",
         f"| creator mai visto prima (nessuna storia) | {quota(ignoto):.0f}% | {len(ignoto)} |", ""]

    if len(pulito) >= 15 and len(sporco) >= 15:
        delta = quota(sporco) - quota(pulito)
        scartati = len(sporco) / max(1, len(pulito) + len(sporco)) * 100
        L += ["## Verdetto", ""]
        if delta >= 10:
            L += [f"> ✅ **Il cancello funziona.** Chi ha già combinato disastri li ripete: **{delta:.0f} punti**",
                  f"> di eventi terminali in più. Escludendo questi creator si scarta il **{scartati:.0f}%** dei",
                  "> token, e si evita una quota sproporzionata dei disastri.", "",
                  "> Resta un **cancello**, non un segnale d'acquisto: dice quali token NON toccare, non",
                  "> quali compreranno gli altri. Il rendimento deve venire da un secondo stadio."]
        elif delta <= -10:
            L += [f"> ⚠️ **Rovesciato**: i creator con precedenti sporchi finiscono male **meno** dei puliti",
                  f"> ({delta:.0f} punti). Prima di usarlo va capito — un risultato al contrario è quasi sempre",
                  "> un difetto di misura, non una scoperta."]
        else:
            L += [f"> ❌ **Il cancello non separa niente**: {delta:+.0f} punti di differenza, dentro il rumore.",
                  "> **Criterio di morte scattato**: non si inventano nuove categorie di creator per salvarlo."]
    else:
        L += ["## Verdetto", "",
              f"> ⏸️ **Non ancora giudicabile**: servono almeno 15 token per gruppo "
              f"(puliti {len(pulito)}, sporchi {len(sporco)}). Il limite è la copertura del campo",
              "> `creator`, non il metodo. Il test si rifà da solo man mano che il censimento cresce."]
    L += ["", "> ⚠️ Limite dichiarato: il marchio GoPlus è una **fotografia al momento del censimento**, non",
          "> necessariamente lo stato al momento in cui il token è nato. Sui token censiti appena nati la",
          "> differenza è trascurabile; sui più vecchi può contenere un pezzo di futuro. Da rifare quando",
          "> il censimento sarà abbastanza veloce da fotografare ogni token il giorno stesso.", "",
          f"> Nota: «finito male» = ha perso almeno il {CROLLO*100:.0f}% dal massimo (misurato sui **minimi**",
          "> delle candele, non sulle chiusure: se collassa dentro l'ora, tu sei uscito lì) **oppure** è",
          "> sparito senza mai lasciare un prezzo utilizzabile — che è il modo peggiore di finire, non un",
          "> dato mancante."]
    open("CREATOR_GATE.md", "w").write("\n".join(L))
    print(f"CREATOR_GATE | {CHAIN} | puliti {len(pulito)} ({quota(pulito):.0f}% male) | "
          f"sporchi {len(sporco)} ({quota(sporco):.0f}% male) | ignoti {len(ignoto)}", flush=True)


if __name__ == "__main__":
    main()
