# Rebuilding the data — all of it is free, none of it is work

On 27 Oct the local `data/` folder held 700 MB. It was deleted: **every byte
is a cache that public, free endpoints will hand back on request.** What is
not reproducible — code, documents, the external reviewers' output — lives on
GitHub, and was verified published before anything was removed.

| folder | size | rebuild with |
|---|---|---|
| `binance/`, `binance_piccoli/`, `binance_f150/450/600/` | 270 MB | `agents/scarica_binance*.py` |
| `binance_resto/` | 6 MB | `agents/scarica_il_resto.py` |
| `posizionamento/` | 116 MB | `agents/scarica_posizionamento.py` (only 30 days exist at any time) |
| `candele3/`, `candele_hl/`, `binance_hl/` | 106 MB | `agents/scarica_candele3.py` (walks **backwards** — the API ignores startTime) |
| `finanziamento/` (Hyperliquid) | 130 MB | Hyperliquid `fundingHistory` |
| `mercati/`, `azioni/`, `multichain/` | 59 MB | closed families, rebuild only if reopened |

## Kept on purpose

`finanziamento_profondo/` and `finanziamento_resto/` (~12 MB) — the data
behind the only live result, the cross-venue funding spread (+3.2%/year).
Cheap to keep, annoying to refetch.

## The rule this follows

A local file is either **pushed or deleted** — never left as the only copy.
The check ran first and found 19 files that existed nowhere else, including
eleven Grok reviews, which do not regenerate. They were published before the
cleanup, not after.
