"""La domanda quotidiana: «come posso essere piu' forte, piu' sveglio, piu' preciso di ieri?»

L'IDEA E' DI NICOLO (27/09): l'unico modo per arrivare a un'intelligenza che cresce da sola e'
FARSI LA DOMANDA IN MODO SCHEDULATO, ogni giorno, e poi attuare la risposta. Non quando capita:
sempre, come un turno di lavoro.

PERCHE' LA DOMANDA DA SOLA NON BASTA — ed e' l'unica cosa che ho aggiunto al disegno.
«Come posso migliorare?» chiesto nel vuoto produce buoni propositi: *sii piu' attento, verifica di
piu'*. Sono frasi che non cambiano una riga di codice e il giorno dopo si possono ripetere identiche.
La stessa domanda fatta **sui fatti di oggi** produce una modifica:
«oggi ho rotto tre volte la stessa corsia, sempre con un'ottimizzazione; ho impiegato due ore a
riconoscere il secondo caso e dieci minuti il terzo; cosa mi manca perche' non ci sia un quarto?»

Quindi questo agente prima RACCOGLIE le prove della giornata, poi fa la domanda con quelle davanti.

COSA RACCOGLIE, e perche' proprio questo:
 · gli errori scritti nel codice oggi (le lezioni finiscono li', non nei documenti)
 · quanto e' cresciuto il sapere esterno (LEARNINGS, consulenze)
 · la salute della fabbrica: quante corsie sono cadute, quanto spesso, per cosa
 · il tempo di riconoscimento: la misura che dice se stiamo imparando o solo lavorando

La risposta la da' Grok, che e' gratis e non e' me: chiedere a me stesso come migliorare ha il
difetto ovvio di usare la testa che ha fatto gli errori. Poi la risposta viene SCRITTA e le azioni
concrete finiscono in un elenco da fare, non in un tema.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

GIORNI = int(os.environ.get("GIORNI", 1))
FUORI = "PIU_INTELLIGENTE.md"


def _git(*a):
    try:
        return subprocess.run(["git"] + list(a), capture_output=True, text=True, timeout=120).stdout
    except Exception:
        return ""


def prove():
    """I fatti di oggi, non le impressioni — e soprattutto non il RUMORE.

    PRIMA CONTAVA TUTTO (27/09, corretto dieci minuti dopo averlo scritto): 6.798 commit e 16.076
    file in un giorno. Ma quasi tutti sono scritture automatiche delle corsie di raccolta, che
    scrivono in continuazione e non dicono niente su quanto stiamo imparando.
    Dare quei numeri a chi deve consigliarmi significa chiedere consigli sul nulla: **una misura
    sbagliata non e' meglio di nessuna misura, e' peggio, perche' sembra una misura.**

    Qui si contano solo i cambiamenti VERI: quelli che ho fatto io passando da `pubblica.sh`, non
    quelli che una corsia deposita ogni due minuti.
    """
    da = f"--since={GIORNI}.days.ago"
    # i messaggi delle corsie hanno una forma riconoscibile: nome della corsia e ora, oppure Merge
    import re
    rumore = re.compile(r"^(Merge|vivo|storico|scoperta|censimento|coppie|iniziatori|hook|riserve|"
                        r"previsioni|popolazione|insieme|ricerca|collector|sperimenti|nascite|"
                        r"pubblico|prove del giorno|GC squash|soccorso:)\b", re.I)
    righe = [l for l in _git("log", da, "--format=%s").splitlines() if l.strip()]
    veri = [l for l in righe if not rumore.match(l)]
    p = {"cambiamenti_veri": len(veri), "scritture_delle_corsie": len(righe) - len(veri)}

    # le lezioni vivono nei commenti dentro agents/: si contano le righe di commento AGGIUNTE
    diff = _git("log", da, "-p", "--", "agents")
    p["righe_di_lezione_aggiunte"] = sum(
        1 for l in diff.splitlines() if l.startswith("+") and l.lstrip("+").strip().startswith("#"))
    p["file_di_codice_toccati"] = len({
        l.split("/")[-1] for l in _git("log", da, "--name-only", "--format=", "--", "agents",
                                       ".github").split() if l.endswith((".py", ".yml"))})
    # di cosa parlano i cambiamenti veri: e' il ritratto della giornata in cinque parole
    testo = " ".join(veri).lower()
    for parola in ("ripar", "guardia", "rete", "verific", "soccorso", "misura"):
        n = testo.count(parola)
        if n:
            p[f"cambiamenti_su_'{parola}'"] = n
    p["titoli_dei_cambiamenti"] = veri[:12]

    # LE USCITE POSITIVE, che sono l'altra meta' del mestiere (Nicolo, 27/09).
    # «Non ci poniamo la domanda solo sugli errori. Se ho proposto una strategia, mi devo chiedere:
    #  come faccio a fare in modo che quella di domani sia migliore di questa?»
    # E' il punto che mancava, e vale piu' della meta' sugli errori: **un errore si fa notare da
    # solo, una proposta buona passa e resta uguale per sempre.** Nessuno critica cio' che non e'
    # sbagliato, quindi se non le si fa la domanda apposta, il livello si ferma dov'e'.
    # Qui si raccolgono le cose BUONE prodotte oggi, cosi' la domanda si puo' fare su ognuna.
    # I PIU' RECENTI, NON I PRIMI IN ORDINE ALFABETICO (28/09, trovato dalla domanda su se stessa).
    # Qui c'era `sorted(...)[:10]`: l'elenco delle uscite positive partiva dalla A e si fermava
    # dopo dieci, quindi **la domanda quotidiana non vedeva niente dopo la lettera B**.
    # Giudicava la giornata guardando `ACCUMULATION_ROADMAP.md` e `ANALYSIS.md`, toccati chissa'
    # quando, e non vedeva ne' l'ipotesi registrata ieri ne' i verdetti di stanotte.
    # **Uno strumento di misura che ordina per nome invece che per tempo misura un'altra cosa.**
    # `git log` li restituisce gia' dal piu' recente: basta non riordinarli.
    # E SI SALTANO I COMMIT CHE TOCCANO TUTTO (28/09). Il compattatore riscrive il repository in un
    # commit solo che contiene OGNI file: infilato nell'elenco, seppellisce il lavoro vero sotto
    # centinaia di nomi in ordine alfabetico. Non dice niente su cosa e' stato fatto, quindi non e'
    # una prova: e' rumore che somiglia a una prova.
    fatti, visti = [], set()
    for blocco in _git("log", da, "--name-only", "--format=%x00").split("\x00"):
        nomi = blocco.split()
        if len(nomi) > 50:                        # commit di manutenzione, non di lavoro
            continue
        for f in nomi:
            if f not in visti:
                visti.add(f)
                fatti.append(f)                   # ordine di apparizione = dal piu' recente
    def _primi(quanti, filtro):
        return [f for f in fatti if filtro(f)][:quanti]
    # LE USCITE SI LEGGONO DAL REGISTRO, NON DALLA STORIA (29/09). Il compattatore riscrive la
    # storia ogni giorno: dopo, il lavoro prodotto compare solo dentro il suo commit gigante, che
    # scartiamo come manutenzione. Misurato oggi: tre verdetti pubblicati nelle ultime 24 ore e le
    # prove dicevano zero — e da quello zero e' nato il giudizio «intelligenza ferma».
    # `data/prodotti.json` e' scritto da `pubblica_file.py` a ogni pubblicazione: e' contenuto, e il
    # contenuto sopravvive.
    import time as _t
    da_quando = _t.time() - GIORNI * 86400
    recenti = []
    try:
        for r in json.load(open("data/prodotti.json")):
            if r.get("quando", 0) >= da_quando:
                recenti += r.get("file", [])
    except Exception:
        pass
    recenti = list(dict.fromkeys(reversed(recenti)))          # dal piu' recente, senza doppioni
    scegli = lambda n, f: [x for x in recenti if f(x)][:n] or _primi(n, f)
    p["documenti_prodotti"] = scegli(10, lambda f: f.endswith(".md") and "/" not in f)
    p["ipotesi_registrate"] = scegli(6, lambda f: f.startswith("IPOTESI"))
    p["verdetti_emessi"] = scegli(6, lambda f: f.startswith("VERDETTO"))
    p["giri_di_ricerca"] = scegli(6, lambda f: f.startswith(("RICERCA", "REVISIONE", "CONSULENZA")))
    # QUANTO DI CIO' CHE CREDIAMO E' DIMOSTRATO (28/09). La domanda quotidiana giudicava il lavoro
    # senza sapere quante delle nostre lezioni siano provate e quante siano solo convinzioni scritte
    # con sicurezza. Questo numero e' la misura piu' onesta di quanto sappiamo davvero, e peggiora
    # da solo se qualcuno rompe una difesa: una lezione la cui prova fallisce diventa SMENTITA.
    # CAPACITA' O AFFERMAZIONI? (28/09). Un'azione chiusa senza aggiungere un controllo che possa
    # fallire non e' una capacita' acquisita: e' una dichiarazione che la prossima volta andra'
    # meglio. Distinguerle e' il modo piu' onesto di misurare se stiamo imparando davvero, e non
    # richiede nessun rituale nuovo: basta guardare se la riparazione ha lasciato una sentinella.
    try:
        az = json.load(open("data/azioni_miglioramento.json"))
        fatte = [x for x in az if x.get("stato") == "fatta"]
        con = [x for x in fatte if x.get("controllo", "nessuno") != "nessuno"]
        p["azioni"] = {"chiuse": len(fatte), "con_un_controllo": len(con),
                       "aperte": len([x for x in az if x.get("stato") == "da fare"])}
    except Exception as e:
        p["azioni"] = f"non leggibili: {type(e).__name__}"
    try:
        import lezioni as _L
        stati = {}
        for x in _L.verifica():
            stati[x["stato"]] = stati.get(x["stato"], 0) + 1
        p["lezioni"] = stati
    except Exception as e:
        p["lezioni"] = f"non verificabili: {type(e).__name__}"
    return p


def domanda(p):
    return f"""Sei il revisore di un sistema che deve diventare piu' intelligente ogni giorno, non
