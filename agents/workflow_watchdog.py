#!/usr/bin/env python3
"""
WORKFLOW_WATCHDOG — il guardiano dei REPARTI (workflow GitHub Actions). Gira ogni 2h e per OGNI workflow controlla:
  1) fallimenti veri (conclusion=failure) nelle ultime run → BUG, segnala
  2) workflow FERMO (nessuna run da > soglia) → cron rotto, lo RI-LANCIA da solo (auto-recovery)
  3) troppe cancellazioni → possibili sovrapposizioni, segnala
Scrive WATCHDOG.md con lo stato + le azioni prese, cosi' quando Nicolo chiede 'news?' il problema e' GIA' gestito.
Auto-recovery: ri-dispatcha i workflow fermi/falliti (workflow_dispatch), max 1 volta per giro. €0 (repo pubblico).
Usa GITHUB_TOKEN (automatico in Actions) e GITHUB_REPOSITORY. Nessun segreto hardcodato.
"""
import urllib.request, json, os, time, calendar

TOK = os.environ.get("GITHUB_TOKEN", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "nicolostancato-web/whale-radar")
API = f"https://api.github.com/repos/{REPO}/actions"
STALE_HOURS = 2.0          # se un workflow schedulato non gira da > 2h → probabilmente fermo
now = time.time()


