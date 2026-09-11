#!/usr/bin/env python3
"""
DUE_GAMBE — un rendimento netto vale solo se ENTRAMBE le gambe sono state misurate sulla SUA chain.

DA DOVE VIENE (10/09, consulenza esterna). Astra ha trovato l'assunzione invisibile: il metro dei
costi e' stato misurato SOLO su Jupiter, cioe' solo su Solana, e per giunta "in calma" e non durante
una fuga. Con quel metro classifichiamo Base e Robinhood. Sono chain diverse, DEX diversi, liquidita'
diversa: usare il costo di un mercato per giudicare un altro non e' un'approssimazione, e' una
misura che non esiste.

LA VERIFICA E' UNA SOLA DOMANDA, per ogni trade selezionato: esiste una misura di costo fatta sulla
SUA chain, alla SUA taglia, in un momento compatibile? Se manca anche una sola gamba, quel rendimento
non e' +1% ne' +24%: e' NON IDENTIFICATO. E un numero non identificato non puo' scegliere una pista.

CRITERIO DI MORTE (di Astra, scritto prima di guardare): se il 100% dei trade Base e Robinhood non ha
entrambe le gambe misurate sulla propria chain, le loro due classifiche nette sono morte come
evidenza. Non si "aggiusta con un fattore": si misura o non si usa.

Sola lettura, nessuna chiamata. €0.
"""
import json, os, glob, time

ARCH = "data/costi_archivio.json"
CHAINS = ("base", "robinhood", "solana")


def misure():
    """Le misure di costo che abbiamo, divise per famiglia di indirizzo."""
    try:
        d = json.load(open(ARCH))
    except Exception:
        return {}, 0
    fam = {"evm": set(), "solana": set()}
    for k in d:
        (fam["evm"] if str(k).startswith("0x") else fam["solana"]).add(str(k).lower())
    # LE MISURE FATTE SULLA CATENA CONTANO COME LE ALTRE (10/09). Sono quote vere lette dai pool di
    # Base e Robinhood: se il controllo non le vedesse, resterebbe rosso anche dopo aver risolto il
    # problema — e un allarme che non si spegne quando il guasto e' riparato smette di significare.
    try:
        ev = json.load(open("data/costi_evm.json"))
        tot_evm = 0
        for ch, pool in ev.items():
            # DI NUOVO POOL CONTRO TOKEN: le misure on-chain sono per POOL, la copertura si conta per
            # TOKEN. E' la seconda volta oggi che questo incrocio da' zero — e uno zero da incrocio
            # sbagliato e indistinguibile da uno zero vero. Si passa dalla mappa, sempre.
            mp = f"data/multichain/{ch}/token_map.json"
            mappa = {}
            if os.path.exists(mp):
                try: mappa = {k.lower(): str(v).lower() for k, v in json.load(open(mp)).items()}
                except Exception: mappa = {}
            for a in pool:
                tok = mappa.get(str(a).lower())
                if tok:
                    fam["evm"].add(tok); tot_evm += 1
    except Exception:
        tot_evm = 0
    return fam, len(d) + tot_evm


def token_di(chain):
    """I token su cui la chain esprime un rendimento.

    ATTENZIONE AL NOME DELLE COSE: le candele sono archiviate per POOL, i costi per TOKEN. Confrontare
    le due liste cosi' come sono da zero in comune SEMPRE — e uno zero del genere non e' un risultato,
    e' un incrocio sbagliato. E' lo stesso errore che ci ha fatto credere per un giorno che un
    esperimento non avesse eventi. Qui si passa dalla mappa pool->token prima di confrontare."""
    mappa = {}
    p = f"data/multichain/{chain}/token_map.json"
    if os.path.exists(p):
        try:
            mappa = {k.lower(): str(v).lower() for k, v in json.load(open(p)).items()}
        except Exception:
            mappa = {}
    out = set()
    for f in glob.glob(f"data/multichain/{chain}/candles/*.jsonl.gz"):
        pool = os.path.basename(f).split(".")[0].lower()
        tok = mappa.get(pool)
        if tok: out.add(tok)
    return out, len(mappa)


def main():
    fam, tot = misure()
    L = ["# 🦵🦵 LE DUE GAMBE — un netto vale solo se misurato sulla SUA chain",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · nato dalla revisione esterna del "
         f"10/09 · sola lettura · €0*", "",
         "> **L'assunzione invisibile**: il metro dei costi è stato misurato solo su Jupiter — cioè",
         "> solo su Solana — e per giunta *in calma*, non durante una fuga. Con quel metro stiamo",
         "> classificando Base e Robinhood. Chain diverse, DEX diversi, liquidità diversa: usare il",
         "> costo di un mercato per giudicare un altro non è un'approssimazione, è **una misura che",
         "> non esiste**.", "",
         f"**Misure di costo in archivio: {tot}** — di cui su indirizzi EVM (Base/Robinhood): "
         f"**{len(fam.get('evm', []))}**, su Solana: **{len(fam.get('solana', []))}**.", ""]

    L += ["| chain | token valutabili | con costo misurato sulla SUA chain | copertura |",
          "|---|---|---|---|"]
    copertura = {}
    for ch in CHAINS:
        tok, n_mappa = token_di(ch)
        if not n_mappa:
            L.append(f"| **{ch}** | — | — | *manca la mappa pool→token: non misurabile* |")
            copertura[ch] = 0.0
            continue
        propria = fam.get("evm" if ch in ("base", "robinhood") else "solana", set())
        coperti = len(tok & propria)
        pct = (coperti / len(tok) * 100) if tok else 0.0
        copertura[ch] = pct
        L.append(f"| **{ch}** | {len(tok):,} | {coperti:,} | "
                 f"{'**' if pct < 100 else ''}{pct:.1f}%{'**' if pct < 100 else ''} |")
    L += [""]

    rotte = [ch for ch in ("base", "robinhood") if copertura.get(ch, 0) < 100]
    L += ["## Verdetto", ""]
    if rotte:
        L += [f"> ❌ **Criterio di morte scattato** (scritto da chi sta fuori, prima di guardare): "
              f"su **{', '.join(rotte)}** la copertura non è del 100%.", "",
              "> Quindi **+1% su Base e +24% su Robinhood non sono rendimenti**: sono numeri lordi",
              "> a cui è stato sottratto il costo di un altro mercato. Il loro valore corretto è",
              "> **non identificato** — e un numero non identificato **non può scegliere una pista**.", "",
              "> Non si aggiusta con un fattore di conversione: o si misurano i costi su quelle chain,",
              "> o quelle due classifiche non si usano per decidere niente.", "",
              "## Cosa serve per riaccenderle", "",
              "1. Un misuratore di costo che giri **sui DEX di Base e Robinhood** (non su Jupiter),",
              "   alla taglia che useremmo davvero, sui token che il modello seleziona.",
              "2. Le misure **al momento dello stop**, non solo in calma: è il consiglio del 4",
              "   settembre, mai eseguito, e la revisione di oggi lo richiama come blocco principale.",
              "3. Finché non ci sono: **Solana è l'unica chain con un metro suo**, ed è l'unica su cui",
              "   un verdetto significa qualcosa."]
    else:
        L += ["> ✅ Tutte le chain hanno entrambe le gambe misurate a casa loro: i netti sono confrontabili."]

    open("DUE_GAMBE.md", "w").write("\n".join(L))
    print(f"DUE_GAMBE | copertura " + " ".join(f"{c}:{copertura[c]:.0f}%" for c in CHAINS), flush=True)


if __name__ == "__main__":
    main()
