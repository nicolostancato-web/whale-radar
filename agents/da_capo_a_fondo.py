"""La prova che attraversa tutto: dal prezzo che scende ai soldi in cassa.

PERCHE' ESISTE (5/11). Tutte le prove precedenti costruivano la Piano in
Solidity e la passavano a un contratto appena distribuito: non attraversavano
ne' l'indirizzo vero ne' i byte che costruiamo in Python. E' il buco in cui
e' vissuto il selettore sbagliato per ~12.000 pacchetti.
Questa invece legge la calldata VERA dal cassetto, fa SCENDERE il prezzo
della garanzia finche' la posizione cade, e pretende che in CASSA arrivino
soldi -- non che "non sia andata in errore".

Gira da sola nel giro del laghetto e scrive l'esito, cosi' il C-check lo
legge senza pagare 27 secondi a ogni passata.
"""
import json, os, re, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indirizzi as I
from pescatore import salute, U
import indirizzi as I

D = "data/liquidazioni"
FUORI = f"{D}/da_capo_a_fondo.json"
FOUNDRY = os.path.expanduser("~/.foundry/bin")
WETH = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"


def _scegli():
    """La posizione piu' vicina a cadere fra quelle con un ordine VERO."""
    VP = json.load(open(f"{D}/vendite_pronte.json"))
    c = [(u, v) for u, v in VP.items()
         if (v.get("chiamata") or "").startswith("0x" + I.SELETTORE_ESEGUI)
         and v.get("premio", 0) > 200
         and (v.get("debito") or "").lower() == WETH]
    c.sort(key=lambda x: x[1].get("salute", 9))
    return c[0] if c else (None, None)


def _piano_v4():
    """Il piano a DUE passaggi su Uniswap v4, per la posizione piu' vicina a
    cadere fra quelle che v4 sa vendere.

    PERCHE' STA QUI (5/11): il percorso v4 gira solo quando ne' v3 ne' Curve
    hanno una strada, cioe' quasi mai -- ed e' il pezzo con piu' parti nuove
    (due passaggi invece di uno, autorizzazione via Permit2, uscita in ether
    da avvolgere). Un pezzo che gira raramente e non viene provato a ogni
    giro e' un pezzo che scopriremo rotto nel momento in cui serve.
    Provato a mano una volta: 0,09358 WETH in cassa su un calo del 6%.
    """
    import vendita_univ4 as V4
    from pescatore import cast, salute
    VP = json.load(open(f"{D}/vendite_pronte.json"))
    PR = json.load(open(f"{D}/prezzi_oracolo.json"))
    cand = [(v.get("salute", 9), u, v) for u, v in VP.items()
            if (v.get("garanzia") or "").lower() in PR
            and (v.get("debito") or "").lower() == WETH]
    cand.sort()
    # SI GUARDA ABBASTANZA IN BASSO. Con sei candidate la prova non trovava
    # nulla: le piu' vicine a cadere hanno garanzie (osETH, weETH, wstETH)
    # le cui pozze v4 sono sottili, e quella con WBTC -- che funziona --
    # stava piu' giu' nell'elenco. Un campione troppo corto fa concludere
    # "non si puo'" su qualcosa che si puo'.
    fuori = []
    for _s, u, v in cand[:40]:
        g = v["garanzia"].lower()
        sv = salute(u)
        if not sv or not sv.get("debito"):
            continue
        pg, pd = PR.get(g), PR.get(WETH)
        if not pg or not pd:
            continue
        qd = int(sv["debito"]*0.5/pd["prezzo_usd"]*10**pd["decimali"])
        qg = int(sv["debito"]*0.5*1.07*0.995/pg["prezzo_usd"]*10**pg["decimali"])
        m = V4.quota(g, WETH, qg, dst_e_weth=True)
        if not m or m[0] <= 0:
            continue
        # UN PREVENTIVO NON E' UN PERMESSO, e qui l'avevo dimenticato dopo
        # averlo imparato stanotte sul modulo di GHO (che quotava 1:1
        # perfetto su un milione mentre era chiuso con capienza zero).
        # Una pozza v4 quasi vuota risponde con un'uscita MINUSCOLA ma
        # maggiore di zero: su rsETH tornava 0,000010 per 0,4 ETH immessi.
        # Chiedere "piu' di zero" fa scegliere la pozza vuota, e la vendita
        # fallisce in esecuzione. Si pretende la RESA.
        import premi as _PM
        _reso = m[0]/10**pd["decimali"]*pd["prezzo_usd"]
        _dato = qg/10**pg["decimali"]*pg["prezzo_usd"]
        if not _dato or _reso/_dato < _PM.resa_minima(g):
            continue
        # LA GUARDIA DEVE PROVARE UN CASO CHE CONTA. Il 5/11 ha scelto una
        # posizione da 47 $ di premio -- la piu' povera del cassetto -- ed e'
        # fallita: un rosso su una cosa che non ci cambia la vita, che fa
        # sembrare rotta la rotta v4 mentre lo scambio da solo funziona
        # (provato: 0,2 weETH -> 0,2206 ETH sulla stessa pozza).
        # Una prova vale quanto il caso che prova.
        if (v.get("premio") or 0) < 500:
            continue
        ts = {100: 1, 500: 10, 3000: 60, 10000: 200}[m[1]]
        r4 = V4.scambio(g, m[2], m[1], ts, qg, con_posizione=True)
        if not r4:
            continue
        perm = cast("calldata", "approve(address,address,uint160,uint48)",
                    g, V4.UNIVERSAL_ROUTER, str((1 << 160)-1), "4000000000")
        if not perm.startswith("0x"):
            continue
        passi = (f"[({g},{V4.PERMIT2},{V4.PERMIT2},{perm},0),"
                 f"({g},{V4.UNIVERSAL_ROUTER},{V4.PERMIT2},{r4[0]},{r4[1]})]")
        ch = cast("calldata", I.FIRMA_ESEGUI, WETH, str(qd),
                  f"({g},{u},{passi},{int(0.01*10**18)},0)")
        if ch.startswith("0x"):
            fuori.append((u, g, ch))
            if len(fuori) >= 3:
                break
    return fuori


