"""CHI FA LE X, RIPETUTE — l'unico agente che produce casi da mostrare a Nicolo'.

Il suo scopo e' una frase sola, sua: «tu mi dai dei wallet e delle cripto, io guardo e dico: wow,
sto qua veramente ha fatto 10 per». Quindi non produce percentuali: produce **portafoglio +
moneta + le due transazioni**, e solo se ha superato i controlli.

== LE REGOLE, OGNUNA NATA DA UN ERRORE ==

1. **posizione intera** — letta dal blocco di nascita della moneta, non da una finestra di
   blocchi recenti (il 38% delle posizioni era una fetta della storia, mediana 25%);
2. **i gettoni venduti sono quelli comprati** (90-110%) — il «157x» era un portafoglio che
   vendeva 100 volte i gettoni che aveva comprato: un rapporto fra merci diverse;
3. **una sola valuta, dichiarata** — niente importi grezzi sommati fra asset diversi;
4. **lanciatori esclusi** — chi crea la moneta non e' bravo, e' il banco;
5. **gas incluso** — misurato, 0,000008135 nativi per giro completo;
6. **grappoli = una persona** — nove portafogli che comprano nella stessa transazione sono una
   decisione sola (19% delle posizioni sopra 2x veniva da un solo grappolo);
7. **ripetizione, non fortuna** — si guarda chi ha fatto X **piu' volte**, perche' un colpo solo
   su venti tentativi e' il caso;
8. **la prova prima del numero** — i casi in cima si ricalcolano dalla chain e, se non
   combaciano, NON si scrivono. E' il cancello che il 7/10 mancava.
"""
import collections
import glob
import gzip
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grappoli as GR                                        # noqa: E402
import riprova_dalla_chain as RC                             # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
DENTRO = os.environ.get("DENTRO", f"{BASE}/moneta_pezzo_*.jsonl.gz")
FUORI = os.environ.get("FUORI", f"{BASE}/chi_fa_le_x.json")
VERSIONE_ATTESA = 1
GAS = 0.000008135
SOGLIE = (2.0, 5.0, 10.0)
DA_PROVARE = int(os.environ.get("DA_PROVARE", "6"))


