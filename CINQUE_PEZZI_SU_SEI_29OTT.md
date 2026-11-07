# Five pieces of six — 29 Oct, morning

| piece | state |
|---|---|
| contract that reverts unless profitable | ✅ compiles clean, no warnings |
| reaction window | ✅ **6.47s median**, confirmed live |
| shortlist of near-threshold positions | ✅ 140 positions, refreshed in 148s |
| listener on the hint stream | ✅ 690 hints/min, survives stalls |
| **Flashbots authentication** | ✅ **signature accepted** |
| full test on a local chain copy | → next |

## The Flashbots signature trap

Worth recording, because it is the kind of thing that costs days.

Flashbots wants the signature over **the characters** of the body's hash —
the ASCII string `"0xabc…"` — not over the bytes those characters represent.
`cast wallet sign` silently decodes any input starting with `0x` into bytes
before signing, so the relay kept answering **"invalid flashbots
signature"** with no explanation.

The fix: hex-encode the ASCII string first, so the tool decodes it back to
exactly the characters we want signed.

Evidence it worked: the error changed from *"invalid flashbots signature"*
to *"rpc method is not whitelisted"*, and then on `eth_callBundle` to
*"incorrect request"* — an error about the dummy data, not about identity.
**We are through the door.**

## On the identity key

It is **not a wallet**. It holds nothing and never will: Flashbots uses it
only to recognise a sender and build reputation. Generated locally, written
straight to a file without passing through any output, `chmod 600`, and
`.chiavi/` is in `.gitignore`.

Still **zero euro**, nothing on-chain.
