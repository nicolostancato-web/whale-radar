"""CONSULTA ASTRA — spedisce il fascicolo alla revisione esterna, con due freni prima del portafoglio.

COSA COSTA DAVVERO (misurato il 21/09, non stimato). La prima chiamata di prova e' costata
$0,00018 per 11 token in ingresso e 5 in uscita. Il fascicolo completo pesa circa 3.000 token, non
200.000 come avevo previsto: una consultazione vera costa intorno a $0,17, non $2,30.
Avevo sbagliato di un fattore dieci perche' avevo immaginato il fascicolo invece di misurarlo.

I DUE FRENI, in quest'ordine:

  1. IL TETTO DEI TOKEN. Oltre 272.000 token in ingresso, Astra ripreza L'INTERA richiesta a
     $20/$75 invece di $10/$50 — non il sovrapprezzo sull'eccedenza: tutto. Un fascicolo che cresce
     da 270k a 275k quasi raddoppia il conto, e la richiesta riesce lo stesso, quindi nessuno se ne
     accorge. E' la stessa forma dell'addebito da 77 euro di maggio: un prezzo cambiato sotto i
     piedi mentre il codice diceva un'altra cosa. Qui il confine non e' una cosa da ricordare: e'
     una cosa che il codice NON PUO' attraversare.

  2. IL CONTATORE GIORNALIERO. Il cap sul provider e' l'ultima linea, non la prima: un ciclo che si
     riarma male spedisce cento volte in un'ora e il cap se ne accorge a soldi gia' spesi. Questo
     contatore si rifiuta di spedire piu' di due volte al giorno, qualunque cosa dica il resto del
     sistema.

SI PAGA LA META' DEL LISTINO: `service_tier: flex` dimezza la tariffa, ed e' accettato (verificato
con una chiamata vera). Una consulenza la leggiamo dopo, non ci serve in tre secondi: non c'e'
ragione di pagare la fretta.

IL CONTATORE SI SEGNA SOLO SE LA CHIAMATA E' PARTITA. Un errore di rete non deve mangiarci una
consulenza: e' il genere di scambio fra fallimento ed esito che in questo progetto ho gia' fatto
otto volte, ogni volta credendo di aver finito un lavoro che non era partito.
"""
import json
import os
import time
import urllib.error
import urllib.request

# IL MODELLO E' BLOCCATO, E NON SI CAMBIA DA UNA VARIABILE D'AMBIENTE (21/09, direttiva del
# fondatore: «il modello dev'essere il piu' potente di OpenAI, Astra. NON voglio altri modelli»).
# Prima stava dietro a MODELLO_ASTRA: bastava una variabile sbagliata in una corsia per consultare
# in silenzio un modello piu' debole, e la consulenza sarebbe tornata comunque — solo peggiore.
# Un mentore scambiato non da' errore: da' consigli mediocri che crediamo suoi.
MODELLO = "gpt-6-astra"
TETTO_TOKEN = int(os.environ.get("TETTO_TOKEN", 250_000))   # margine sotto i 272.000
# UNA AL GIORNO, NON DUE (21/09, decisione del fondatore). A 0,11 dollari a consulenza fanno
# circa 3,30 dollari al mese invece di 6,60. La consulenza deve essere FATTA BENE, non frequente:
# due riviste mediocri al giorno valgono meno di una fatta su misure fresche.
MAX_AL_GIORNO = int(os.environ.get("MAX_AL_GIORNO", 3))   # alzato 23/09/26 da Nicolo: ~$0,11 a chiamata
MAX_USCITA = int(os.environ.get("MAX_USCITA", 4000))
CONTATORE = "data/consulenze/contatore.json"
FASCICOLO = os.environ.get("OUT_FASCICOLO", "FASCICOLO_ASTRA.txt")
# listino verificato sul sito ufficiale il 21/09/2026, tariffa flex (meta' dello standard)
PREZZO_IN, PREZZO_OUT = 5.00 / 1_000_000, 25.00 / 1_000_000