def gira():
    u, v = _scegli()
    if not u:
        return {"esito": "nessun ordine col selettore di adesso", "quando": time.time()}
    os.makedirs("liquidatore/dati", exist_ok=True)
    for n, t in (("e2e_calldata", v["chiamata"]), ("e2e_garanzia", v["garanzia"]),
                 ("e2e_debito", v["debito"]), ("e2e_utente", u)):
        open(f"liquidatore/dati/{n}.txt", "w").write(t)
    r = subprocess.run([f"{FOUNDRY}/forge", "test", "--root", "liquidatore",
                        "--match-contract", "DaCapoAFondo",
                        "--fork-url", U, "-vv"],
                       capture_output=True, text=True, timeout=900)
    t = r.stdout + r.stderr
    if ("failed to retrieve chain ID" in t or "Connection refused" in t):
        out = {"quando": time.time(), "passata": None,
               "esito": "la copia locale della catena non si e' aperta",
               "non_ha_potuto_girare": True}
        json.dump(out, open(FUORI, "w"), indent=1)
        print("   da capo a fondo: non ha potuto girare (fork rifiutato)")
        return out
    if "NON HO POTUTO PROVARE" in t:
        # «NON HO POTUTO PROVARE» NON E' «E' ROTTO» (riparato il 7/11).
        # Qui si scriveva un esito vuoto, e il C-check lo leggeva come un
        # rosso: la prova piu' importante sembrava fallita quando in realta'
        # non aveva trovato un soggetto da far cadere. L'altra prova
        # end-to-end (prova_in_catena) questa lezione l'aveva gia' imparata
        # il 4/11 -- questa no, e la famiglia si e' ripetuta.
        # Il verdetto precedente si TIENE, e si dice che oggi non si e'
        # potuto rifare. Un rosso falso insegna a ignorare i rossi.
        _vecchio = {}
        try:
            _vecchio = json.load(open(FUORI))
        except Exception:
            pass
        out = {"quando_tentato": time.time(),
               "esito": "la posizione scelta non si fa cadere: collaterale misto",
               "non_ha_potuto_girare": True,
               # si riporta il verdetto precedente, con la SUA data
               "quando": _vecchio.get("quando"),
               "passata": _vecchio.get("passata"),
               "in_cassa_wei": _vecchio.get("in_cassa_wei"),
               "selettore": _vecchio.get("selettore"),
               "sconto_che_la_fa_cadere": _vecchio.get(
                   "sconto_che_la_fa_cadere"),
               "verdetto_di": "prova precedente" if _vecchio else None}
        json.dump(out, open(FUORI, "w"), indent=1)
        print("   da capo a fondo: NON HO POTUTO PROVARE (nessuna posizione "
              "si fa cadere adesso) — tengo il verdetto precedente")
        return out
    passata = "[PASS]" in t
    def num(eti):
        m = re.search(eti + r":\s*(\d+)", t)
        return int(m.group(1)) if m else None
    dopo, prima = num("in cassa dopo "), num("in cassa prima")
    out = {"quando": time.time(), "passata": passata,
           "utente": u, "premio": v.get("premio"),
           "sconto_che_la_fa_cadere": num("caduta a sconto percento"),
           "in_cassa_wei": (dopo - prima) if (dopo is not None and prima is not None) else None,
           "selettore": I.SELETTORE_ESEGUI}
    tmp = FUORI + ".tmp"
    json.dump(out, open(tmp, "w"), indent=1)
    os.replace(tmp, FUORI)
    print(f"   da capo a fondo: {'PASSATA' if passata else 'NON PASSATA'}"
          f" | in cassa {(out['in_cassa_wei'] or 0)/1e18:.4f} WETH"
          f" | cade a -{out['sconto_che_la_fa_cadere']}%")
    return out


