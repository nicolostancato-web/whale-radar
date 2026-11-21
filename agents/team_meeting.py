#!/usr/bin/env python3
"""
TEAM · IL VERBALE — la stanza in cui entra l'investitore.

Ogni ciclo del motore e' una riunione di squadra. Cinque ruoli, cinque responsabilita':
  🏃 OPERATIONS — che tutto giri e niente si blocchi          (loop_engine + goal_base)
  🔬 RICERCA    — alzare la percentuale, inventando segnali    (explorer + team_ricerca)
  ✅ VERITA'     — che la percentuale non sia una favola        (auditor)
  🔒 SECURITY   — che il repo pubblico non perda credenziali   (team_security)
  💰 CFO        — che tutto continui a costare zero            (team_cfo)
Questo file mette insieme i loro verdetti in una pagina sola: TEAM.md. €0.
"""
import json, os, re, time

now = int(time.time())


def leggi(path, default=""):
    try: return open(path).read()
    except Exception: return default


def verdetto_da(md, default="— non ha ancora parlato"):
    """prende la riga '## Verdetto: ...' o il primo titolo di stato dal report di un ruolo."""
    m = re.search(r"^## (?:Verdetto|Stato|Architetto): (.+)$", md, re.M)
    if m: return m.group(1).strip()
    m = re.search(r"^## (🟢|🟡|🔴|✅|⚠️).*$", md, re.M)
    return m.group(0).replace("## ", "").strip() if m else default


def json_safe(p):
    try: return json.load(open(p))
    except Exception: return {}


