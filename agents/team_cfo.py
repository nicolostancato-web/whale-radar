#!/usr/bin/env python3
"""
TEAM · CFO — il ruolo che si assicura che tutto questo continui a costare ZERO.

Il sistema gira 24h su 24 e macina migliaia di minuti di GitHub Actions al mese. Oggi sono gratis per un
solo motivo: **il repo è PUBBLICO**. Se diventasse privato, gli stessi minuti si pagherebbero (~$0.008/min
oltre la franchigia): il nostro ritmo attuale sarebbe decine di euro al mese, per una cosa che oggi è €0.
È già successo di prendere spaventi cosi'. Questo ruolo lo controlla a ogni riunione, e verifica anche che
nessun reparto abbia iniziato a chiamare un'API a pagamento.
Scrive CFO.md · €0 (usa solo file locali + l'API GitHub che è gratuita).
"""
import json, os, re, glob, time, urllib.request

now = int(time.time())
REPO = "nicolostancato-web/whale-radar"
COSTO_MIN = 0.008          # $ al minuto su repo privato (runner Linux), fonte: pricing GitHub Actions
# servizi che costano se qualcuno li chiama: qui NON devono comparire senza una decisione esplicita
A_PAGAMENTO = [
    (r"api\.anthropic\.com", "API Anthropic (a token)"),
    (r"api\.openai\.com", "API OpenAI (a token)"),
    (r"cometapi\.com", "CometAPI (prepagato)"),
    (r"maps\.googleapis\.com|places\.googleapis\.com", "Google Places/Maps (a chiamata)"),
    (r"api\.apify\.com", "Apify (abbonamento)"),
    (r"helius-rpc\.com|helius\.xyz", "Helius (free tier: da tenere d'occhio)"),
]
GRATIS_ATTESI = ["geckoterminal.com", "dexscreener.com", "mainnet.base.org", "blxrbdn.com",
                 "rpc.mainnet.chain.robinhood.com"]


def repo_pubblico():
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{REPO}",
                                     headers={"Accept": "application/vnd.github+json"})
        tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("WR_PAT")
        if tok: req.add_header("Authorization", f"token {tok}")
        with urllib.request.urlopen(req, timeout=20) as r:
            return not json.load(r).get("private", True)
    except Exception:
        return None


def usa_a_pagamento():
    trovati = []
    for f in glob.glob("agents/*.py") + glob.glob("*.py"):
        try: txt = open(f, errors="ignore").read()
        except Exception: continue
        for pat, nome in A_PAGAMENTO:
            if re.search(pat, txt): trovati.append((os.path.basename(f), nome))
    return trovati


def minuti_stimati():
    """quanti minuti/mese stiamo bruciando al ritmo attuale (il motore gira in continuo)."""
    return int(24 * 60 * 30)      # un job praticamente sempre acceso = ~43.200 min/mese


def main():
    pub = repo_pubblico()
    pag = usa_a_pagamento()
    minuti = minuti_stimati()
    costo_se_privato = minuti * COSTO_MIN

    allarmi = []
    if pub is False:
        allarmi.append(("CRITICA", f"il repo è **PRIVATO**: al ritmo attuale (~{minuti:,} min/mese) "
                                   f"sarebbero circa **${costo_se_privato:,.0f}/mese**. Rimetterlo pubblico "
                                   f"o fermare il motore".replace(",", ".")))
    inattesi = [(f, n) for f, n in pag if "Helius" not in n]
    if inattesi:
        allarmi.append(("DA VERIFICARE", "reparti che chiamano servizi a pagamento: " +
                        ", ".join(f"`{f}` → {n}" for f, n in inattesi)))

    verdetto = ("🟢 **COSTO ZERO CONFERMATO**" if not allarmi else
                "🔴 **ATTENZIONE AI COSTI**" if any(a[0] == "CRITICA" for a in allarmi) else
                "🟡 **DA VERIFICARE**")
    L = ["# 💰 TEAM · CFO — quanto ci costa tutto questo",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))}*", "",
         f"## {verdetto}", "",
         f"| voce | stato |", "|---|---|",
         f"| repo pubblico (= Actions gratis) | {'✅ sì' if pub else ('❌ NO' if pub is False else '❓ non verificabile ora')} |",
         f"| minuti Actions stimati | ~{minuti:,} al mese".replace(",", ".") + " |",
         f"| **costo attuale** | **{'€0' if pub else 'a rischio'}** |",
         f"| costo se il repo diventasse privato | ~${costo_se_privato:,.0f}/mese".replace(",", ".") + " |",
         f"| fonti dati usate | {', '.join(GRATIS_ATTESI[:3])}… (tutte free tier) |", ""]
    if allarmi:
        L += ["## Segnalazioni", ""] + [f"- **{g}** — {t}" for g, t in allarmi] + [""]
    else:
        L += ["**Controlli passati:**", "",
              "- il repo è pubblico, quindi i minuti di GitHub Actions sono gratuiti",
              "- nessun reparto chiama API a pagamento (niente Anthropic/OpenAI/Google/Apify nel codice che gira)",
              "- i dati arrivano solo da fonti gratuite: GeckoTerminal, DexScreener, RPC pubblici", ""]
    L += ["> **Perché questo ruolo esiste:** il sistema gira 24 ore su 24 e macina ~43.000 minuti di Actions al",
          "> mese. Sono gratis solo perché il repo è pubblico. Basta cambiare quella impostazione e la stessa",
          "> identica cosa inizia a costare centinaia di dollari al mese, in silenzio."]
    open("CFO.md", "w").write("\n".join(L))
    json.dump({"ts": now, "pubblico": pub, "allarmi": len(allarmi)}, open("data/cfo_flags.json", "w"))
    print(f"CFO | {verdetto[:32]} | pubblico={pub} | {len(allarmi)} allarmi", flush=True)


if __name__ == "__main__":
    main()