def main():
    lanci_p = f"{BASE}/curva_lanci.json.gz"
    if not os.path.exists(lanci_p):
        print("X | manca l'elenco dei lanci: non so chi sono i lanciatori. Non misuro.")
        return 0
    dl = json.load(gzip.open(lanci_p, "rt"))
    lanci, assets = dl["da"], dl.get("assets", {})
    creatori = {v["creatore"].lower() for v in lanci.values()}

    righe, versioni, visti = [], collections.Counter(), set()
    for p in sorted(glob.glob(DENTRO)):
        for ln in gzip.open(p, "rt"):
            if not ln.strip():
                continue
            x = json.loads(ln)
            versioni[x.get("v", "senza versione")] += 1
            if x.get("v") != VERSIONE_ATTESA:
                continue
            k = (x["chi"], x["moneta"])
            if k in visti:          # una sola riga per coppia, sempre
                continue
            visti.add(k)
            righe.append(x)
    sole = set(versioni)
    if sole and sole != {VERSIONE_ATTESA}:
        print(f"X | RIFIUTO: versioni mescolate {dict(versioni)}, attesa {VERSIONE_ATTESA}. "
              f"Sommare due generazioni di righe e' la causa del guadagno di 7.740 dollari "
              f"dove la chain diceva 3,36. Non misuro.")
        return 0
    print(f"X | {len(righe):,} posizioni intere", flush=True)
    if len(righe) < 200:
        print("X | troppo poche per dire qualcosa: non scrivo niente.")
        return 0

    sane = [r for r in righe
            if r["compra_valuta"] > 0 and r["compra_gettoni"] > 0 and not r.get("grezzo")
            and r["chi"] not in creatori
            and 0.9 <= r["vende_gettoni"] / r["compra_gettoni"] <= 1.1]
    for r in sane:
        r["x"] = (r["vende_valuta"] - GAS) / r["compra_valuta"]
    chiuse = [r for r in sane if r["vende_valuta"] > 0]
    print(f"X | {len(sane):,} sane, di cui {len(chiuse):,} chiuse "
          f"(mediana {statistics.median([r['x'] for r in chiuse]):.3f}x)" if chiuse else "X | nessuna chiusa")

    capo_di, gr, ref = GR.referto(sane)
    print(f"X | grappoli: {ref['grappoli']} ({ref['portafogli_in_grappolo']} portafogli, "
          f"{ref['quota_pct']}%; il piu' grande ne tiene {ref['piu_grande']})", flush=True)

    # PER PERSONA **E PER MONETA**, non per portafoglio (7/10, difetto trovato in un'ora).
    # La prima versione metteva in cima un attore con «9 tentativi, 6 sopra 2x»: guardando, i
    # nove portafogli avevano comprato UNA SOLA moneta nella stessa transazione. Una scommessa
    # replicata nove volte diventava nove tentativi e sei successi — una ripetizione FINTA,
    # cioe' precisamente cio' che cerchiamo di distinguere dalla fortuna.
    # Quindi una persona su una moneta e' **una posizione**: i soldi si sommano, il tentativo
    # resta uno.
    per_pos = collections.defaultdict(lambda: {"compra_valuta": 0.0, "vende_valuta": 0.0,
                                               "portafogli": set(), "tx_compra": [],
                                               "tx_vende": [], "simbolo": None})
    for r in sane:
        k = (capo_di.get(r["chi"], r["chi"]), r["moneta"])
        d = per_pos[k]
        d["compra_valuta"] += r["compra_valuta"]
        d["vende_valuta"] += r["vende_valuta"]
        d["portafogli"].add(r["chi"])
        d["simbolo"] = r.get("simbolo")
        for kk in ("tx_compra", "tx_vende"):
            for h in (r.get(kk) or []):
                if h not in d[kk] and len(d[kk]) < 3:
                    d[kk].append(h)
    print(f"X | {len(sane):,} righe per portafoglio -> {len(per_pos):,} posizioni per "
          f"persona-moneta (le scommesse replicate su piu' portafogli contano una volta)",
          flush=True)
    per_uno = collections.defaultdict(list)
    for (chi, mon), d in per_pos.items():
        d["x"] = (d["vende_valuta"] - GAS) / d["compra_valuta"] if d["compra_valuta"] > 0 else 0.0
        d["moneta"], d["chi"] = mon, chi
        per_uno[chi].append(d)

    classifica = []
    for chi, rs in per_uno.items():
        xs = [r["x"] for r in rs if r["vende_valuta"] > 0]
        if not xs:
            continue
        v = {s: sum(1 for x in xs if x >= s) for s in SOGLIE}
        classifica.append({"chi": chi, "tentativi": len(rs), "chiuse": len(xs),
                           "portafogli": len({w for r in rs for w in r["portafogli"]}),
                           "mediana": round(statistics.median(xs), 3),
                           "sopra": {str(s): v[s] for s in SOGLIE},
                           "migliore": round(max(xs), 3),
                           "capitale": round(sum(r["compra_valuta"] for r in rs), 6),
                           "simbolo": rs[0].get("simbolo")})
    # LA RIPETIZIONE PRIMA DEL PICCO: chi fa 2x cinque volte conta piu' di chi lo fa una volta.
    classifica.sort(key=lambda d: (-d["sopra"]["5.0"], -d["sopra"]["2.0"], -d["migliore"]))
    print("\nX | chi RIPETE (grappoli contati come una persona):")
    for d in classifica[:8]:
        print(f"   {d['chi'][:14]}…  tentativi {d['tentativi']:3}  "
              f">=2x {d['sopra']['2.0']:2}  >=5x {d['sopra']['5.0']:2}  "
              f">=10x {d['sopra']['10.0']:2}  migliore {d['migliore']:7.2f}x  "
              f"mediana {d['mediana']:.2f}x" + (f"  [{d['portafogli']} portafogli]" if d["portafogli"] > 1 else ""))

    # IL CANCELLO: i casi migliori si ricalcolano dalla chain. Chi non combacia NON esce.
    migliori = sorted([r for r in sane if r["vende_valuta"] > 0], key=lambda r: -r["x"])[:DA_PROVARE]
    # la prova resta per PORTAFOGLIO: una transazione appartiene a un indirizzo, non a un
    # grappolo. Il grappolo si dichiara accanto al caso, non ci si nasconde dentro.
    provati, bocciati = [], []
    for r in migliori:
        ok, guai, _ric = RC.caso_pulito(r["chi"], r["moneta"], r, None, lanci, assets)
        voce = {"portafoglio": r["chi"], "moneta": r["moneta"], "x": round(r["x"], 3),
                "speso": round(r["compra_valuta"], 9), "incassato": round(r["vende_valuta"], 9),
                "valuta": r.get("simbolo"), "acquisti": r.get("tx_compra", [])[:2],
                "vendite": r.get("tx_vende", [])[:3],
                "una_persona_con": sorted(gr.get(capo_di.get(r["chi"], r["chi"]), []))[:12]}
        (provati if ok else bocciati).append(voce if ok else {**voce, "perche": guai})
    print(f"\nX | casi provati sulla chain: {len(provati)} passano, {len(bocciati)} bocciati")
    for b in bocciati:
        print(f"   BOCCIATO {b['portafoglio'][:14]}…: {b['perche'][0][:90]}")
    for v in provati[:3]:
        print(f"   OK {v['x']:.2f}x  {v['portafoglio']}  su  {v['moneta']}")

    json.dump({"chain": CHAIN, "posizioni": len(righe), "sane": len(sane),
               "mediana_chiuse": round(statistics.median([r["x"] for r in chiuse]), 4) if chiuse else None,
               "grappoli": ref, "primi": classifica[:50],
               "casi_verificati": provati, "casi_bocciati": bocciati,
               "regole": ("posizione intera, gettoni che tornano 90-110%, una valuta sola, "
                          "lanciatori esclusi, gas incluso, grappoli come una persona, "
                          "ripetizione prima del picco, prova sulla chain prima di uscire")},
              open(FUORI, "w"), indent=1)
    print(f"X | scritto {FUORI}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
