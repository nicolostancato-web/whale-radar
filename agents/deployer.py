#!/usr/bin/env python3
"""
DEPLOYER — chi crea questi token, e i suoi precedenti.

Ultimo punto della consulenza esterna (01/09), e quello che il quant indicava come *"probabilmente piu'
prezioso del vostro prezzo orario"*: non guardare il token, guardare CHI l'ha fatto. Un deployer che ha
gia' lasciato dietro di se' honeypot e rug e' un'informazione disponibile PRIMA di comprare, e vale piu'
di qualunque indicatore sul grafico.

I dati arrivano dalla stessa risposta che gia' chiediamo per la sicurezza (GoPlus): creator_address,
quanto ne tiene, e se lo stesso creatore ha gia' prodotto honeypot. Nessuna chiamata in piu', nessun costo.

Scrive DEPLOYER.md + data/deployer.json. €0.
"""
import json, os, glob, time, collections

now = int(time.time())


def carica():
    righe = []
    for f in glob.glob("data/sicurezza/*.jsonl"):
        try:
            for l in open(f):
                if l.strip(): righe.append(json.loads(l))
        except Exception: pass
    return righe


def main():
    righe = carica()
    con_creator = [r for r in righe if r.get("creator")]
    if not con_creator:
        open("DEPLOYER.md", "w").write(
            "# 👤 DEPLOYER\n\n*Nessun creatore censito ancora: l'archivio si costruisce in avanti, "
            "man mano che i token vengono controllati.*\n")
        print("DEPLOYER | nessun creatore ancora", flush=True); return

    per_creator = collections.defaultdict(list)
    for r in con_creator: per_creator[r["creator"]].append(r)

    seriali = {c: v for c, v in per_creator.items() if len(v) > 1}
    sospetti = [r for r in con_creator if str(r.get("creator_gia_honeypot") or "0") not in ("0", "None", "")]
    # quanto tiene il creatore: se ne tiene molto, puo' scaricartelo addosso
    tengono_molto = []
    for r in con_creator:
        try:
            p = float(r.get("creator_percent") or 0)
            if p > 0.05: tengono_molto.append((r["token"], p * 100))
        except Exception: pass

    json.dump({"ts": now, "token_con_creatore": len(con_creator), "creatori": len(per_creator),
               "seriali": len(seriali), "gia_honeypot": len(sospetti)}, open("data/deployer.json", "w"))

    L = ["# 👤 DEPLOYER — chi crea questi token, e cosa ha fatto prima",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · dai dati di sicurezza, nessuna chiamata extra*", "",
         "> La consulenza esterna indicava questa come l'area **più preziosa del prezzo orario**: non guardare",
         "> il token, guardare CHI l'ha fatto. I precedenti di un creatore sono noti PRIMA di comprare.", "",
         "| | quanti |", "|---|---|",
         f"| token con creatore identificato | **{len(con_creator)}** |",
         f"| creatori distinti | {len(per_creator)} |",
         f"| **creatori seriali** (più di un token) | **{len(seriali)}** |",
         f"| token il cui creatore ha già fatto honeypot | **{len(sospetti)}** |",
         f"| token dove il creatore tiene oltre il 5% | {len(tengono_molto)} |", ""]
    if seriali:
        L += ["## I creatori seriali", "", "| creatore | token creati |", "|---|---|"]
        for c, v in sorted(seriali.items(), key=lambda kv: -len(kv[1]))[:10]:
            L.append(f"| `{c[:10]}…{c[-6:]}` | {len(v)} |")
        L += [""]
    if sospetti:
        L += ["## ⚠️ Token il cui creatore ha precedenti di honeypot", ""]
        for r in sospetti[:10]:
            L.append(f"- `{r['token'][:12]}…` ({r['chain']})")
        L += ["", "> Questi non andrebbero comprati, e lo sappiamo **prima**, non dopo.", ""]
    L += ["> L'archivio cresce a ogni giro: più token censiamo, più i precedenti dei creatori diventano",
          "> visibili. Un creatore diventa interessante solo quando ha una storia — e la storia si accumula."]
    open("DEPLOYER.md", "w").write("\n".join(L))
    print(f"DEPLOYER | {len(con_creator)} token | {len(per_creator)} creatori | "
          f"{len(seriali)} seriali | {len(sospetti)} con precedenti", flush=True)


if __name__ == "__main__":
    main()
