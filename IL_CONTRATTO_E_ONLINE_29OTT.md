# The contract is live — 29 Oct

```
contract:   0xE30b58692FB7a1a417d3e0F1F5585a8Bc4D51212
padrone:    0x4355962379C779009F833d81bd8D2912773749A0   (operating, commands)
cassa:      0x055e75aEaCF141c3118d039D5E099a821152eB66   (Nicolò's, receives profit)
Aave pool:  0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2
```

Read back from the contract itself. Both addresses are **immutable** —
nobody, including me, can change where the money goes.

**Deployment cost: $0.10.** I had said twenty cents; ten were enough.

## Funds

| wallet | balance |
|---|---|
| operating `0x4355…49A0` | **0.01643 ETH ≈ $38** |
| cassa `0x055e…eB66` | **0** — correct, it only receives |
| leftover on Robinhood chain | 0.00088 ETH ≈ $2 (gas there) |

The bridge from Robinhood Chain to Ethereum via Relay cost **7 cents** and
took seconds. $38 of gas is **over 400 landed attempts**, and attempts that
are not profitable are never included, so they cost nothing at all.

## Next

The dry run: the program listens, recognises opportunities and **writes down
what it would have done**, sending nothing. A few days of log, then the
numbers say whether a real attempt is worth making.

Nothing has been risked beyond the ten cents of deployment.