def chiave():
    """Dal segreto in cloud, dal file delle credenziali in locale. Mai dal codice, mai nei log."""
    v = os.environ.get("OPENAI_API_KEY")
    if v:
        return v.strip()
    p = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")
    try:
        for riga in open(p, errors="ignore"):
            for pref in ("sk-proj-", "sk-svcacct-"):
                j = riga.find(pref)
                if j < 0:
                    continue
                t = ""
                for c in riga[j:]:
                    if c.isalnum() or c in "-_":
                        t += c
                    else:
                        break
                if len(t) > 40:
                    return t
    except Exception:
        pass
    return ""


def quanti_token(testo):
    """Stima prudente: si arrotonda VERSO L'ALTO.

    Una stima ottimista non fa risparmiare niente e puo' farci attraversare il confine dei 272.000
    credendo di stare sotto. Meglio spedire un fascicolo piu' corto del necessario che pagarne uno
    al doppio."""
    return int(len(testo) / 3.5) + 1


def oggi_e_conto():
    oggi = time.strftime("%Y-%m-%d", time.gmtime())
    try:
        d = json.load(open(CONTATORE))
    except Exception:
        d = {}
    return oggi, int(d.get(oggi, 0)), d


# LA DISTANZA MINIMA (1/10). Il tetto di tre al giorno c'era e ha retto, ma oggi le tre chiamate
# sono partite alle 06:29, 11:55 e 11:57: due a DUE MINUTI di distanza, cioe' sullo stesso
# identico stato del sistema. Il budget era rispettato e la consulenza valeva un terzo.
# E' la stessa famiglia del `retry storm`: un freno sul TOTALE non e' un freno sul RITMO.
# Tre pareri su tre stati diversi valgono tre volte tre pareri sullo stesso stato.
DISTANZA_MINIMA_ORE = float(os.environ.get("DISTANZA_MINIMA_ORE", 3))


def troppo_presto(cont):
    """Quante ore mancano prima che una nuova consulenza abbia senso. 0 = si puo'."""
    u = cont.get("ultima")
    if not u:
        return 0.0
    passate = (time.time() - float(u)) / 3600.0
    return max(0.0, DISTANZA_MINIMA_ORE - passate)


def segna(oggi, d):
    d[oggi] = d.get(oggi, 0) + 1
    d["ultima"] = time.time()
    limite = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 7 * 86400))
    for k in [x for x in d if x < limite]:
        d.pop(k, None)
    os.makedirs(os.path.dirname(CONTATORE), exist_ok=True)
    json.dump(d, open(CONTATORE, "w"))


