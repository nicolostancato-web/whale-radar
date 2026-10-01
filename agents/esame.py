"""ESAME DEL DATABASE — l'unica cosa che può dire «no, non ancora».

PERCHE' ESISTE (21/09). La revisione esterna ha trovato il difetto piu' scomodo della giornata, e
non era un bug: *«database affidabile non e' una condizione soddisfatta: e' un'etichetta senza test
di accettazione verificabile»*. Avevamo percentuali che cambiavano ogni ora e soglie scelte da me,
ma nessun criterio che potesse dire NO.

E' esattamente cosi' che due mesi fa un database e' stato dichiarato buono: non perche' i numeri
fossero alti, ma perche' non c'era niente che potesse bocciarlo. Un mese e mezzo di analisi buttato.

LE SOGLIE SONO SCRITTE PRIMA DI SAPERE SE LE PASSEREMO. Se le scrivessi dopo aver guardato i
risultati, sceglierei quelle che passano — senza nemmeno accorgermene. Questo file nasce il 21/09
alle 16:00, con robinhood al 50% e base all'87%: nessuna delle due passa oggi, ed e' giusto cosi'.

OGNI CONDIZIONE DICHIARA LA SUA POPOLAZIONE. La critica piu' seria che abbiamo ricevuto e' che le
nostre percentuali erano calcolate su insiemi scelti da noi — il 41% dichiarato contro il 24% vero,
il 95,3% misurato su 3.613 pool mentre la popolazione ne ha 7.690. Qui ogni numero porta scritto
su cosa e' calcolato, e il denominatore non puo' essere il sottoinsieme che ci conviene.

I FILE CALDI SONO ESCLUSI, E DICHIARATO. La riparazione non tocca i file che i raccoglitori stanno
scrivendo: se lo facesse si cancellerebbero il lavoro a vicenda. Quindi il tetto raggiungibile non
e' il 100% ma circa il 97,5%, e la condizione si misura sui file FREDDI. Escluderli e' legittimo;
escluderli in silenzio no.
"""
import gzip
import hashlib
import json
import os
import sys
import time

CAMPIONE = int(os.environ.get("CAMPIONE", 40))
FREDDO = 7200
MARCHIO_SOSPETTO = 1789986813
# vedi ripara_orario: su base i timbri anteriori alla correzione dell'abbinamento (22/09 02:35
# UTC) non provano niente, perche' il riparatore accoppiava le risposte per posizione. Su
# robinhood valgono: 120 record su 120 verificati corretti contro la catena.
VALIDA_DA = {"base": 1790041500}
SCRITTO_IL = "2026-09-21 16:00 UTC"

# ---------------------------------------------------------------- le soglie, dichiarate prima
SOGLIE = {
    "istanti_freddi": 95.0,      # % di record in file freddi con orario chiesto alla catena
    "marchi_sospetti": 0.5,      # % massima di marchi non riverificati
    "coppie": 95.0,              # % di pool della popolazione con la coppia di token risolta
}


def misura(chain):
    ch = chain
    ora = time.time()
    tot = freddi = freddi_ok = sospetti = 0
    for sub in ("storico", "vivo"):
        d = f"data/multichain/{chain}/{sub}"
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if int(hashlib.md5(fn.encode()).hexdigest()[:4], 16) % CAMPIONE:
                continue
            try:
                righe = [json.loads(l) for l in gzip.open(os.path.join(d, fn), "rt") if l.strip()]
            except Exception:
                continue
            if not righe:
                continue
            caldo = (ora - max((r.get("acq") or 0) for r in righe)) < FREDDO
            for r in righe:
                tot += 1
                # L'ESAME MISURA CIO' CHE E' DIMOSTRABILE (22/09). Contava come verificato tutto
                # cio' che portava l'etichetta «orario: catena» — che pero' la scriveva anche il
                # codice vecchio. Adesso conta solo cio' che porta la DATA della verifica, e i
                # sospetti sono i record etichettati ma senza quella data.
                _ok = bool(r.get("ver")) and r["ver"] >= VALIDA_DA.get(ch, 0)
                if r.get("orario") == "catena" and not _ok:
                    sospetti += 1
                if caldo:
                    continue
                freddi += 1
                if bool(r.get("ver")) and r["ver"] >= VALIDA_DA.get(ch, 0):
                    freddi_ok += 1
    return {
        "righe": tot,
        "freddi": freddi,
        "istanti_freddi": round(100 * freddi_ok / max(1, freddi), 1),
        "marchi_sospetti": round(100 * sospetti / max(1, tot), 1),
    }


