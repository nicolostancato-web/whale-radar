"""MOTORE A VUOTO — quanto facilmente questa macchina trova cose che non esistono.

E' il primo pezzo del loop 1, e si costruisce PRIMA degli altri di proposito.

PERCHE' ESISTE. Il vecchio motore provava novanta configurazioni e prendeva la migliore. Con
novanta prove sullo stesso campione, la migliore e' migliore anche per fortuna — e non c'era modo
di distinguere «funziona» da «ha pescato bene». La revisione esterna ha poi mostrato che nemmeno
le correzioni statistiche classiche bastano: controllano la quota di false scoperte fra quelle
dichiarate, non la probabilita' che l'UNICA configurazione mandata in produzione sia falsa.
E nel documento avevo scritto «Benjamini-Hochberg, non Bonferroni che sarebbe troppo severo»:
avevo scelto il controllo in base a quanto era facile passarlo, senza accorgermene.

LA RISPOSTA NON E' UNA CORREZIONE PIU' FURBA, E' UNA MISURA.
Si costruiscono dati in cui, PER COSTRUZIONE, non c'e' NIENTE da trovare. Poi si fa girare sopra
l'intera pipeline — la stessa, senza sconti — e si conta quante volte promuove qualcosa.
Se su dati vuoti promuove nel 30% dei casi, una promozione sui dati veri vale quanto quella.

I DATI FINTI DEVONO SOMIGLIARE AI VERI DOVE CONTA, o la prova e' troppo facile:
  - RENDIMENTI ASIMMETRICI A DESTRA: quasi tutti i token vanno quasi a zero, pochissimi fanno
    molti multipli. Con rendimenti simmetrici qualunque metodo sembra prudente.
  - DIPENDENZA FRA TOKEN CONTEMPORANEI: quando il mercato si muove, si muovono insieme. Ignorarlo
    fa sembrare le osservazioni molto piu' numerose di quante siano davvero.
  - CONDIZIONI OSSERVABILI SCORRELATE DALL'ESITO: liquidita', eta', numero di compratori esistono
    e si possono tagliare in gruppi — ma non predicono niente. E' qui che nasce l'illusione:
    con abbastanza tagli, un gruppo «buono» si trova sempre.

COSA NON FA. Non dice se una strategia e' buona. Dice se questa macchina e' capace di dire di no.
Una macchina che non sa dire di no non serve a niente, per quanto sofisticata sia.
"""
import json
import math
import os
import random
import sys

SEME = int(os.environ.get("SEME", 20260922))
N_TOKEN = int(os.environ.get("N_TOKEN", 3000))
N_PROVE = int(os.environ.get("N_PROVE", 200))      # quante volte si rifa' il mondo da zero
SOGLIA_ALLARME = float(os.environ.get("SOGLIA_ALLARME", 5.0))   # % massima di promozioni ammessa
FUORI = "data/loop1/motore_a_vuoto.json"

# le condizioni osservabili: esistono, si misurano, e NON predicono nulla
CONDIZIONI = ["liquidita", "eta_ore", "compratori", "concentrazione", "ritmo_scambi"]


