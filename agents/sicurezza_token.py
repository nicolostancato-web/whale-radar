#!/usr/bin/env python3
"""
SICUREZZA_TOKEN — il token si puo' VENDERE? chi lo controlla? quanti lo possiedono davvero?

Punto 5 (e parte del 6) della consulenza esterna del 01/09. Finora nel modello un token da cui non si esce
risultava semplicemente come un trade che perde il 70%. Nella realta' e' un trade che perde TUTTO: honeypot,
tassa di vendita al 99%, vendite disabilitate, owner che puo' cambiare le regole dopo che sei entrato.
La misura dei costi reali l'ha gia' mostrato: su 5 token, 4 avevano almeno una size non vendibile.

REGOLA CONTRO IL LEAKAGE (dalla consulenza): questi campi si raccolgono ADESSO per i token di ADESSO.
Interrogare oggi il contratto di un token del passato NON e' lecito: owner, tasse e permessi possono essere
cambiati dopo, e useremmo informazione che al momento della decisione non esisteva. Percio' l'archivio si
costruisce in avanti, giorno dopo giorno, e diventera' utilizzabile quando questi token avranno un esito.

Fonte: GoPlus (gratis, nessuna chiave). Scrive SICUREZZA.md + data/sicurezza/<chain>.jsonl (append). €0.
"""
import json, os, glob, time, datetime, urllib.request

CHAIN_ID = {"base": "8453", "bsc": "56"}          # id EVM per GoPlus
PAUSA = 2.2                                        # free tier: ~30 richieste al minuto
MAX = int(os.environ.get("MAX_TOKEN", 60))
BUDGET = int(os.environ.get("BUDGET_SEC", 400))
now = int(time.time()); t0 = time.time()


def chiedi(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}),
                                    timeout=25) as r:
            d = json.loads(r.read())
        return (d.get("result") or {})
    except Exception:
        return {}


def eta_ore(p):
    c = p.get("created")
    if c:
        try:
            return (now - datetime.datetime.strptime(c, "%Y-%m-%dT%H:%M:%SZ")
                    .replace(tzinfo=datetime.timezone.utc).timestamp()) / 3600
        except Exception: pass
    return 999


def con_candele(chain):
    """I token di cui abbiamo GIA' le candele — cioe' gli unici su cui si possa poi misurare qualcosa.

    Aggiunto il 02/09 dopo una scoperta imbarazzante: censivamo token a caso dalla rubrica, e le candele
    le raccoglievamo su altri token. Risultato, su Base solo 211 token su 3.475 avevano insieme la
    sicurezza E il prezzo: tutto il resto era archivio morto, meta' di un dato ciascuno.
    La sicurezza serve a spiegare un prezzo. Senza il prezzo accanto, non serve a niente."""
    f = f"data/multichain/{chain}/token_map.json"
    if not os.path.exists(f): return []
    try: tm = {k.lower(): v for k, v in json.load(open(f)).items()}
    except Exception: return []
    pool = [os.path.basename(x).replace(".jsonl.gz", "").lower()
            for x in glob.glob(f"data/multichain/{chain}/serie/*.jsonl.gz")
            + glob.glob(f"data/multichain/{chain}/candele/*.jsonl.gz")
            + glob.glob(f"data/multichain/{chain}/*/*.jsonl.gz")]
    return list(dict.fromkeys(tm[p] for p in pool if p in tm))


def da_rubrica(chain):
    """i token noti dalla rubrica del pulse (pool -> token), inclusi i pool scartati per liquidita'."""
    f = f"data/multichain/{chain}/token_map.json"
    if not os.path.exists(f): return []
    try: return list(dict.fromkeys(json.load(open(f)).values()))
    except Exception: return []


def token_dai_nostri_dati(chain, quanti):
    """L'indirizzo del token lo abbiamo GIA' nei file del pulse (campo 'tk'): nessuna chiamata extra e
    nessuna dipendenza dal fatto che DexScreener conosca ancora quel pool. E' la fonte piu' affidabile."""
    import gzip
    out = []
    fs = glob.glob(f"data/multichain/{chain}/pulse/*.jsonl.gz")
    fs.sort(key=lambda f: os.path.getmtime(f), reverse=True)
    for f in fs[:quanti * 3]:
        try:
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("tk"): out.append(d["tk"]); break
        except Exception: pass
        if len(out) >= quanti * 2: break
    return out