def coppie(chain):
    """Sulla POPOLAZIONE definita, non sui pool che abbiamo gia' risolto.

    Contare «risolte / tentate» darebbe sempre quasi 100%: e' la stessa auto-selezione che ci ha
    fatto dichiarare 41% dove il vero era 24%."""
    # LA FORMA DEL FILE SI LEGGE, NON SI INDOVINA (21/09). Avevo scritto una lettura «elastica»
    # che provava due strutture possibili, e non trovandole tornava un insieme VUOTO: l'esame
    # dichiarava «0,0% su 2 pool» e bocciava per un difetto mio, non del database.
    # Un esame che boccia per un proprio errore di lettura e' inutile quanto uno che non boccia
    # mai: in entrambi i casi il verdetto non parla del database. La struttura vera e'
    # {"chain": {"base": {"n": 8869, "pool": [...]}}} e adesso e' letta cosi', senza ripieghi.
    try:
        pop = json.load(open("data/popolazione_congelata.json"))["chain"][chain]
        insieme = set(pop["pool"])
    except Exception as e:
        print(f"     (popolazione congelata illeggibile per {chain}: {type(e).__name__})")
        insieme = set()
    try:
        c = json.load(open(f"data/multichain/{chain}/coppie.json")).get("coppie", {})
    except Exception:
        c = {}
    if not insieme:
        return None, 0, 0
    risolti = sum(1 for p in insieme if p in c)
    return round(100 * risolti / max(1, len(insieme)), 1), risolti, len(insieme)


def main():
    print(f"ESAME DEL DATABASE — soglie scritte il {SCRITTO_IL}, prima di sapere se le passiamo\n")
    esiti = []
    for ch in ("base", "robinhood"):
        m = misura(ch)
        pc, ris, tot_pop = coppie(ch)
        print(f"  {ch.upper()}  (campione 1 file su {CAMPIONE}: {m['righe']} righe)")

        for nome, valore, soglia, verso, su in (
                ("istanti verificati", m["istanti_freddi"], SOGLIE["istanti_freddi"], ">=",
                 f"{m['freddi']} record in file FREDDI"),
                ("marchi sospetti", m["marchi_sospetti"], SOGLIE["marchi_sospetti"], "<=",
                 f"{m['righe']} record"),
                ("coppie risolte", pc, SOGLIE["coppie"], ">=",
                 f"{tot_pop} pool della popolazione congelata")):
            if valore is None:
                print(f"     {nome:<22} NON MISURABILE  (manca la popolazione congelata per "
                      f"questa chain)")
                esiti.append(False)
                continue
            ok = valore >= soglia if verso == ">=" else valore <= soglia
            esiti.append(ok)
            print(f"     {nome:<22} {valore:>6.1f}%  {verso} {soglia}%   "
                  f"{'PASSA' if ok else 'NON PASSA'}   su {su}")
        print()

    # UN ESAME CHE NON PUO' BOCCIARE NON E' UN ESAME. Il verdetto e' uno solo per tutti:
    # basta una condizione fuori soglia e il database non e' pronto.
    if all(esiti):
        print("VERDETTO: il database PASSA tutte le condizioni dichiarate.")
        print("          Questo NON dimostra che sia corretto: dimostra che ha superato le prove")
        print("          che avevamo il coraggio di scrivere prima di guardare i risultati.")
        sys.exit(0)
    print(f"VERDETTO: NON PRONTO — {sum(1 for e in esiti if not e)} condizioni su {len(esiti)} "
          f"fuori soglia.")
    print("          Il loop 1 resta fermo. Riaccenderlo adesso ripeterebbe l'errore di luglio:")
    print("          un mese e mezzo di analisi su dati che non reggevano.")
    sys.exit(1)


if __name__ == "__main__":
    main()
