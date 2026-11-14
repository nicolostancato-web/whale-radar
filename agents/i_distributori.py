"""CHI DISTRIBUISCE I GETTONI, E COME CI SI ENTRA.

== PERCHE' QUESTA DOMANDA E' LA PIU' IMPORTANTE (23/10, richiamata da Nicolo') ==

Emerse su Robinhood mesi fa — «vedo le vendite ma non gli acquisti» — e fu parcheggiata per
guardare chi compra. Misurata dopo: il 27% del venduto su Solana e il 32% su Base viene da chi
i gettoni non li ha mai comprati. Ed e' l'UNICA posizione che in tre chain risulta in utile:
un portafoglio ha incassato ~53 SOL (9.500 EUR) vendendo gettoni mai pagati, spendendo meno di
1 SOL di cauzioni e commissioni.

La domanda non e' piu' «esiste?» ma «COME ci arrivano?». Le strade possibili sono diverse e
solo alcune sono aperte a chi non e' dentro:
  - quota della squadra o del creatore, sbloccata da un contratto di rilascio
  - prevendita a cui ci si iscrive
  - regalo per aver fatto certe operazioni (il caso interessante: si puo' qualificarsi)
  - acquisto fatto altrove e portato li'

Qui si parte dai MITTENTI: chi sono, quanti destinatari servono, con che programma, e se lo
stesso mittente serve molti indirizzi diversi (distribuzione) o pochi (quote interne).
"""
import collections, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import solana_rpc as S

NOTI = ["GU63SH4oypiFiLC14FVfyEwC4zqmPe", "3XDcE2tQRocmrXB2rKbYpQff6r7hKQ"]
FUORI = "data/multichain/solana/distributori.json"


def main():
    # 1) i mittenti completi: si ricavano dalle transazioni dei portafogli che ricevono
    storie = [json.loads(r) for r in open("data/multichain/solana/storia2.jsonl")]
    mitt = collections.Counter()
    dest = collections.defaultdict(set)
    prog = collections.Counter()
    chiam = 0
    for d in storie:
        w = d["w"]
        if not d.get("regali"):
            continue
        sig = S.rpc("getSignaturesForAddress", [w, {"limit": 120}]) or []
        chiam += 1
        for x in sig[:60]:
            if x.get("err"):
                continue
            t = S.rpc("getTransaction", [x["signature"],
                      {"maxSupportedTransactionVersion": 2, "encoding": "jsonParsed",
                       "commitment": "confirmed"}])
            chiam += 1
            if not t:
                continue
            meta = t["meta"]
            pre = {y["accountIndex"]: float(y["uiTokenAmount"]["uiAmount"] or 0)
                   for y in meta.get("preTokenBalances", [])}
            rec = [y for y in meta.get("postTokenBalances", [])
                   if y.get("owner") == w and
                   float(y["uiTokenAmount"]["uiAmount"] or 0) - pre.get(y["accountIndex"], 0.0) > 0]
            if not rec:
                continue
            for y in meta.get("postTokenBalances", []):
                if y.get("owner") and y.get("owner") != w and \
                   float(y["uiTokenAmount"]["uiAmount"] or 0) - pre.get(y["accountIndex"], 0.0) < 0:
                    mitt[y["owner"]] += 1
                    dest[y["owner"]].add(w)
            for i in t["transaction"]["message"].get("instructions", []):
                p = str(i.get("program") or i.get("programId", ""))
                if "ComputeBudget" not in p:
                    prog[p] += 1
            time.sleep(0.01)
    print(f"I DISTRIBUTORI | {chiam} chiamate\n")
    print(f"   {'mittente':<34}{'consegne':>10}{'destinatari':>13}")
    print('   ' + '-' * 58)
    for m, n in mitt.most_common(8):
        print(f"   {m[:32]:<34}{n:>10}{len(dest[m]):>13}")
    print('   ' + '-' * 58)
    print(f"\n   programmi coinvolti nelle consegne:")
    for p, n in prog.most_common(6):
        print(f"      {p[:44]:<46}{n}")
    json.dump({"mitt": dict(mitt.most_common(50)),
               "dest": {k: sorted(v) for k, v in list(dest.items())[:50]}}, open(FUORI, "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