def token_dal_pool(chain, pools):
    """I nostri indirizzi sono POOL, GoPlus vuole il TOKEN. Vale per TUTTE le chain, non solo Solana:
    la prima versione lo faceva solo per Solana e su Base/BSC chiedeva la sicurezza di un pool — che
    ovviamente non esiste come contratto ERC-20, e infatti tornavano zero risultati."""
    out = []
    for i in range(0, min(len(pools), 120), 30):
        try:
            url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/" + ",".join(pools[i:i + 30])
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "wr"}),
                                        timeout=20) as r:
                d = json.loads(r.read())
            for pr in (d.get("pairs") or []):
                b = (pr.get("baseToken") or {}).get("address")
                if b and not b.startswith("So1111") and b.lower() != "0x4200000000000000000000000000000000000006":
                    out.append(b)
        except Exception: pass
        time.sleep(0.3)
        if len(out) >= 400: break
    return out


def giovani(chain, quanti):
    pf = f"data/multichain/{chain}/pools.json"
    if not os.path.exists(pf): return []
    try: pools = json.load(open(pf))
    except Exception: return []
    vivi = [a for a, p in pools.items() if eta_ore(p) <= 240]     # 10 giorni: piu' materiale da censire
    vivi.sort(key=lambda a: pools[a].get("created", ""), reverse=True)
    # ROTAZIONE: se prendessimo sempre i piu' giovani, dopo averli censiti resteremmo fermi. Ogni giro
    # parte da un punto diverso del registro, cosi' in qualche ora lo copriamo tutto.
    if len(vivi) > quanti:
        salto = (now // 1800) % max(1, len(vivi) // quanti)
        vivi = vivi[salto * quanti:] + vivi[:salto * quanti]
    return vivi[:quanti]


def gia_visti(chain):
    f = f"data/sicurezza/{chain}.jsonl"
    if not os.path.exists(f): return set()
    try: return {json.loads(l)["token"] for l in open(f) if l.strip()}
    except Exception: return set()


def main():
    os.makedirs("data/sicurezza", exist_ok=True)
    riep = {}
    for chain in ("base", "solana", "bsc"):
        if time.time() - t0 > BUDGET: break
        visti = gia_visti(chain)
        # DA DOVE ARRIVANO I CANDIDATI (rivisto 02/09 — il collo dell'accumulo).
        # Prima li prendevamo solo dal pulse, che scarta i pool sotto i $5.000 di liquidita': il perito
        # aveva 71 candidati su 43.000 pool scoperti, e il database cresceva di ~50 token al giorno
        # (4 mesi per arrivare all'obiettivo). Ma per costruire il filtro ANTI-TRASH servono proprio i
        # token scartati: sono loro il trash da imparare a riconoscere.
        # Ora si pesca dal registro completo dei pool, risolvendo l'indirizzo via DexScreener (30 per
        # chiamata, gratis). Il collo torna a essere GoPlus (~30 al minuto), non la nostra pipeline.
        # la RUBRICA del pulse: contiene l'indirizzo del token di OGNI pool interrogato, compresi quelli
        # scartati per liquidita' bassa — cioe' proprio il trash che dobbiamo censire.
        # DA DOVE PESCARE (rivisto 02/09): la rubrica del pulse si ESAURISCE — il perito l'aveva censita
        # tutta (Base 239 su 239) e l'accumulo si e' fermato di colpo, senza che nessun controllo lo vedesse
        # (l'ispezione guarda l'archivio totale, che restava alto). Ora, quando la rubrica e' finita, si
        # pesca dal registro completo dei pool: 14.544 su Base contro i 239 della rubrica.
        visti_ora = gia_visti(chain)
        # PRIMA i token che hanno gia' le candele: censire un token di cui non sapremo mai il prezzo
        # e' mezzo dato, e mezzo dato non risponde a nessuna domanda.
        cand = [t for t in con_candele(chain) if t not in visti_ora]
        cand += [t for t in da_rubrica(chain) if t not in visti_ora and t not in cand]
        if len(cand) < MAX:
            # la rubrica non basta piu': si va sul registro completo, dai pool piu' giovani in giu'
            altri = token_dal_pool(chain, giovani(chain, MAX * 6))
            cand += [t for t in altri if t not in visti_ora and t not in cand]
        if not cand:
            cand = [t for t in token_dai_nostri_dati(chain, MAX) if t not in visti_ora]
        cand = [c for c in cand if c not in visti][:MAX]
        n = 0; problemi = 0; senza_dati = 0
        for tk in cand:
            if time.time() - t0 > BUDGET: break
            if chain == "solana":
                res = chiedi(f"https://api.gopluslabs.io/api/v1/solana/token_security?contract_addresses={tk}")
            else:
                res = chiedi(f"https://api.gopluslabs.io/api/v1/token_security/{CHAIN_ID[chain]}"
                             f"?contract_addresses={tk.lower()}")
            time.sleep(PAUSA)
            if not res: senza_dati += 1; continue
            k = list(res)[0]; d = res[k] if isinstance(res[k], dict) else {}
            if chain == "solana":
                riga = {"token": tk, "chain": chain, "ts": now,
                        "mintable": (d.get("mintable") or {}).get("status"),
                        "freezable": (d.get("freezable") or {}).get("status"),
                        "metadata_mutable": (d.get("metadata_mutable") or {}).get("status"),
                        "holder_count": d.get("holder_count"),
                        "top10": sum(float(h.get("percent") or 0) for h in (d.get("holders") or [])[:10]),
                        "lp_locked": sum(float(h.get("percent") or 0) for h in (d.get("lp_holders") or [])
                                         if str(h.get("is_locked")) == "1"),
                        "creator": (d.get("creators") or [{}])[0].get("address") if d.get("creators") else None}
                brutto = riga["freezable"] == "1" or riga["mintable"] == "1"
            else:
                riga = {"token": tk, "chain": chain, "ts": now,
                        "honeypot": d.get("is_honeypot"), "buy_tax": d.get("buy_tax"),
                        "sell_tax": d.get("sell_tax"), "cannot_sell_all": d.get("cannot_sell_all"),
                        "mintable": d.get("is_mintable"), "owner_change_balance": d.get("owner_change_balance"),
                        "hidden_owner": d.get("hidden_owner"), "open_source": d.get("is_open_source"),
                        "holder_count": d.get("holder_count"),
                        "top10": sum(float(h.get("percent") or 0) for h in (d.get("holders") or [])[:10]),
                        "lp_locked": sum(float(h.get("percent") or 0) for h in (d.get("lp_holders") or [])
                                         if str(h.get("is_locked")) == "1"),
                        # IL GRAFO DEI DEPLOYER: chi ha creato il token, quanto ne tiene, e — il campo piu'
                        # prezioso — se lo stesso creatore ha gia' fatto honeypot in passato. Tutto questo
                        # arriva nella stessa risposta che chiediamo per la sicurezza: nessuna chiamata extra.
                        "creator": d.get("creator_address"),
                        "creator_percent": d.get("creator_percent"),
                        "creator_gia_honeypot": d.get("honeypot_with_same_creator"),
                        "owner": d.get("owner_address")}
                try: st_ = float(riga.get("sell_tax") or 0)
                except Exception: st_ = 0
                brutto = (riga.get("honeypot") == "1" or st_ > 0.10 or riga.get("cannot_sell_all") == "1"
                          or str(riga.get("creator_gia_honeypot") or "0") not in ("0", "None", ""))
            if brutto: problemi += 1
            with open(f"data/sicurezza/{chain}.jsonl", "a") as fo:
                fo.write(json.dumps(riga) + "\n")
            n += 1
        riep[chain] = {"nuovi": n, "problemi": problemi, "senza_dati": senza_dati,
                       "archivio": len(visti) + n}

    L = ["# 🛡️ SICUREZZA DEI TOKEN — si possono vendere davvero?",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · fonte GoPlus, gratis*", "",
         "> **Perché**: nel modello un token da cui non si esce risultava come un trade che perde il 70%.",
         "> Nella realtà perde TUTTO. La misura dei costi reali l'ha già mostrato: su 5 token, 4 avevano",
         "> almeno una size non vendibile.", "",
         "| chain | token nuovi controllati | **con problemi** | senza dati | archivio totale |",
         "|---|---|---|---|---|"]
    for ch, r in riep.items():
        L.append(f"| {ch} | {r['nuovi']} | **{r['problemi']}** | {r['senza_dati']} | {r['archivio']} |")
    L += ["", "## Cosa guardiamo", "",
          "- **EVM**: honeypot, tassa di acquisto e vendita, impossibilità di vendere tutto, owner che può",
          "  cambiare i saldi, owner nascosto, contratto non verificato",
          "- **Solana**: mint authority ancora attiva (possono stampare altri token), freeze authority",
          "  (possono congelarti), metadata modificabili",
          "- **Entrambe**: quanti holder ci sono davvero e quanto pesano i primi dieci, quota di liquidità bloccata",
          "",
          "> ⚠️ **Questo archivio si costruisce IN AVANTI.** Interrogare oggi il contratto di un token del",
          "> passato non sarebbe lecito: owner, tasse e permessi possono essere cambiati dopo, e useremmo",
          "> un'informazione che al momento della decisione non esisteva. Diventerà utilizzabile quando i",
          "> token censiti oggi avranno un esito."]
    open("SICUREZZA.md", "w").write("\n".join(L))
    print("SICUREZZA | " + " · ".join(f"{c}: +{r['nuovi']} ({r['problemi']} problematici)"
                                      for c, r in riep.items()), flush=True)


if __name__ == "__main__":
    main()
