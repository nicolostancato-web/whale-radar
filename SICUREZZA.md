# 🛡️ SICUREZZA DEI TOKEN — si possono vendere davvero?
*2026-09-12 15:24 UTC · fonte GoPlus, gratis*

> **Perché**: nel modello un token da cui non si esce risultava come un trade che perde il 70%.
> Nella realtà perde TUTTO. La misura dei costi reali l'ha già mostrato: su 5 token, 4 avevano
> almeno una size non vendibile.

| chain | token nuovi controllati | **con problemi** | senza dati | archivio totale |
|---|---|---|---|---|
| base | 18 | **0** | 11 | 4713 |
| solana | 1 | **0** | 2 | 2468 |
| bsc | 2 | **0** | 0 | 1471 |

## Cosa guardiamo

- **EVM**: honeypot, tassa di acquisto e vendita, impossibilità di vendere tutto, owner che può
  cambiare i saldi, owner nascosto, contratto non verificato
- **Solana**: mint authority ancora attiva (possono stampare altri token), freeze authority
  (possono congelarti), metadata modificabili
- **Entrambe**: quanti holder ci sono davvero e quanto pesano i primi dieci, quota di liquidità bloccata

> ⚠️ **Questo archivio si costruisce IN AVANTI.** Interrogare oggi il contratto di un token del
> passato non sarebbe lecito: owner, tasse e permessi possono essere cambiati dopo, e useremmo
> un'informazione che al momento della decisione non esisteva. Diventerà utilizzabile quando i
> token censiti oggi avranno un esito.