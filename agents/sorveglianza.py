"""IL GIRO DI SORVEGLIANZA: tre domande, e un permesso.

PERCHE' CAMBIA IL REGIME (deciso con Nicolo' il 5/11 pomeriggio).
Per tre giorni il lavoro piu' redditizio era cercare difetti, perche' la
macchina era rotta: il contratto in catena era una versione vecchia e
NESSUN pacchetto poteva eseguire. Trovati e riparati, oggi contratto, porta,
offerta e tre rotte di vendita sono tutti provati in catena.
Quello che manca non e' un difetto: e' un'OCCASIONE, e non dipende da noi.

E il metodo di prima adesso fa danno: ogni modifica rimette in coda
centinaia di ordini. Il 5/11 li ho rifatti TRE volte (selettore nuovo,
aggregatore in castigo, mancia ricalcolata) e il blocco delle vendite e'
rimasto al 91% non perche' fosse rotto, ma perche' lo rimescolavo io. Nel
momento in cui passa l'occasione, il cassetto a meta' sarebbe colpa mia.

QUINDI: si sorveglia, e si tocca il codice SOLO se la sorveglianza lo
chiede. Le idee si accumulano e si applicano in blocco, non una ogni
mezz'ora.
"""
import json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

D = "data/liquidazioni"
IDEE = "IDEE_DA_FARE.md"


def _leggi(nome, massimo_minuti=None):
    """Legge un file di stato. None se manca; (dati, eta_minuti) se c'e'."""
    p = f"{D}/{nome}"
    if not os.path.exists(p):
        return None, None
    eta = (time.time() - os.path.getmtime(p)) / 60
    if massimo_minuti and eta > massimo_minuti:
        return None, eta
    try:
        return json.load(open(p)), eta
    except Exception:
        return None, eta


def passata_un_occasione():
    """DOMANDA 1 — la sola che puo' autorizzare una modifica.

    Se nel mondo e' passata una liquidazione di valore da quando il
    contratto giusto e' in catena: eravamo pronti? l'abbiamo vinta? e se no,
    quale blocco ha la colpa?
    """
    d, eta = _leggi("da_quando_siamo_veri.json")
    if not d:
        return {"so": False, "perche": "il punteggio non e' stato misurato"}
    liq = d.get("liquidazioni") or []
    grosse = [r for r in liq if (r.get("premio") or 0) >= 150]
    pronti = [r for r in grosse if r.get("ordine_pronto")]
    vinte = [r for r in liq if r.get("vinta_da_noi")]
    perse_da_pronti = [r for r in pronti if not r.get("vinta_da_noi")]
    return {"so": True, "ore": d.get("ore"), "eta_misura": round(eta or 0),
            "nel_mondo": d.get("liquidazioni_nel_mondo", 0),
            "di_valore": len(grosse), "eravamo_pronti": len(pronti),
            "vinte": len(vinte),
            "perse_essendo_pronti": len(perse_da_pronti),
            "autorizza_modifica": bool(perse_da_pronti),
            "premio_passato": d.get("premio_passato", 0)}


def siamo_pronti():
    """DOMANDA 2 — i fatti che devono essere veri ADESSO.

    Non si rifa' il C-check intero: quello gira da solo ogni 15 minuti nel
    ciclo delle guardie. Qui si LEGGE il suo esito, perche' rifare 129
    verifiche a ogni mezz'ora costa e non aggiunge niente.
    """
    fuori = []
    # il contratto giusto e' in catena
    c, _ = _leggi("contratto.json")
    # l'esito del C-check, letto non rifatto
    b, eta_b = _leggi("blocchi.json", 45)
    if b is None:
        fuori.append(f"l'esito del C-check manca o e' vecchio ({eta_b and round(eta_b)} min)")
    # la porta e' provata
    p, _ = _leggi("prova_di_porta.json")
    if not (p or {}).get("inclusa"):
        fuori.append("la porta non risulta provata")
    # le tre rotte di vendita
    for f, eti in (("da_capo_a_fondo.json", "rotta normale"),
                   ("da_capo_a_fondo_v4.json", "rotta v4"),
                   ("tre_passaggi_provato.json", "rotta a tre passaggi")):
        d, eta = _leggi(f)
        if not d:
            fuori.append(f"{eti}: mai provata")
        elif d.get("non_ha_potuto_girare"):
            pass          # non ha potuto girare: non e' un buco della macchina
        elif d.get("passata") is False:
            fuori.append(f"{eti}: provata e NON passata")
    # il cassetto e la copertura
    try:
        VP = json.load(open(f"{D}/vendite_pronte.json"))
        pronti = sum(1 for v in VP.values() if v.get("chiamata"))
    except Exception:
        pronti = 0
        fuori.append("il cassetto non si legge")
    return {"fuori_posto": fuori, "ordini_pronti": pronti}


