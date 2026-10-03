"""La sentinella: si accorge quando una corsia SMETTE DI PRODURRE pur non dando errori.

PERCHE' (25/09, dalla ricerca su come costruire meglio, delegata a Grok).
Tutti i guasti che ci hanno fatto perdere tempo in due giorni erano SILENZIOSI: la corsia girava,
usciva con successo, e non produceva niente. Nessun errore, nessun avviso.
 - le nascite giravano 1 volta invece di 15 (cron saltati)  -> scoperto dopo una notte
 - due raccolte si cancellavano a vicenda                    -> scoperto perche' un numero SCENDEVA
 - la restrizione non si applicava, 2,4 milioni invece di 600 mila -> scoperto leggendo i log

La regola che li unisce, scritta in positivo: **misura se il lavoro AVANZA, non se il processo
termina senza errori.** Un processo che finisce bene e non produce niente e' peggio di uno rotto,
perche' quello rotto almeno si vede.

COSA FA: per ogni archivio che ci interessa, confronta quanto conteneva l'ultima volta con quanto
contiene adesso. Se non e' cresciuto entro il tempo previsto, lo dice — e, se e' grave, avvisa su
Telegram.
"""
import datetime as dt
import gzip
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

STATO = "data/loop1/sentinella.json"

# archivio -> (ogni quanti minuti dovrebbe crescere, descrizione)
SORVEGLIATI = {
    # TOLTI IL 29/09 — secondo falso allarme, e insegna una cosa sul TIPO di archivio.
    # La sentinella ha gridato «fermo da 668 minuti». La corsia non si era mai fermata: gira ogni
    # dieci minuti e riesce sempre. Il file non cresceva perche' **non c'era niente da aggiungere** —
    # aveva smaltito l'arretrato, e lavora solo quando nascono pool nuovi.
    # **La crescita e' la misura giusta per chi raccoglie in continuazione, non per chi smaltisce un
    # arretrato**: il secondo, quando ha finito, sta fermo perche' e' in pari, ed e' il suo stato
    # migliore. Dirgli che e' rotto e' esattamente il modo di far disattivare un guardiano.
    # Che questa corsia sia viva lo controlla gia' `heartbeat`, che guarda se GIRA invece di quanto
    # produce — ed e' il controllo giusto per lei.

    "data/multichain/robinhood/hook.json": (90, "hook robinhood"),
    "data/multichain/base/hook.json": (90, "hook base"),
    # TOLTO DALLA SORVEGLIANZA IL 28/09 — e il dato resta, si toglie solo la guardia.
    # La sentinella ha gridato «previsioni fermo da 177 minuti». Due cose sbagliate in una riga:
    #  · il file non lo scrive `previsioni` ma `registro_segnali`, quindi l'allarme mandava a
    #    cercare il guasto nella corsia sbagliata — e `previsioni` intanto lavorava benissimo,
    #    240 previsioni scritte e spinte al primo tentativo;
    #  · `registro_segnali.py` non e' avviato da NESSUNA corsia: quell'archivio non crescera' mai
    #    piu', quindi l'allarme sarebbe suonato per sempre.
    # Un guardiano che grida al lupo viene disattivato, e sarebbe una perdita molto piu' grande di
    # questa riga. **Si sorveglia cio' che deve crescere; il resto e' storia, e la storia sta ferma
    # per mestiere.** Il file non viene cancellato: serve ancora a `verdetto_h4.py`.

    # LA CORSIA NUOVA VA SORVEGLIATA COME LE ALTRE (26/09). `insieme.yml` e' nata stanotte e
    # ricostruisce i dati su cui si decide: se si ferma, le analisi continuano a girare sull'ultima
    # versione buona e nessuno se ne accorge — e' il modo peggiore di rompersi, perche' non sembra
    # rotto. Aggiungerla qui e' la condizione 2 dell'auto-apprendimento: un miglioramento si propaga
    # a tutti i pezzi simili nello stesso momento in cui lo si scopre.
    # Soglia larga (90 min) perche' la corsia gira ogni ~27 minuti ma la coda dei push puo' ritardarla.
    "data/loop1/insieme_robinhood.jsonl.gz": (90, "insieme robinhood"),
    "data/loop1/insieme_base.jsonl.gz": (90, "insieme base"),
}