def api(path, method="GET", body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(API + path, data=data, method=method,
        headers={"Authorization": f"token {TOK}", "Accept": "application/vnd.github+json",
                 "User-Agent": "whale-watchdog"})
    try:
        r = urllib.request.urlopen(req, timeout=25)
        return json.load(r) if method == "GET" else True
    except Exception as e:
        return None if method == "GET" else False


def age_h(iso):
    """Da quante ore e' successo. L'istante di GitHub e' UTC e va letto come UTC (19/09).

    Prima usava time.mktime, che interpreta l'ora come LOCALE, e poi provava a correggere con
    time.timezone — che vale l'offset STANDARD, non quello in vigore con l'ora legale. Sul runner di
    GitHub (che vive in UTC) il conto tornava per caso; da qualunque altra macchina no: misurato
    oggi, una corsia girata da 30 minuti risultava vecchia di 3 ore e mezza.
    calendar.timegm legge l'istante come UTC e basta, senza correzioni da indovinare."""
    try:
        return (now - calendar.timegm(time.strptime(iso, "%Y-%m-%dT%H:%M:%SZ"))) / 3600
    except Exception:
        return 999



def intervallo_dichiarato(w):
    """Ogni quante ore questa corsia DICE di voler girare, leggendo il suo cron.

    Torna None se non ha un cron o se non lo so leggere: in quel caso chi chiama torna al metodo
    vecchio invece di inventarsi un numero."""
    try:
        import base64, re
        d = json.load(urllib.request.urlopen(urllib.request.Request(
            f"https://api.github.com/repos/{REPO}/contents/{w['path']}",
            headers={"Authorization": f"token {TOK}", "Accept": "application/vnd.github+json",
                     "User-Agent": "whale-watchdog"}), timeout=25))
        testo = base64.b64decode(d["content"]).decode(errors="replace")
    except Exception:
        return None
    ore = []
    for riga in testo.split("\n"):
        r = riga.strip()
        if not r.startswith("- cron:"):
            continue
        # IL COMMENTO IN CODA VA TOLTO PRIMA (19/09): le righe del repo sono scritte
        # `- cron: "17 */2 * * *"   # ogni 2 ore`, e senza togliere il commento i campi diventano
        # sette invece di cinque e la riga veniva scartata in silenzio — cioe' le corsie con un cron
        # commentato risultavano «senza cron» e tornavano alla soglia adattiva, quella rotta.
        espr = r.split("cron:")[1].split("#")[0].strip().strip('"').strip("'")
        campi = espr.split()
        if len(campi) != 5:
            continue
        minuto, ora, _, _, giorno = campi
        if giorno not in ("*", "?"):
            ore.append(168.0)                      # settimanale
        elif ora.startswith("*/"):
            try: ore.append(float(ora[2:]))
            except Exception: pass
        elif ora == "*":
            if minuto.startswith("*/"):
                try: ore.append(float(minuto[2:]) / 60.0)
                except Exception: pass
            else:
                ore.append(1.0)                    # una volta l'ora
        else:
            ore.append(24.0)                       # a un'ora fissa del giorno
    return min(ore) if ore else None


def main():
    wfs = api("/workflows?per_page=100")
    if not wfs:
        print("WATCHDOG | API workflows non raggiungibile"); return
    active = [w for w in wfs["workflows"] if w.get("state") == "active"]
    problems = []; fixed = []; rows = []
    for w in active:
        runs = api(f"/workflows/{w['id']}/runs?per_page=8")
        if not runs or not runs.get("workflow_runs"):
            continue
        rr = runs["workflow_runs"]
        last = rr[0]
        # e' schedulato (ha un cron)? lo deduciamo: se ha girato piu' volte con event=schedule
        scheduled = any(r.get("event") == "schedule" for r in rr)
        concl = [r["conclusion"] for r in rr[:6] if r["conclusion"]]
        fails = concl.count("failure")
        cancels = concl.count("cancelled")
        last_age = age_h(last["created_at"])
        # LO ZOMBIE CHE TIENE LA CORSIA (aggiunto 04/09, dopo esserci cascati due volte).
        # Un turno risultava "in esecuzione" da 8 ore e 54 minuti — oltre il suo stesso limite di 350
        # minuti — e teneva occupato il gruppo di concorrenza: ogni nuovo turno restava in coda per ore
        # senza mai partire. Da fuori sembra un workflow lento, e invece e' MORTO: il lavoro non
        # riparte non perche' manchi la potenza, ma perche' un cadavere occupa il posto.
        # E' successo prima al motore (#71, 5h48) e poi alla ricerca (#37, 8h54): due volte non e' un
        # caso, e' un difetto strutturale. Qui si chiude chi ha passato il suo tempo massimo.
        for r in rr:
            if r["status"] in ("in_progress", "queued", "pending") and age_h(r["created_at"]) > 6.2:
                if api(f"/runs/{r['id']}/cancel", "POST", {}) is not None:
                    fixed.append(f"{w['name']} #{r['run_number']}: chiuso, era appeso da "
                                 f"{age_h(r['created_at']):.1f}h e bloccava la corsia")
        # LA SOGLIA VIENE DAL CRON DICHIARATO, NON DAL COMPORTAMENTO OSSERVATO (19/09).
        # Prima era adattiva: mediana degli intervalli fra le ultime 8 corse, per 3. Sembra prudente
        # ed e' invece il difetto: se GitHub salta i cron di una corsia (e lo fa, quando il repo e'
        # occupato — e il nostro lo e' sempre), gli intervalli OSSERVATI diventano enormi, quindi la
        # soglia diventa enorme, e il guardiano IMPARA IL GUASTO COME NORMALITA'.
        # Misurato oggi: sette corsie su dodici erano ferme da 2-5 ore e il guardiano — che gira ogni
        # due ore e le aveva viste — non ne ha rilanciata nessuna. storico girava ogni 5 ore perche'
        # era rotta, quindi la soglia calcolata era 15 ore.
        # E' la stessa malattia che sto correggendo da due giorni nei numeri: misurare una
        # popolazione che il difetto stesso ha plasmato. Qui la cura e' identica: si confronta con
        # quello che la corsia DICHIARA di voler fare, non con quello che le e' riuscito di fare.
        atteso = intervallo_dichiarato(w)
        if atteso:
            stale = max(STALE_HOURS, atteso * 2.5)
        else:
            ages = sorted(age_h(r["created_at"]) for r in rr)
            gaps = [ages[i + 1] - ages[i] for i in range(len(ages) - 1) if ages[i + 1] - ages[i] > 0.01]
            interval = sorted(gaps)[len(gaps) // 2] if gaps else 999
            stale = max(STALE_HOURS, interval * 3)
        status = "✅"
        # 1) fallimenti veri
        if fails >= 2:
            status = "🔴"; problems.append(f"**{w['name']}**: {fails} run FALLITE nelle ultime 6 (bug reale, da guardare)")
        # 2) fermo (schedulato ma non gira da troppo, rispetto al SUO ritmo)
        elif scheduled and last_age > stale:
            status = "🟠"
            if api(f"/workflows/{w['id']}/dispatches", "POST", {"ref": "main"}):
                fixed.append(f"**{w['name']}**: fermo da {last_age:.1f}h → RI-LANCIATO ✅")
                status = "🔧"
            else:
                problems.append(f"**{w['name']}**: fermo da {last_age:.1f}h, ri-lancio FALLITO (dispatch non disponibile?)")
        # 3) troppe cancellazioni
        elif cancels >= 3:
            status = "🟡"; problems.append(f"**{w['name']}**: {cancels} cancellazioni (sovrapposizioni? controllare frequenza cron)")
        rows.append((status, w['name'], last['conclusion'] or last['status'], last_age))

    # report
    lines = ["# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti",
             f"*controllo ogni 2h · {len(active)} workflow attivi*", ""]
    if problems:
        lines.append(f"## 🔴 {len(problems)} PROBLEMI"); lines += [f"- {p}" for p in problems]; lines.append("")
    if fixed:
        lines.append(f"## 🔧 {len(fixed)} AUTO-FIXATI"); lines += [f"- {f}" for f in fixed]; lines.append("")
    if not problems and not fixed:
        lines.append("## ✅ Tutti i reparti sani (nessun fallimento, nessuno fermo)"); lines.append("")
    lines.append("## Stato per workflow")
    lines.append("| | workflow | ultima run | età |")
    lines.append("|---|---|---|---|")
    for st, name, lc, ag in sorted(rows, key=lambda x: x[0] != "🔴"):
        lines.append(f"| {st} | {name} | {lc} | {ag:.1f}h fa |")
    lines.append("")
    lines.append("> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.")
    open("WATCHDOG.md", "w").write("\n".join(lines))
    print(f"WATCHDOG | {len(active)} workflow · {len(problems)} problemi · {len(fixed)} auto-fixati", flush=True)


if __name__ == "__main__":
    main()
