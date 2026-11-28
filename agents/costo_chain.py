#!/usr/bin/env python3
"""
COSTO_CHAIN — il costo delle due gambe calcolato dalla LIQUIDITA' DI QUELLA CHAIN.

IL BLOCCO CHE RISOLVE (indicato dalla revisione esterna il 04/09 e di nuovo il 10/09). Il metro dei
costi e' stato misurato solo su Jupiter, cioe' solo su Solana: 815 misure, ZERO su Base e Robinhood.
Con quel metro calcolavamo i netti delle altre due chain. E' come stimare quanto ti resta vendendo
casa a Milano usando le spese di agenzia di un altro paese: il prezzo e' vero, quello che ti resta no.

L'IDEA. Non possiamo chiedere un preventivo di vendita su ogni chain (non esiste un Jupiter per
Robinhood). Ma la riserva del pool CE L'ABBIAMO, ed e' la liquidita' vera di quel mercato in quel
momento. Da li' il costo si calcola: su un pool a prodotto costante, comprare S dentro una riserva R
sposta il prezzo di circa S/(R+S), e la stessa cosa succede uscendo.

PERCHE' NON E' UN'ASSUNZIONE MASCHERATA. Su Solana abbiamo TUTTE E DUE le cose: la liquidita' E il
costo misurato davvero da Jupiter. Quindi la formula si puo' VERIFICARE dove la verita' e' nota,
prima di usarla dove non lo e'. Se sbaglia su Solana, non ha diritto di parlare di Base e Robinhood:
si scrive che non sappiamo, e non si usa. Una formula che non e' stata controllata dove poteva
esserlo e' un'opinione con dei numeri intorno.

Sola lettura, nessuna chiamata. €0.
"""
import json, os, glob, gzip, time, statistics as st

ARCH = "data/costi_archivio.json"
TAGLIA = float(os.environ.get("TAGLIA_USD", 25))
CHAINS = ("base", "robinhood", "solana")


def stimato(liq, size=TAGLIA):
    """Costo di andata+ritorno da riserva. liq e' il valore TOTALE del pool: il lato in cui entriamo
    e' circa la meta'."""
    r = max(1.0, liq / 2.0)
    una_gamba = size / (r + size)
    return 2 * una_gamba


def controllo_su_solana():
    """Dove la verita' e' nota: la formula ci azzecca?"""
    try:
        d = json.load(open(ARCH))
    except Exception:
        return None
    coppie = []
    for v in d.values():
        L = v.get("liquidita") or 0
        s = (v.get("size") or {}).get(str(int(TAGLIA))) or {}
        c = s.get("costo_roundtrip_pct")
        if L > 0 and isinstance(c, (int, float)):
            coppie.append((stimato(L), c / 100.0))
    if len(coppie) < 30:
        return {"n": len(coppie)}
    rel_grezza = st.median([abs(a - b) / max(1e-6, b) for a, b in coppie])
    # LA FORMULA NUDA SBAGLIA DEL 49% E SOTTOSTIMA SEMPRE (2,00% contro 3,86%): mancano le commissioni,
    # il lato token della riserva, il percorso dell'ordine. Un fattore unico puo' recuperarlo — ma NON
    # si trova e si verifica sugli stessi token, o si racconta due volte la stessa storia. Meta' per
    # trovare il fattore, l'altra meta' MAI VISTA per giudicarlo. La soglia resta quella di prima: 35%.
    meta = len(coppie) // 2
    tara, prova = coppie[:meta], coppie[meta:]
    rap = [b / a for a, b in tara if a > 0]
    fatt = st.median(rap) if rap else 1.0
    rel = [abs(a * fatt - b) / max(1e-6, b) for a, b in prova]
    return {"n": len(coppie),
            "stimato_mediano": st.median([a for a, _ in coppie]),
            "misurato_mediano": st.median([b for _, b in coppie]),
            "errore_relativo_grezzo": rel_grezza,
            "fattore": fatt, "n_prova": len(prova),
            "errore_relativo_mediano": st.median(rel)}


def liquidita_di(chain):
    """L'ultima liquidita' vista per ogni pool di quella chain."""
    out = []
    for f in glob.glob(f"data/multichain/{chain}/pulse/*.jsonl.gz"):
        ultima = None
        try:
            for l in gzip.open(f, "rt"):
                if l.strip():
                    try:
                        ultima = json.loads(l).get("liq")
                    except Exception: pass
        except Exception: continue
        if ultima: out.append(float(ultima))
    return out