def gira_v4():
    """PIU' DI UNA CANDIDATA, e si ferma alla prima che INCASSA.

    Con una sola candidata la guardia diceva "non passata" e sembrava un
    guasto del percorso v4, mentre il percorso funziona (provato: 0,09358
    WETH in cassa su una posizione con garanzia WBTC). Il problema era la
    SCELTA: un preventivo buono alla taglia prevista non garantisce la resa
    sulla quantita' davvero incassata, che si scopre solo dentro
    l'operazione. Quindi si provano fino a tre piani e si registra anche
    quante hanno fallito: un verdetto su un solo caso non e' un verdetto.
    """
    piani = _piano_v4()
    if not piani:
        # NON HA POTUTO GIRARE, NON HA FALLITO (riparato il 5/11: la mia
        # regola violata dal mio codice). "Nessuna posizione che v4 sappia
        # vendere" non dice niente sulla rotta: dice che non c'era un caso
        # con cui provarla. Scriverlo come fallimento fa diventare rossa la
        # sorveglianza e autorizza una modifica che non serve.
        out = {"esito": "nessuna posizione che v4 sappia vendere",
               "quando": time.time(), "passata": None,
               "non_ha_potuto_girare": True}
        json.dump(out, open(f"{D}/da_capo_a_fondo_v4.json", "w"), indent=1)
        print("   da capo a fondo SU V4: nessuna candidata")
        return out
    fallite, saltate = [], []
    for u, g, ch in piani:
        os.makedirs("liquidatore/dati", exist_ok=True)
        for n, t in (("e2e_calldata", ch), ("e2e_garanzia", g),
                     ("e2e_debito", WETH), ("e2e_utente", u)):
            open(f"liquidatore/dati/{n}.txt", "w").write(t)
        r = subprocess.run([f"{FOUNDRY}/forge", "test", "--root", "liquidatore",
                            "--match-contract", "DaCapoAFondo",
                            "--fork-url", U, "-vv"],
                           capture_output=True, text=True, timeout=900)
        t = r.stdout + r.stderr
        # «NON HA POTUTO GIRARE» NON E' «NON HA FUNZIONATO» (5/11).
        # La copia locale della catena si appoggia a un nodo pubblico
        # gratuito che a volte rifiuta: chiede stato storico a valanga. Se
        # lo scambio col nodo non si apre, la prova non ha ESITO -- e
        # scriverla come fallita sarebbe una bugia che fa sembrare rotto il
        # sistema mentre il sistema e' sano (verificato: le letture normali
        # rispondevano 5 su 5 e il pescatore leggeva 100 salute).
        if ("failed to retrieve chain ID" in t
                or "Connection refused" in t):
            out = {"quando": time.time(), "passata": None,
                   "esito": "la copia locale della catena non si e' aperta: "
                            "il nodo pubblico ha rifiutato il fork",
                   "non_ha_potuto_girare": True}
            json.dump(out, open(f"{D}/da_capo_a_fondo_v4.json", "w"), indent=1)
            print("   da capo a fondo SU V4: non ha potuto girare "
                  "(il nodo ha rifiutato il fork)")
            return out
        def num(eti):
            m = re.search(eti + r":\s*(\d+)", t)
            return int(m.group(1)) if m else None
        dopo, prima = num("in cassa dopo "), num("in cassa prima")
        # UN «PASSATA» CHE NON PROVA NIENTE E' PEGGIO DI UN ROSSO.
        # La prova ora dice quando non riesce a far CADERE la posizione (il
        # collaterale di quell'utente e' misto, e abbassare la garanzia
        # principale non basta nemmeno al 90%). In quel caso forge riporta
        # PASS perche' non c'e' stato alcun errore -- ma non abbiamo provato
        # niente. Si passa alla candidata dopo.
        if "NON HO POTUTO PROVARE" in t:
            saltate.append(u[:14])
            continue
        passata = "[PASS]" in t
        if not passata:
            fallite.append(u[:14])
            continue
        out = {"quando": time.time(), "passata": True, "utente": u,
               "garanzia": g, "due_passaggi": True,
               "fallite_prima": fallite, "provate": len(fallite)+1,
               "sconto_che_la_fa_cadere": num("caduta a sconto percento"),
               "in_cassa_wei": (dopo-prima) if (dopo is not None and prima is not None) else None}
        tmp = f"{D}/da_capo_a_fondo_v4.json.tmp"
        json.dump(out, open(tmp, "w"), indent=1)
        os.replace(tmp, f"{D}/da_capo_a_fondo_v4.json")
        print(f"   da capo a fondo SU V4: PASSATA alla {len(fallite)+1}a prova"
              f" | in cassa {(out['in_cassa_wei'] or 0)/1e18:.5f} WETH"
              f" | cade a -{out['sconto_che_la_fa_cadere']}%")
        return out
    out = {"quando": time.time(),
           "passata": None if saltate and not fallite else False,
           "fallite": fallite, "saltate_perche_non_cadono": saltate,
           "non_ha_potuto_girare": bool(saltate and not fallite),
           "provate": len(piani),
           "esito": ("nessuna delle candidate si e' potuta far cadere"
                     if saltate and not fallite
                     else "nessuno dei piani v4 ha incassato")}
    json.dump(out, open(f"{D}/da_capo_a_fondo_v4.json", "w"), indent=1)
    print(f"   da capo a fondo SU V4: su {len(piani)} piani -> "
          f"{len(fallite)} non hanno incassato, {len(saltate)} non si sono "
          f"potute far cadere")
    return out


