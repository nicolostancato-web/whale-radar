"""CHI INCASSA LO SPREAD DOPO IL DIPLOMA?

Misurato oggi: chi paga lo spread perde 1,01% a giro, chi lo incassa guadagna
0,72%. Per tre mesi siamo stati dalla parte che paga. Questa e' la prima volta
che guardiamo l'altra.

Nel pre-diploma la commissione del pool Pons e' ZERO e se la prende il
protocollo. Dopo il diploma i pool sono v4 normali: la commissione potrebbe
andare a chi mette la liquidita'. Qui si guarda, per i pool post-diploma:
   1. la commissione dichiarata e l'hook (dall'evento Initialize)
   2. se esistono eventi ModifyLiquidity, cioe' se qualcuno mette liquidita'
   3. se esistono Donate, cioe' se l'hook restituisce agli LP (ipotesi di Astra)
"""
import json, os, urllib.request, collections, gzip, glob
RPC = os.environ.get("RPC_ROBINHOOD", "https://rpc.mainnet.chain.robinhood.com")
GEST = "0x8366a39cc670b4001a1121b8f6a443a643e40951"
# firme degli eventi v4
INIT = "0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
MODL = "0xf208f4912782fd25c7f114ca3723a2d5dd6f3bcc3ac8db5af63baa85f711d5ec"
DONA = "0x29ef05caaff9404b7cb6d1c0e9bbae9eaa7ab2541feba1a9c4248594c08156cb"

def rpc(m, p):
    r = urllib.request.Request(RPC, json.dumps({"jsonrpc":"2.0","id":1,"method":m,
        "params":p}).encode(), {"content-type":"application/json"})
    with urllib.request.urlopen(r, timeout=45) as f:
        return json.load(f).get("result")

# prendo i pool diplomati piu' recenti dall'archivio
pool = {}
with gzip.open(sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl.gz"))[0],"rt") as fh:
    for i, riga in enumerate(fh):
        if i > 400: break
        try: d=json.loads(riga)
        except Exception: continue
        if d.get("diploma"): pool[d["pool"]] = d["diploma"]
print(f"{len(pool)} pool diplomati dall'archivio")

ult = int(rpc("eth_blockNumber", []) or "0x0", 16)
print(f"ultimo blocco: {ult:,}\n")

campione = list(pool.items())[:6]
for pid, dip in campione:
    da, a = hex(dip-5), hex(dip+200)
    logs = rpc("eth_getLogs", [{"address": GEST, "topics":[[INIT,MODL,DONA], pid],
                                "fromBlock": da, "toBlock": a}]) or []
    c = collections.Counter()
    fee = hook = None
    for L in logs:
        t0 = L["topics"][0]
        c[{INIT:"Initialize", MODL:"ModifyLiquidity", DONA:"Donate"}.get(t0, t0[:10])] += 1
        if t0 == INIT:
            dati = L["data"][2:]
            # Initialize(id indexed, c0 indexed, c1 indexed, fee, tickSpacing, hooks, sqrt, tick)
            fee = int(dati[0:64], 16)
            hook = "0x" + dati[128+24:192]
    print(f"   {pid[:18]}…  fee={fee}  hook={hook[:14] if hook else '?'}…  {dict(c)}")

print("\n   fee e' in centomillesimi: 3000 = 0,30% | 10000 = 1,00% | 8388608 = dinamica")