def main():
    ctrl = controllo_su_solana()
    L = ["# 💸 IL COSTO, CHAIN PER CHAIN — calcolato dalla liquidità di casa propria",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · taglia ${TAGLIA:.0f} · sola "
         f"lettura · €0*", "",
         "> **Il blocco**: 815 misure di costo, tutte su Solana via Jupiter, **zero su Base e",
         "> Robinhood** — eppure i loro netti li calcolavamo con quelle. È stimare quanto ti resta",
         "> vendendo casa a Milano con le spese di agenzia di un altro paese.", "",
         "> **La via d'uscita**: la riserva del pool ce l'abbiamo, ed è la liquidità vera di quel",
         "> mercato in quel momento. Su un pool a prodotto costante, entrare con S in una riserva R",
         "> sposta il prezzo di circa `S/(R+S)` — e uscendo si paga di nuovo.", "",
         "## Prima: la formula regge dove la verità è nota?", ""]

    ok = False
    if not ctrl:
        L += ["> ❓ Non riesco a leggere l'archivio dei costi: senza controllo non si applica niente."]
    elif ctrl.get("n", 0) < 30:
        L += [f"> ⏸️ Solo {ctrl['n']} token hanno **sia** la liquidità **sia** il costo misurato: "
              "troppo pochi per controllare la formula. Non si applica finché non se ne accumulano 30."]
    else:
        e = ctrl["errore_relativo_mediano"]
        ok = e <= 0.35
        L += [f"Su **{ctrl['n']} token Solana** dove abbiamo entrambe le cose. Metà per trovare il",
              "fattore di correzione, l'altra metà — **mai vista** — per giudicarlo:", "",
              "| | valore |", "|---|---|",
              f"| costo **misurato** (Jupiter), mediano | **{ctrl['misurato_mediano']*100:.2f}%** |",
              f"| costo dalla formula nuda, mediano | **{ctrl['stimato_mediano']*100:.2f}%** |",
              f"| errore della formula nuda | {ctrl['errore_relativo_grezzo']*100:.0f}% |",
              f"| fattore trovato sulla prima metà | ×**{ctrl['fattore']:.2f}** |",
              f"| **errore sulla metà mai vista** ({ctrl['n_prova']} token) | **{e*100:.0f}%** |", "",
              (f"> ✅ **La formula ha diritto di parlare**: sbaglia del {e*100:.0f}% in mediana, sotto "
               "la soglia del 35% fissata prima. Non sostituisce una misura vera, ma è **la liquidità "
               "di quella chain** e non il prezzo di un altro mercato."
               if ok else
               f"> ❌ **La formula NON ha diritto di parlare**: sbaglia del {e*100:.0f}% in mediana, "
               "sopra la soglia del 35% fissata prima. Su Base e Robinhood scriviamo *non sappiamo*, "
               "e non si decide. Meglio un buco dichiarato di un numero inventato."), ""]

    L += ["## Poi: quanto costerebbe, chain per chain", ""]
    if ok:
        L += ["| chain | pool con liquidità nota | costo stimato mediano | il 25% peggiore |",
              "|---|---|---|---|"]
        for ch in CHAINS:
            liq = liquidita_di(ch)
            if len(liq) < 5:
                L.append(f"| **{ch}** | {len(liq)} | *troppo pochi per dirlo* | — |")
                continue
            cs = sorted(stimato(x) * ctrl["fattore"] for x in liq)
            L.append(f"| **{ch}** | {len(liq)} | **{st.median(cs)*100:.2f}%** | "
                     f"{cs[int(len(cs)*0.75)]*100:.2f}% |")
        L += ["", "> Questi numeri **non sostituiscono** le misure vere: servono a smettere di usare il",
              "> costo di Solana per giudicare Base e Robinhood. Il passo successivo resta quello che la",
              "> revisione chiede dal 4 settembre: misurare **al momento dello stop**, non in calma."]
    else:
        L += ["> Non si applica finché il controllo su Solana non passa. **Un numero non controllato",
              "> dove poteva esserlo non è una stima: è un'opinione con dei numeri intorno.**"]

    open("COSTO_CHAIN.md", "w").write("\n".join(L))
    print(f"COSTO_CHAIN | controllo su solana: {'passa' if ok else 'NON passa'}", flush=True)


if __name__ == "__main__":
    main()