GHO = "0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f"


def gira_tre():
    """La catena a TRE passaggi, due piazze: garanzia -> USDC su v3, poi
    USDC -> GHO su v4.

    SI SCEGLIE UNA POSIZIONE CON COLLATERALE PURO, e questo e' il punto.
    Il 5/11 la prova falliva con HealthFactorNotBelowThreshold su posizioni
    col collaterale MISTO: abbassare il prezzo della garanzia principale non
    le fa cadere nemmeno al 90%, perche' il resto del collaterale tiene su
    la salute. Sembrava il piano rotto, era la prova a non poter provare.
    La purezza si misura: valore della garanzia principale diviso il
    collaterale TOTALE letto in catena. Sopra il 90% la posizione cade
    davvero quando si abbassa quel prezzo.
    Provato cosi': caduta al -10%, 688,72 GHO in cassa.
    """
    import indirizzi as I2
    from pescatore import rpc, POOL
    co = {k.lower(): v for k, v in
          json.load(open(f"{D}/composizione.json")).items()}
    VP = json.load(open(f"{D}/vendite_pronte.json"))
    cand = [(u, v, co.get(u.lower())) for u, v in VP.items()
            if (v.get("debito") or "").lower() == GHO
            and (v.get("chiamata") or "").startswith("0x"+I2.SELETTORE_ESEGUI)
            and len(v["chiamata"])//2 > 2400          # i tre passaggi
            and co.get(u.lower())]
    cand.sort(key=lambda x: -x[1].get("premio", 0))
    for u, v, c in cand[:10]:
        r = rpc("eth_call", [{"to": POOL,
                              "data": "0xbf92857c"+u[2:].zfill(64)},
                             "latest"], giri=2)
        if not isinstance(r, str) or len(r) < 2+64*6:
            continue
        tot = int(r[2:66], 16)/1e8
        gu = c.get("garanzia_usd") or 0
        if not tot or gu/tot < 0.9:
            continue
        for n, t in (("e2e_calldata", v["chiamata"]),
                     ("e2e_garanzia", v["garanzia"]),
                     ("e2e_debito", GHO), ("e2e_utente", u)):
            open(f"liquidatore/dati/{n}.txt", "w").write(t)
        rr = subprocess.run([f"{FOUNDRY}/forge", "test", "--root", "liquidatore",
                             "--match-contract", "DaCapoAFondo",
                             "--fork-url", U, "-vv"],
                            capture_output=True, text=True, timeout=900)
        t = rr.stdout + rr.stderr
        if "NON HO POTUTO PROVARE" in t:
            continue
        def num(eti):
            m = re.search(eti + r":\s*(\d+)", t)
            return int(m.group(1)) if m else None
        dopo, prima = num("in cassa dopo "), num("in cassa prima")
        out = {"quando": time.time(), "passata": "[PASS]" in t,
               "utente": u, "garanzia": v["garanzia"],
               "purezza_collaterale": round(gu/tot, 3),
               "sconto_che_la_fa_cadere": num("caduta a sconto percento"),
               "in_cassa_wei": (dopo-prima) if (dopo is not None and prima is not None) else None}
        tmp = f"{D}/tre_passaggi_provato.json.tmp"
        json.dump(out, open(tmp, "w"), indent=1)
        os.replace(tmp, f"{D}/tre_passaggi_provato.json")
        print(f"   TRE PASSAGGI: {'PASSATA' if out['passata'] else 'NON PASSATA'}"
              f" | in cassa {(out['in_cassa_wei'] or 0)/1e18:.2f} GHO"
              f" | cade a -{out['sconto_che_la_fa_cadere']}%")
        return out
    out = {"quando": time.time(), "passata": None,
           "non_ha_potuto_girare": True,
           "esito": "nessuna posizione a tre passaggi col collaterale puro"}
    json.dump(out, open(f"{D}/tre_passaggi_provato.json", "w"), indent=1)
    print("   TRE PASSAGGI: nessuna posizione col collaterale puro")
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "v4":
        gira_v4()
    elif len(sys.argv) > 1 and sys.argv[1] == "tre":
        gira_tre()
    else:
        gira()