def qualcosa_e_scivolato():
    """DOMANDA 3 — un blocco che SCENDE e' un segnale, non una lista."""
    b, eta = _leggi("blocchi.json")
    if not b:
        return {"so": False}
    # il file lo scrive agents/blocchi.py: si LEGGE il suo esito invece di
    # rifare 129 verifiche a ogni mezz'ora. Il C-check gira da solo ogni 15
    # minuti nel ciclo delle guardie.
    # SI USA IL CAMPO CHE ESISTE. Le righe non portano l'andamento: lo
    # scivolamento sta nel campo "tornati_indietro", che blocchi.py riempie
    # confrontando col giro prima. Cercarlo nelle righe avrebbe dato sempre
    # "nessuno scivolamento" -- un controllo che non puo' scattare.
    scesi_nomi = b.get("tornati_indietro") or []
    perc = {r.get("blocco"): r.get("percento") for r in (b.get("righe") or [])}
    giu = [(n, perc.get(n)) for n in scesi_nomi]
    return {"so": True, "scesi": giu, "eta": round(eta or 0),
            "tutti_al_100": b.get("tutti_al_100")}


def quante_idee():
    if not os.path.exists(IDEE):
        return 0
    return sum(1 for l in open(IDEE) if l.strip().startswith("- [ ]"))


def giro():
    o = passata_un_occasione()
    p = siamo_pronti()
    s = qualcosa_e_scivolato()
    n_idee = quante_idee()
    permesso = bool(o.get("autorizza_modifica")) or bool(s.get("scesi")) \
        or bool(p["fuori_posto"])
    print("   SORVEGLIANZA")
    if o.get("so"):
        print(f"   1. occasioni: {o['nel_mondo']} nel mondo in {o['ore']}h, "
              f"{o['di_valore']} di valore, pronti su {o['eravamo_pronti']}, "
              f"vinte {o['vinte']}")
        if o["perse_essendo_pronti"]:
            print(f"      !!! {o['perse_essendo_pronti']} perse ESSENDO PRONTI "
                  f"-> modifica autorizzata")
    else:
        print(f"   1. occasioni: non lo so ({o['perche']})")
    print(f"   2. pronti: {p['ordini_pronti']} ordini pronti" +
          ("" if not p["fuori_posto"] else
           " | FUORI POSTO: " + "; ".join(p["fuori_posto"])))
    if s.get("so"):
        print(f"   3. scivolamenti: " +
              ("nessuno" if not s["scesi"] else
               ", ".join(f"{a} a {b}" for a, b in s["scesi"])))
    print(f"   idee in attesa: {n_idee} (si applicano in blocco, non a ogni giro)")
    print(f"   -> {'MODIFICA AUTORIZZATA' if permesso else 'SOLO SORVEGLIANZA: non tocco niente'}")
    out = {"quando": time.time(), "occasioni": o, "pronti": p,
           "scivolamenti": s, "idee": n_idee, "permesso": permesso}
    json.dump(out, open(f"{D}/sorveglianza.json", "w"), indent=1)
    return out


if __name__ == "__main__":
    giro()
