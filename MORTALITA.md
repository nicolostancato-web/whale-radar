# ⚰️ MORTALITÀ — quanti token spariscono prima di entrare nei nostri conti
*2026-09-15 20:02 UTC*

> **Perché conta:** impariamo sui token sopravvissuti abbastanza da avere una serie di prezzi. Chi
> muore subito non entra nel campione — quindi nello storico ci sono **meno −100% di quanti ne
> incontreremmo davvero**, e ogni percentuale che calcoliamo è ottimista di conseguenza.

| chain | pool scoperti (>12h) | mai tentati (limite nostro) | **tentati** | senza dati = morti | tasso di morte |
|---|---|---|---|---|---|
| base | 14727 | 12717 | 2010 | **457** | **23%** |
| solana | 14733 | 13158 | 1575 | **389** | **25%** |
| bsc | 17461 | 16380 | 1081 | **353** | **33%** |

## Come si legge

**"Mai tentati"** non è mortalità: è un limite nostro (le API gratuite ci lasciano scaricare
poche decine di pool per giro su migliaia scoperti). Quelli non dicono niente sul mercato.

**Il tasso di morte vero** è calcolato solo sui pool che abbiamo davvero interrogato: in media
il **27%** di quelli non ha mai prodotto una serie di prezzi utilizzabile — nati morti,
o morti entro poche ore.

**Regola prudente:** finché non misuriamo quanti muoiono DOPO l'entrata, trattiamo ogni
percentuale come ottimista di almeno qualche punto, e non apriamo mai il live su un numero
appena sopra la soglia. È uno dei motivi per cui il cancello è a +40% e non a +5%.

> Prossimo passo su questo: contare i token che avevano dati e poi **smettono di aggiornarsi**
> mentre il prezzo crolla — quelli sono i rug veri, ed è lì che si nasconde il -100% che non vediamo.