def main():
    loops = leggi("LOOPS.md"); audit = leggi("AUDIT.md")
    sec = leggi("SECURITY.md"); cfo = leggi("CFO.md"); perc = leggi("PERCENTUALE.md")

    # RICERCA: quante strategie e quanti segnali nuovi sono stati provati, su tutte le chain
    strategie = segnali = promossi = 0
    for ch in ("base", "solana", "robinhood", "bsc"):
        strategie += json_safe(f"data/explorer_{ch}.json").get("tentativi", 0)
        r = json_safe(f"data/ricerca_{ch}.json")
        segnali += len(r.get("provate", [])); promossi += len(r.get("promosse", []))

    # la riga della percentuale per chain, dal report del ruolo VERITA'/percentuale
    righe_perc = re.findall(r"^\| \*\*(\w+)\*\* \| ([+-][\d.]+%) \| \*\*([+-][\d.]+%)\*\* \| ([\d.]+% \([\d]+ trade\)) \| ([\d.]+%) \|",
                            perc, re.M)

    L = ["# 👥 IL TEAM — verbale della riunione",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · una riunione a ogni ciclo, ~ogni 30 minuti*", "",
         "| ruolo | responsabilità | come è andata |", "|---|---|---|",
         f"| 🏃 **Operations** | che tutto giri e niente si blocchi | {verdetto_da(loops)} |",
         f"| 🔬 **Ricerca** | alzare la percentuale | {strategie:,} strategie provate · {segnali} segnali nuovi messi alla prova · **{promossi} promossi** |".replace(",", "."),
         f"| ✅ **Verità** | che la percentuale non sia una favola | {verdetto_da(audit)} |",
         f"| 🔒 **Security** | niente credenziali nel repo pubblico | {verdetto_da(sec)} |",
         f"| 💰 **CFO** | che tutto costi zero | {verdetto_da(cfo)} |", ""]
    if righe_perc:
        L += ["## Dove siamo con la percentuale", "",
              "| chain | media | **robusta** | vinti | peso dei 3 colpi migliori |", "|---|---|---|---|---|"]
        for ch, med, rob, vin, top3 in righe_perc:
            L.append(f"| {ch} | {med} | **{rob}** | {vin} | {top3} |")
        L += ["", "> La **robusta** è il numero su cui si decide: è quello che resta togliendo i 3 colpi",
              "> migliori. Il live si apre a +40%.", ""]
    # QUANTE VOLTE CI ABBIAMO SBATTUTO LA TESTA FINO IN FONDO
    # (definizione di Nicolò, 31/08): un "test" non è una configurazione provata — è il GIRO COMPLETO:
    # si scopre → si valida in cassaforte → esce un verdetto → la lezione viene archiviata → si riparte.
    # I tentativi grezzi si contano a migliaia e da soli non insegnano niente: quello che fa avanzare è il
    # numero di giri CHIUSI. Questa è la velocità di apprendimento vera del team.
    prop_all = json_safe("data/proposte.json").get("proposte", [])
    giudicate = [p for p in prop_all if p.get("validazione")]
    bocciate = [p for p in giudicate if p["validazione"].get("robusta", -999) <= 0]
    archiviate = 0
    if os.path.exists("data/proposte_storico.jsonl"):
        try: archiviate = sum(1 for l in open("data/proposte_storico.jsonl") if l.strip())
        except Exception: pass
    con_all = json_safe("data/conoscenza.json").get("voci", {})
    lezioni = sum(1 for v in con_all.values() if v.get("prove", 0) > 0)
    grezzi = strategie + segnali

    # proposte aperte + memoria del team
    prop = json_safe("data/proposte.json").get("proposte", [])
    aperte = [p for p in prop if p.get("stato") == "APERTA"]
    con = json_safe("data/conoscenza.json").get("voci", {})
    archiviate = sum(1 for v in con.values() if v.get("bocciature", 0) >= 3)
    funzionano = sum(1 for v in con.values() if v.get("promozioni", 0) > 0)
    L += ["## Quante volte ci abbiamo sbattuto la testa", "",
          "| | quante |", "|---|---|",
          f"| tentativi grezzi (configurazioni e segnali provati) | **{grezzi:,}** |".replace(",", "."),
          f"| lezioni archiviate (ogni prova lascia una traccia) | **{lezioni}** |",
          f"| scoperte arrivate al **giudizio in cassaforte** | **{len(giudicate)}** |",
          f"| di cui **bocciate perché erano rumore** | **{len(bocciate)}** |",
          f"| giri chiusi e archiviati per sempre | **{archiviate}** |", "",
          "> I tentativi grezzi si contano a migliaia e da soli non insegnano nulla. Quello che fa avanzare",
          "> è il **giro completo**: si scopre, si valida su dati mai visti, esce un verdetto, la lezione",
          "> resta scritta, si riparte più informati. Questa riga è la velocità di apprendimento vera.", "",
          "## Sul tavolo dell'investitore", ""]
    if aperte:
        L += [f"**{len(aperte)} proposte aperte** (vedi `PROPOSTE.md`):", ""]
        for p in aperte[:3]:
            L.append(f"- **{p['chain']}** · {p['tipo']} · **{p['guadagno']:+.0f} punti** "
                     f"({p.get('da','?')}% → {p['a']:+.0f}%)")
    else:
        L += ["Nessuna proposta aperta: il team cerca ma non ha ancora trovato niente che valga la pena."]
    L += ["", f"**Memoria del team:** {len(con)} idee provate · {funzionano} funzionano · "
          f"{archiviate} archiviate (non si riprovano finché i dati non raddoppiano)", "",
          "> **Come funziona questa stanza:** il team si riunisce da solo ogni 30 minuti, misura, ripara ciò",
          "> che può riparare e cerca di alzare la percentuale. Le RIPARAZIONI le fa da sé; le DECISIONI",
          "> (aprire il live, cambiare strategia) restano dell'investitore e passano da DECISIONS.md.",
          "> I verbali dettagliati: `LOOPS.md`, `PERCENTUALE.md`, `EXPLORER_*.md`, `RICERCA_*.md`, `AUDIT.md`,",
          "> `SECURITY.md`, `CFO.md`."]
    open("TEAM.md", "w").write("\n".join(L))
    print(f"TEAM | riunione fatta | {strategie} strategie · {segnali} segnali · {promossi} promossi", flush=True)


if __name__ == "__main__":
    main()
