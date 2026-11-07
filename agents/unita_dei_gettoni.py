# -*- coding: utf-8 -*-
"""VERIFICA UNITA' DI OGNI GETTONE SULLA CATENA.
Nato il 3/11 da un errore trovato prima di usarlo: il file prezzi dava
0x356b8d89 a 1,15 dollari con 6 decimali, mentre e' un derivato di ETH.
Armarlo avrebbe sbagliato la quantita' di vendita di un fattore miliardario.
REGOLA: un gettone entra nell'elenco ammessi SOLO dopo che simbolo e
decimali sono letti dal suo contratto e il prezzo e' coerente col simbolo.
"""
import json, sys, urllib.request
sys.path.insert(0, "agents")
FONTI = ["https://gateway.tenderly.co/public/mainnet",
         "https://ethereum-rpc.publicnode.com",
         "https://rpc.mevblocker.io"]
def chiama(to, dati):
    # piu' di una fonte: il 3/11 publicnode ha risposto 403 senza intestazione.
    # Si prova in ordine e si smette alla prima che risponde: non si martella.
    c = {"jsonrpc":"2.0","id":1,"method":"eth_call",
         "params":[{"to":to,"data":dati},"latest"]}
    ultimo = None
    for u in FONTI:
        try:
            r = urllib.request.urlopen(urllib.request.Request(u,
                json.dumps(c).encode(),
                {"Content-Type":"application/json",
                 "User-Agent":"Mozilla/5.0"}), timeout=20)
            return json.load(r).get("result")
        except Exception as e:
            ultimo = e
    raise RuntimeError(f"nessuna fonte risponde: {ultimo}")
def stringa(h):
    if not h or len(h) < 130: return None
    b = bytes.fromhex(h[2:])
    n = int.from_bytes(b[32:64], "big")
    return b[64:64+n].decode("utf8", "ignore")
def dec(h): return int(h, 16) if h and h != "0x" else None
PR = json.load(open("data/liquidazioni/prezzi_oracolo.json"))
from pescatore import AMMESSI
CAND = ["0xa1290d69c65a6fe4df752f95823fae25cb99e5a7",
        "0xf1c9acdc66974dfb6decb12aa385b9cd01190e38",
        "0x4c9edd5852cd905f086c759e8383e09bff1e68b3",
        "0x356b8d89c1e1239cbbb9de4815c39a1474d5ba7d",
        "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf",
        "0xae78736cd615f374d3085123a210448e74fc6393",
        "0xbe9895146f7af43049ca1c1ae358b0541ea49704",
        "0x8236a87084f8b84306f72007f36f2618a5634494",
        "0x68749665ff8d2d112fa859aa293f07a622782f38",
        "0x18084fba666a33d37592fa2633fd49a74dd93a88"]
print(f"{'gettone':12s} {'simbolo':10s} {'dec catena':>10s} {'dec file':>9s} "
      f"{'prezzo file':>13s}  esito")
righe = []
for a in sorted(set(list(AMMESSI) + CAND)):
    s = stringa(chiama(a, "0x95d89b41"))      # symbol()
    d = dec(chiama(a, "0x313ce567"))          # decimals()
    p = PR.get(a, {})
    pf, df = p.get("prezzo_usd"), p.get("decimali")
    esito = "OK"
    if df is None: esito = "nessun prezzo"
    elif d != df:  esito = f"!! DECIMALI SBAGLIATI (catena {d})"
    armato = "armato" if a in AMMESSI else "candidato"
    righe.append((a, s, d, df, pf, esito, armato))
    print(f"{a[:10]:12s} {str(s):10s} {str(d):>10s} {str(df):>9s} "
          f"{(('%.4f'%pf) if pf else '-'):>13s}  {esito} [{armato}]")
guasti = [r for r in righe if "SBAGLIATI" in r[5]]
print(f"\n{len(guasti)} gettoni con le unita' sbagliate nel file prezzi")
for r in guasti: print("  ", r[0], r[1], "catena", r[2], "file", r[3], f"[{r[6]}]")
json.dump([{"gettone":r[0],"simbolo":r[1],"decimali":r[2],"prezzo":r[4],
            "esito":r[5],"stato":r[6]} for r in righe],
          open("data/liquidazioni/unita_gettoni.json","w"), indent=1)