def quanti(p):
    """Quante cose contiene. None se non si riesce a leggere — che NON e' zero."""
    if not os.path.exists(p):
        return None
    try:
        if p.endswith(".jsonl.gz"):
            # PRIMA DI QUESTA RIGA finiva nel ramo `.json.gz`, `json.load` si strozzava sulla seconda
            # riga e `quanti()` tornava None: il guardiano avrebbe detto «non riesco a leggere»
            # invece di contare. Un guardiano che non sa leggere cio' che sorveglia e' un guardiano
            # che tace (26/09, trovato mentre lo collegavo, non dopo).
            return sum(1 for l in gzip.open(p, "rt") if l.strip())
        if p.endswith(".json.gz"):
            d = json.load(gzip.open(p, "rt"))
            return len(d.get("da", d))
        if p.endswith(".json"):
            d = json.load(open(p))
            return len(d.get("hook", d.get("da", d)))
        return sum(1 for l in open(p) if l.strip())
    except Exception:
        return None


from rianima import tutto as _controlla      # una copia sola, usata da piu' guardiani


def dimensione_repository():
    """Quanto pesa il repository su GitHub, e quanto manca al muro.

    IL LIMITE FERMA TUTTO SENZA PREAVVISO (30/09). A dieci gigabyte GitHub rifiuta ogni spinta:
    non una corsia, TUTTE. Ieri e' successo con un file oltre i 100 MB e ci sono volute tre ore
    per capirlo, perche' nei registri si leggeva «contesa sul ramo» — il sintomo, non la causa.
    Oggi il repository e' passato da 4,66 a 7,13 GB, poi la pulizia l'ha riportato a 3,22.
    Non voglio dipendere dal fatto che mi ricordi di guardare: se supera la soglia, si grida.
    """
    import urllib.request
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not tok:
        return None
    repo = os.environ.get("GITHUB_REPOSITORY", "nicolostancato-web/whale-radar")
    try:
        r = urllib.request.Request("https://api.github.com/repos/" + repo,
                                   headers={"Authorization": "token " + tok})
        return json.load(urllib.request.urlopen(r, timeout=20)).get("size", 0) / 1e6
    except Exception:
        return None


