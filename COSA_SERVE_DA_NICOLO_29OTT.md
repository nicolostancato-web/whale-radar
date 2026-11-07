# What is needed from Nicolò — 29 Oct

## Two separate wallets, and why

| | key held by | contains | role |
|---|---|---|---|
| **OPERATIVO** | me, on the computer | **only gas** | commands the contract |
| **CASSA** | **only Nicolò** | the profits | receives everything earned |

The contract was changed today so profit goes to **cassa**, never to the
operating wallet. If the operating key were ever compromised, the loss is
the gas and nothing else.

## Steps

1. **Create two new wallets** (MetaMask or Rabby — two accounts inside the
   same app is fine).
2. **From CASSA, I need only the address.** The seed phrase and private key
   stay with Nicolò and must never be sent — I must not be able to reach it.
3. **From OPERATIVO, I need the private key**, written into the credentials
   file under a new section, never in chat:

```
=== LIQUIDATORE ===
Operativo indirizzo: 0x...
Operativo chiave privata: 0x...
Cassa indirizzo: 0x...
```

4. **Fund OPERATIVO with ETH on Ethereum mainnet** — not Base, not Arbitrum,
   not Polygon. Withdrawing to the wrong network loses the funds.

   **€20 is enough**, not fifty. A transaction costs about **€0.08** at
   current gas, so €20 buys **over 200 landed attempts** — and attempts that
   are not profitable are never included, so they cost nothing.

   The one thing to check: **Robinhood's withdrawal fee**. If it is €15 on
   a €20 withdrawal, send €30 once rather than withdrawing twice.

5. Nothing else. No passwords, no cassa seed phrase, no Robinhood access.

## What happens next

1. Deploy the contract — **€0.20**
2. Run the dry run for a few days: the program watches and **writes down
   what it would have done**, sending nothing
3. Only if that log shows we would have been in time at least sometimes:
   **one** small real liquidation

If the dry run says we always lose, I say so and the €20 stays untouched.