ogni tanto. Non farmi i complimenti e non darmi buoni propositi: voglio COSE DA FARE.

I FATTI DELLE ULTIME {GIORNI*24} ORE, misurati (non raccontati):
{json.dumps(p, indent=2, ensure_ascii=False)}

COSA E' ANDATO STORTO:
- ho riparato quattro strumenti di misura rotti: la finestra di osservazione, il criterio di scarto,
  il VERSO dei prezzi (contavo gli acquisti come vendite nel 73% dei casi) e la taglia (un prezzo a
  10x che scambiava 32 dollari sembrava un'uscita reale);
- ho rotto tre volte la stessa corsia automatica, sempre con una OTTIMIZZAZIONE;
- ho creato tre corsie nuove SENZA il meccanismo che le tiene vive — regola che avevo gia' scritto
  in dieci file e violato lo stesso;
- ho alzato un parametro a 45 per una ragione che due ore dopo avevo io stesso eliminato.

COSA E' ANDATO BENE, e va reso ancora migliore:
- verificare se IL LAVORO AVANZA invece di guardare se i giri dicono «riuscito»: ha trovato ogni
  singolo guasto di questi due giorni;
- registrare l'ipotesi PRIMA di guardare i dati, con la condizione di morte scritta;
- misurare la taglia accanto al prezzo: ha ucciso un'ipotesi che sembrava valere l'11%;
- pubblicare solo attraverso uno script che si rifiuta di spingere se qualcosa non compila.

LE QUATTRO DOMANDE:

1. **Qual e' la FAMIGLIA di errore che sto ripetendo?** Il meccanismo comune, non l'elenco.
2. **Quale MECCANISMO lo renderebbe impossibile?** Non una regola da ricordare — quelle le ho
   violate — ma qualcosa che si RIFIUTA di funzionare se l'errore sta per accadere.
3. **Come rendo ancora piu' forte cio' che gia' funziona?** Prendi le quattro cose buone qui sopra
   e dimmi come spremerle di piu', o dove non le sto ancora applicando.

4. **LA DOMANDA SULLE COSE BUONE — e trattala come la piu' importante.** Qui sotto ci sono le uscite
   POSITIVE di oggi: documenti, ipotesi registrate, verdetti, giri di ricerca. Nessuna di queste e'
   un errore, quindi nessuno le criticherebbe mai — ed e' esattamente per questo che restano allo
   stesso livello per sempre. Per ognuna (o almeno per le due che contano di piu'):
   **come deve essere fatta DOMANI perche' sia migliore di oggi?** Cosa manca, cosa e' pigro, cosa
   darei per scontato se la rifacessi uguale.
   In particolare: **le istruzioni che diamo a Grok per cercare su X e GitHub.** Se ogni giorno
   quelle istruzioni migliorano, la ricerca migliora da sola senza cambiare nulla d'altro.

5. **Cosa NON sto misurando** che mi farebbe vedere il prossimo errore prima di commetterlo?

FORMATO OBBLIGATORIO DELLA RISPOSTA. Prima un'analisi corta. Poi, in fondo, un blocco esatto:

```azioni
[
  {{"cosa": "descrizione in una riga di COSA scrivere", "dove": "percorso/del/file", "perche": "quale errore rende impossibile", "difficolta": "bassa|media|alta"}}
]
```

Da una a quattro azioni, ordinate dalla piu' redditizia. Ognuna deve essere **eseguibile oggi** da
chi ha accesso al codice: niente "valutare", niente "considerare". Verbi concreti."""


def estrai_azioni(risposta):
    """Tira fuori l'elenco delle azioni dal blocco dichiarato. Senza elenco, non c'e' lavoro."""
    import re
    m = re.search(r"```azioni\s*(\[.*?\])\s*```", risposta, re.S)
    if not m:
        return []
    try:
        az = json.loads(m.group(1))
    except Exception:
        return []
    return [a for a in az if isinstance(a, dict) and a.get("cosa")]


def registra(azioni):
    """Le azioni finiscono in un ELENCO DI LAVORO con uno stato, non in un documento da rileggere.

    E' il pezzo che mancava (Nicolo, 27/09): «tu mi dici, ho trovato questo errore, pero' non credo
    che in automatico tu attui una strategia per non farlo piu'». Una lezione scritta in un tema si
    puo' ignorare; una voce «da fare» con una data addosso si vede ogni giorno finche' non e' chiusa.
    """
    p = "data/azioni_miglioramento.json"
    try:
        tutte = json.load(open(p)) if os.path.exists(p) else []
    except Exception:
        tutte = []
    esistenti = {a.get("cosa") for a in tutte}
    aggiunte = 0
    for a in azioni:
        if a["cosa"] in esistenti:
            continue
        a["stato"] = "da fare"
        a["nata"] = time.strftime("%Y-%m-%d", time.gmtime())
        tutte.append(a)
        aggiunte += 1
    os.makedirs("data", exist_ok=True)
    json.dump(tutte, open(p, "w"), indent=1, ensure_ascii=False)
    aperte = [a for a in tutte if a.get("stato") == "da fare"]
    print(f"PIU' INTELLIGENTE | {aggiunte} azioni nuove, {len(aperte)} aperte in tutto", flush=True)
    for a in aperte:
        print(f"   [{a.get('difficolta','?'):5}] {a['cosa'][:90]}  -> {a.get('dove','?')}", flush=True)
    return aperte


def main():
    p = prove()
    print("PIU' INTELLIGENTE | prove raccolte:", json.dumps(p, ensure_ascii=False), flush=True)
    # LE PROVE SI RACCOLGONO DOVE C'E' LA STORIA, LA DOMANDA SI FA DOVE C'E' CHI RISPONDE (27/09).
    # Grok vive nell'abbonamento di Nicolo, sul suo Mac: sui computer di GitHub non c'e' ne' il
    # programma ne' la sessione. Una corsia che chiamasse Grok nel cloud fallirebbe ogni giorno alle
    # 05:40 — un rituale che non produce niente e che dopo una settimana nessuno guarda piu'.
    # Quindi: il cloud scrive le PROVE (che richiedono la storia del repository, e li' c'e'), e la
    # domanda viene fatta da dove Grok risponde. Le prove restano scritte e aspettano: se il Mac e'
    # spento, la domanda si fa piu' tardi sugli stessi fatti, non si perde.
    os.makedirs("data", exist_ok=True)
    json.dump({"quando": int(time.time()), "giorni": GIORNI, "prove": p},
              open("data/prove_del_giorno.json", "w"), indent=1, ensure_ascii=False)
    if os.environ.get("SOLO_PROVE") == "1":
        print("PIU' INTELLIGENTE | prove scritte, la domanda si fa altrove", flush=True)
        return
    import consulta_grok as G
    r = G.chiedi(domanda(p), minuti=25)
    if not r:
        print("PIU' INTELLIGENTE | nessuna risposta: riprovo domani", flush=True)
        return
    testa = f"""# La domanda di oggi — {time.strftime('%d/%m/%Y', time.gmtime())}

*«Come posso essere piu' forte, piu' sveglio, piu' preciso di ieri?» — fatta ogni giorno, sui fatti
del giorno. Idea di Nicolo, 27/09: e' la domanda schedulata che fa crescere l'intelligenza invece di
lasciarla ferma.*

**I fatti su cui e' stata fatta:** {json.dumps(p, ensure_ascii=False)}

---

"""
    vecchio = open(FUORI).read() if os.path.exists(FUORI) else ""
    open(FUORI, "w").write(testa + r + "\n\n---\n\n" + vecchio)
    print(f"PIU' INTELLIGENTE | scritto in {FUORI} ({len(r)} caratteri)", flush=True)
    az = estrai_azioni(r)
    if not az:
        print("PIU' INTELLIGENTE | nessuna azione estratta: la risposta non era eseguibile",
              flush=True)
        return
    registra(az)


if __name__ == "__main__":
    main()