def main():
    ora = int(time.time())
    vecchio = {}
    if os.path.exists(STATO):
        try:
            vecchio = json.load(open(STATO))
        except Exception:
            vecchio = {}
    nuovo = {}
    fermi = []
    # DUE CAMPANE, NON UNA (1/10). Qui ogni cosa ferma faceva uscire con errore, e GitHub manda
    # un'email per ogni errore: 32 email identiche in tre giorni, tutte intitolate «sentinella
    # failed». Non erano guasti — era l'allarme che suonava. Ma un allarme che suona uguale per
    # «una corsia e' indietro di tre ore» e per «si sta cancellando lavoro» si smette di
    # leggerlo: e' `automation bias`, e si paga il giorno in cui quello vero arriva.
    # Qui l'email parte solo per i GRAVI. Gli avvisi si stampano e si leggono quando si guarda.
    avvisi = []
    for p, (minuti, nome) in SORVEGLIATI.items():
        n = quanti(p)
        if n is None:
            print(f"SENTINELLA | {nome}: non leggibile, non giudico", flush=True)
            continue
        v = vecchio.get(p)
        nuovo[p] = {"n": n, "quando": ora}
        if not v:
            print(f"SENTINELLA | {nome}: prima misura, {n:,}", flush=True)
            continue
        passati = (ora - v["quando"]) / 60
        cresciuto = n - v["n"]
        if cresciuto < 0:
            fermi.append(f"{nome}: SCESO da {v['n']:,} a {n:,} — si sta cancellando lavoro")
        elif passati >= minuti and cresciuto == 0:
            # grave solo se il ritardo e' oltre il TRIPLO dell'atteso: sotto, e' la coda
            riga = f"{nome}: fermo a {n:,} da {passati:.0f} minuti (atteso entro {minuti})"
            (fermi if passati > 3 * minuti else avvisi).append(riga)
        else:
            print(f"SENTINELLA | {nome}: {n:,} (+{cresciuto:,} in {passati:.0f} min)", flush=True)
    # si conserva la misura precedente quando non e' passato abbastanza tempo
    for p, v in vecchio.items():
        if p in nuovo and (ora - v["quando"]) / 60 < SORVEGLIATI.get(p, (90,))[0]:
            nuovo[p] = v
    os.makedirs(os.path.dirname(STATO), exist_ok=True)
    json.dump(nuovo, open(STATO, "w"))
    for riga in _controlla():
        print(f"SENTINELLA | {riga}", flush=True)
    gb = dimensione_repository()
    if gb is not None:
        # 7 GB su 10: da li' in poi mancano poche ore di crescita al blocco totale.
        if gb >= 7.0:
            # ACCORGERSENE E NON AGIRE E' META' DEL LAVORO (30/09). La prima versione si limitava
            # a scrivere «lanciare repo_gc adesso» — a qualcuno che magari dormiva. La pulizia
            # gira una volta al giorno alle 3; il repository cresce di mezzo gigabyte l'ora.
            # Fra l'allarme e il muro dei dieci gigabyte ci sono poche ore: la guardia la lancia.
            lanciata = "non sono riuscito a lanciarla"
            try:
                import urllib.request
                tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
                repo = os.environ.get("GITHUB_REPOSITORY", "nicolostancato-web/whale-radar")
                r = urllib.request.Request(
                    f"https://api.github.com/repos/{repo}/actions/workflows/repo_gc.yml/dispatches",
                    data=b'{"ref":"main"}', method="POST",
                    headers={"Authorization": "token " + tok,
                             "Accept": "application/vnd.github+json"})
                urllib.request.urlopen(r, timeout=20)
                lanciata = "ho lanciato repo_gc"
            except Exception as e:
                lanciata = f"NON sono riuscito a lanciare repo_gc ({type(e).__name__})"
            fermi.append(f"IL REPOSITORY PESA {gb:.1f} GB su 10: al limite si ferma TUTTO. "
                         f"{lanciata}.")
        else:
            print(f"SENTINELLA | repository {gb:.2f} GB su 10", flush=True)
    if avvisi:
        print("SENTINELLA | AVVISI (non mandano email, si leggono qui): "
              + " | ".join(avvisi), flush=True)
    if fermi:
        testo = "whale-radar: qualcosa si e' fermato senza dare errori.\n\n" + "\n".join(fermi)
        print("SENTINELLA | " + " | ".join(fermi), flush=True)
        # L'ALLARME VA SU TELEGRAM, NON NELLA CASELLA EMAIL (1/10, chiesto da Nicolo').
        # Uscire con errore qui serviva a una cosa sola: far mandare a GitHub l'email
        # «sentinella failed». Trentadue in tre giorni, tutte col titolo identico, nessuna che
        # dicesse COSA fosse successo. Nicolo' ha smesso di aprirle, che e' il peggior esito
        # possibile per un allarme.
        # Adesso il messaggio parte su Telegram col testo dentro, e la corsia esce PULITA:
        # niente email. Se Telegram non riesce a partire, allora si' che si esce con errore,
        # perche' restare zitti sarebbe peggio di una email di troppo.
        mandato = False
        try:
            import avvisa
            mandato = bool(avvisa.avvisa(testo))
        except Exception as e:
            print(f"SENTINELLA | Telegram non ha funzionato ({type(e).__name__})", flush=True)
        if not mandato:
            print("SENTINELLA | NON SONO RIUSCITO AD AVVISARE SU TELEGRAM: esco con errore, "
                  "cosi' almeno arriva l'email. Un allarme muto non e' un allarme.", flush=True)
            sys.exit(1)
        print("SENTINELLA | avvisato su Telegram, esco pulita: niente email.", flush=True)
        sys.exit(0)
    print("SENTINELLA | tutto avanza", flush=True)


if __name__ == "__main__":
    main()