def mondo(rnd):
    """Un mercato finto senza alcun vantaggio da trovare.

    I rendimenti hanno la forma giusta (log-normale molto asimmetrica, media sotto zero dopo i
    costi) e i token nati nello stesso momento condividono uno shock comune. Le condizioni sono
    generate INDIPENDENTEMENTE dall'esito: qualunque relazione che il motore trovera' qui dentro
    e' rumore, per costruzione."""
    token = []
    n_blocchi = max(1, N_TOKEN // 40)              # token contemporanei = stesso shock
    shock = [rnd.gauss(0, 0.35) for _ in range(n_blocchi)]
    for i in range(N_TOKEN):
        b = i % n_blocchi
        # log-normale: mediana bassa, coda destra lunga
        r = math.exp(rnd.gauss(-1.1, 1.35) + shock[b]) - 1.0
        r = max(-0.98, r)                          # non si perde piu' del capitale
        t = {"rendimento": r, "blocco_tempo": b}
        for c in CONDIZIONI:
            t[c] = rnd.random()                    # scorrelate dall'esito, per costruzione
        token.append(t)
    return token


def mondo_con_vantaggio(rnd, forza=0.55):
    """Lo stesso mercato, ma con un vantaggio VERO nascosto dentro.

    UN TEST CHE NON PUO' SUONARE NON E' UN TEST (22/09). Alla prima prova la macchina ha promosso
    in ZERO mercati vuoti su 40. Ottimo — ma una macchina che non promuove MAI supera quella prova
    e non serve a niente. Le due domande vanno fatte insieme:
        «trova cose che non esistono?»   -> il mondo vuoto
        «trova cose che esistono?»       -> questo
    Qui i token con liquidita' bassa E molti compratori rendono davvero di piu'. Se la macchina non
    lo vede, e' cieca; se lo vede solo qualche volta, sappiamo quanto e' cieca.
    La forza del vantaggio e' dichiarata: cosi' il risultato si legge come «riesce a vedere un
    vantaggio di questa taglia», non come un si' o un no assoluto."""
    token = mondo(rnd)
    for t in token:
        if t["liquidita"] < 0.5 and t["compratori"] >= 0.5:
            t["rendimento"] = max(-0.98, (1 + t["rendimento"]) * (1 + forza) - 1)
    return token


def media_portafoglio(gruppo):
    """La media di cio' che finisce sul conto, non la media delle percentuali."""
    if not gruppo:
        return 0.0
    return sum(1 + t["rendimento"] for t in gruppo) / len(gruppo) - 1


def intervallo_bootstrap(gruppo, rnd, giri=300):
    """Intervallo al 95% con ricampionamento A BLOCCHI TEMPORALI.

    Ricampionare i singoli token darebbe intervalli molto piu' stretti del vero, perche' i token
    contemporanei non sono osservazioni indipendenti: si muovono insieme. Si ricampionano i
    blocchi, non le righe."""
    if len(gruppo) < 30:
        return None
    per_blocco = {}
    for t in gruppo:
        per_blocco.setdefault(t["blocco_tempo"], []).append(t)
    blocchi = list(per_blocco.values())
    medie = []
    for _ in range(giri):
        scelti = [rnd.choice(blocchi) for _ in range(len(blocchi))]
        piatto = [t for b in scelti for t in b]
        medie.append(media_portafoglio(piatto))
    medie.sort()
    return medie[int(0.025 * len(medie))], medie[int(0.975 * len(medie))]


def cerca(token, rnd, min_cella):
    """La ricerca: prova le condizioni e i loro accoppiamenti, e promuove se trova qualcosa.

    Questa e' la parte che deve somigliare al motore vero, altrimenti la prova non dice niente
    sul motore vero. Profondita' massima DUE condizioni, come da metodo."""
    tagli = [0.25, 0.5, 0.75]
    regole = []
    for c in CONDIZIONI:
        for s in tagli:
            regole.append([(c, s, True)])
            regole.append([(c, s, False)])
    for i, a in enumerate(CONDIZIONI):
        for b in CONDIZIONI[i + 1:]:
            for sa in tagli:
                for sb in tagli:
                    regole.append([(a, sa, True), (b, sb, True)])

    tentati = 0
    promossi = []
    for regola in regole:
        gruppo = [t for t in token
                  if all((t[c] >= s) if verso else (t[c] < s) for c, s, verso in regola)]
        if len(gruppo) < min_cella:
            continue
        tentati += 1
        iv = intervallo_bootstrap(gruppo, rnd)
        if iv and iv[0] > 0:                       # il criterio del metodo: limite basso sopra zero
            promossi.append({"regola": [[c, s, v] for c, s, v in regola],
                             "n": len(gruppo),
                             "media": round(media_portafoglio(gruppo), 4),
                             "iv_basso": round(iv[0], 4)})
    return tentati, promossi


def main():
    min_cella = int(os.environ.get("MIN_CELLA", 200))
    rnd = random.Random(SEME)
    promozioni = 0
    tentati_tot = 0
    esempi = []
    for giro in range(N_PROVE):
        token = mondo(rnd)
        tentati, promossi = cerca(token, rnd, min_cella)
        tentati_tot += tentati
        if promossi:
            promozioni += 1
            if len(esempi) < 3:
                esempi.append(max(promossi, key=lambda p: p["iv_basso"]))
        if (giro + 1) % 25 == 0:
            print(f"   ...{giro + 1}/{N_PROVE} mondi, promozioni finora {promozioni}", flush=True)

    # LA PROVA COMPLEMENTARE: con un vantaggio vero dentro, la macchina lo vede?
    visti = 0
    giusti = 0
    for _ in range(max(10, N_PROVE // 4)):
        token = mondo_con_vantaggio(rnd)
        _, promossi = cerca(token, rnd, min_cella)
        if promossi:
            visti += 1
            # ha trovato PROPRIO quella condizione, o un'altra a caso?
            for p in promossi:
                cond = {c for c, _, _ in p["regola"]}
                if cond <= {"liquidita", "compratori"} and cond:
                    giusti += 1
                    break
    n_con = max(10, N_PROVE // 4)
    quota = 100 * promozioni / max(1, N_PROVE)
    print()
    print(f"MOTORE A VUOTO | {N_PROVE} mercati SENZA alcun vantaggio da trovare")
    print(f"   confronti tentati per mercato: ~{tentati_tot // max(1, N_PROVE)}")
    print(f"   mercati in cui la macchina ha promosso qualcosa: {promozioni} = {quota:.1f}%")
    print(f"   soglia dichiarata: {SOGLIA_ALLARME}%")
    print()
    print(f"MOTORE CON UN VANTAGGIO VERO DENTRO | {n_con} mercati")
    print(f"   mercati in cui ha promosso qualcosa: {visti} = {100*visti/n_con:.0f}%")
    print(f"   di cui ha nominato la condizione GIUSTA: {giusti} = {100*giusti/n_con:.0f}%")
    if visti == 0:
        print("   ATTENZIONE: e' cieca. Non promuove nemmeno quando il vantaggio c'e' davvero,")
        print("   quindi superare la prova del mercato vuoto non significa niente.")
    print()
    if esempi:
        print("   esempi di cose «trovate» che NON esistono:")
        for e in esempi:
            regola = " e ".join(f"{c} {'≥' if v else '<'} {s}" for c, s, v in e["regola"])
            print(f"      {regola}  ->  {e['n']} token, media {100*e['media']:+.1f}%, "
                  f"limite basso {100*e['iv_basso']:+.1f}%")

    os.makedirs(os.path.dirname(FUORI), exist_ok=True)
    json.dump({"prove": N_PROVE, "promozioni": promozioni, "quota_pct": round(quota, 2),
               "min_cella": min_cella, "soglia": SOGLIA_ALLARME, "seme": SEME},
              open(FUORI, "w"), indent=1)

    if quota > SOGLIA_ALLARME:
        print()
        print(f"   VERDETTO: la macchina promuove nel {quota:.1f}% dei casi su dati VUOTI.")
        print(f"   Una promozione sui dati veri varrebbe quanto queste. NON e' validata.")
        print(f"   Non si abbassa la soglia: si rende la ricerca piu' severa (celle piu' grandi,")
        print(f"   meno condizioni, conferma su dati mai visti) finche' questa quota non scende.")
        sys.exit(1)
    print()
    print(f"   VERDETTO: la macchina dice di no nel {100 - quota:.1f}% dei casi in cui deve.")
    print(f"   Questo NON dimostra che trovera' qualcosa di vero: dimostra che non e' una")
    print(f"   macchina che trova sempre qualcosa.")
    sys.exit(0)


if __name__ == "__main__":
    main()