def main():
    oggi, fatte, cont = oggi_e_conto()
    if fatte >= MAX_AL_GIORNO:
        print(f"ASTRA | oggi ne ho gia' fatte {fatte} su {MAX_AL_GIORNO}: NON spedisco. "
              f"Il freno sta qui, non sul cap del provider — quello se ne accorge a soldi spesi.",
              flush=True)
        return

    manca = troppo_presto(cont)
    if manca > 0:
        print(f"ASTRA | l'ultima consulenza e' di meno di {DISTANZA_MINIMA_ORE:.0f} ore fa: "
              f"NON spedisco, mancano {manca:.1f} ore. Lo stato del sistema non e' cambiato "
              f"abbastanza perche' un secondo parere valga qualcosa.", flush=True)
        return

    if not os.path.exists(FASCICOLO):
        print(f"ASTRA | manca {FASCICOLO}: lancia prima agents/fascicolo_astra.py", flush=True)
        return
    testo = open(FASCICOLO).read()
    if not testo.strip():
        print("ASTRA | fascicolo VUOTO: non consulto. Un fascicolo vuoto produce consigli generici "
              "che poi crediamo scarsi per colpa di chi li ha dati.", flush=True)
        return

    tk = quanti_token(testo)
    if tk > TETTO_TOKEN:
        print(f"ASTRA | fascicolo da ~{tk} token: TAGLIO a {TETTO_TOKEN}. "
              f"Oltre 272.000 l'intera richiesta costerebbe il doppio.", flush=True)
        testo = testo[:int(TETTO_TOKEN * 3.5)]
        tk = quanti_token(testo)

    k = chiave()
    stima = tk * PREZZO_IN + MAX_USCITA * PREZZO_OUT
    if not k:
        print(f"ASTRA | PROVA A SECCO (nessuna chiave trovata: non spendo nulla)", flush=True)
        print(f"   fascicolo ~{tk} token | costerebbe al massimo ${stima:.3f} a tariffa flex "
              f"| oggi {fatte}/{MAX_AL_GIORNO}", flush=True)
        return

    corpo = json.dumps({"model": MODELLO, "input": testo, "service_tier": "flex",
                        "max_output_tokens": MAX_USCITA}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/responses", data=corpo,
                                 headers={"Authorization": f"Bearer {k}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=900) as x:
            d = json.load(x)
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read().decode()).get("error", {}).get("message", "")
        except Exception:
            msg = ""
        print(f"ASTRA | rifiutata (HTTP {e.code}): {msg[:200]}", flush=True)
        print("ASTRA | NON segno il contatore: un rifiuto non deve mangiarci una consulenza.",
              flush=True)
        return
    except Exception as e:
        print(f"ASTRA | non ha risposto ({type(e).__name__}): NON segno il contatore.", flush=True)
        return

    # CHIEDERE ASTRA NON BASTA: SI CONTROLLA CHI HA RISPOSTO. Un servizio puo' servire un modello
    # diverso da quello chiesto (ripieghi, deprecazioni, alias) e la risposta arriva lo stesso.
    # Qui la differenza non sarebbe visibile a occhio: cambierebbe solo la QUALITA' del consiglio,
    # ed e' esattamente il tipo di errore che in questo progetto scopriamo sei settimane dopo.
    _ha_risposto = d.get("model") or ""
    if MODELLO.split("-")[-1] not in _ha_risposto:
        print(f"ASTRA | ATTENZIONE: ho chiesto {MODELLO} e ha risposto '{_ha_risposto}'. "
              f"La consulenza NON e' di Astra: la tratto come non fatta.", flush=True)
        return

    segna(oggi, cont)                      # si segna solo cio' che e' davvero partito
    u = d.get("usage") or {}
    costo = u.get("input_tokens", 0) * PREZZO_IN + u.get("output_tokens", 0) * PREZZO_OUT
    # IL CONTO DELLA SPESA STA NEL REPO, NON SUL CRUSCOTTO (21/09). Il fondatore ha caricato 10
    # euro di credito PREPAGATO: e' un tetto vero solo se qualcuno guarda quanto ne resta, e
    # guardare il cruscotto del fornitore e' una cosa che ci siamo gia' dimenticati di fare per
    # sei giorni di fila con la revisione esterna.
    # Qui il totale si somma da solo a ogni chiamata, e compare accanto agli altri numeri.
    try:
        c2 = json.load(open(CONTATORE))
    except Exception:
        c2 = {}
    c2["speso_totale"] = round(c2.get("speso_totale", 0.0) + costo, 4)
    c2["chiamate_totali"] = c2.get("chiamate_totali", 0) + 1
    json.dump(c2, open(CONTATORE, "w"))
    _resto = 10 * 1.08 - c2["speso_totale"]        # 10 euro caricati, in dollari approssimati
    print(f"ASTRA | speso in tutto ${c2['speso_totale']:.2f} su {c2['chiamate_totali']} chiamate "
          f"| restano circa ${_resto:.2f} del credito caricato", flush=True)
    risposta = ""
    for el in d.get("output", []):
        for c in el.get("content", []):
            risposta += c.get("text", "")

    fn = f"CONSULENZA_{time.strftime('%Y-%m-%d_%H%M', time.gmtime())}.md"
    open(fn, "w").write(
        f"# Consulenza Astra — {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}\n\n"
        f"Costo reale: ${costo:.4f} ({u.get('input_tokens', 0)} in / "
        f"{u.get('output_tokens', 0)} out, tariffa flex)\n\n"
        + (risposta or f"(nessun testo: stato {d.get('status')})"))
    _pubblica(fn)
    print(f"ASTRA | salvata in {fn}", flush=True)
    print(f"ASTRA | costo REALE ${costo:.4f} (stimato al massimo ${stima:.3f}) | "
          f"oggi {fatte + 1}/{MAX_AL_GIORNO}", flush=True)
    if risposta:
        print("\n" + risposta, flush=True)


def _pubblica(fn):
    """Sul repository SUBITO, con l'interfaccia di GitHub.

    PERCHE' E' STATO RISCRITTO (10/10). La versione precedente cercava `api_push` dentro una
    cartella del Mac di Nicolo' (/private/tmp/claude-501/...). Sul runner quella cartella non
    esiste: l'import falliva, la consulenza restava solo sul runner, e il runner si cancella.
    Il registro diceva «success» e il file moriva — **trenta consulenze pagate perse fra il 3 e
    il 10 ottobre**, recuperate solo perche' la corsia caricava anche un allegato.

    LA REGOLA, in positivo: si pubblica con quello che esiste DOVE si sta girando. Qui si manda
    il file con l'API dei contenuti di GitHub, che funziona identica sul Mac e sul runner, e si
    prende il token dal primo posto che ce l'ha. Se non riesce, si GRIDA con il motivo: un
    fallimento silenzioso di questo passaggio costa denaro.
    """
    import base64
    import json as _j
    import re                 # SERVE QUI: non e' importato a livello di modulo, e la prima
                              # versione di questa funzione moriva con NameError proprio mentre
                              # pubblicava la consulenza. L'avevo riscritta oggi per salvare le
                              # consulenze perse, e non l'avevo mai ESEGUITA: compilare non e'
                              # provare. Un rimedio sulla strada del salvataggio va fatto girare
                              # davvero, su un file vero, prima di dire che e' riparato (10/10).
    import urllib.error
    import urllib.request

    tok = (os.environ.get("WR_PAT") or os.environ.get("GH_TOKEN")
           or os.environ.get("GITHUB_TOKEN"))
    if not tok:
        c = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")
        if os.path.exists(c):
            m = re.search(r"ghp_[A-Za-z0-9]+", open(c, encoding="utf-8", errors="ignore").read())
            tok = m.group(0) if m else None
    if not tok:
        print(f"   NON PUBBLICATA ({fn}): nessun token disponibile (WR_PAT/GH_TOKEN/"
              f"GITHUB_TOKEN). La consulenza e' costata denaro: resta solo nell'allegato.",
              flush=True)
        return False

    url = f"https://api.github.com/repos/nicolostancato-web/whale-radar/contents/{fn}"
    h = {"Authorization": f"token {tok}", "Accept": "application/vnd.github+json"}
    sha = None
    try:
        r = urllib.request.Request(url, headers=h)
        sha = _j.load(urllib.request.urlopen(r, timeout=60)).get("sha")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"   NON PUBBLICATA ({fn}): non riesco a leggere lo stato ({e.code})", flush=True)
            return False
    corpo = {"message": f"consulenza: {fn}",
             "content": base64.b64encode(open(fn, "rb").read()).decode()}
    if sha:
        corpo["sha"] = sha
    try:
        r = urllib.request.Request(url, data=_j.dumps(corpo).encode(), method="PUT", headers=h)
        urllib.request.urlopen(r, timeout=120)
        print(f"   pubblicata su GitHub: {fn}", flush=True)
        return True
    except Exception as e:
        det = getattr(e, "read", lambda: b"")()[:200].decode("utf8", "replace")
        print(f"   NON PUBBLICATA ({fn}): {type(e).__name__} {det}", flush=True)
        return False


if __name__ == "__main__":
    main()