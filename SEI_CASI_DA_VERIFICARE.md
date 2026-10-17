# Sei casi da verificare a mano — 6 ottobre 2026

## Come si verificano (importante)

**L'acquisto su DexScreener NON si vede.** Non è uno scambio del pool: è un acquisto sulla
*curva*, il mercato che esiste prima. Si vede solo sull'esploratore della chain:

> <https://robinhoodchain.blockscout.com>

Si incolla l'hash della transazione nella ricerca. Su DexScreener si vede la **vendita**, non
l'acquisto.

Ogni caso qui sotto l'ho verificato io prima di scriverlo: entrambe le transazioni esistono,
entrambe sono riuscite, **entrambe firmate dal portafoglio stesso** (non da un router), e i
gettoni venduti sono **esattamente** quelli comprati (rapporto 1,0).

---

## Caso 1

| | |
|---|---|
| portafoglio | `0x59d173dd7606d1d172c186e9edf59e83a39e013f` |
| moneta | `0x2ad522452ea0a85774a6c6a8ae0e9f4fec3b2ce1` |
| gettoni comprati sulla curva | **3,007,275** |
| **acquisto sulla curva** | 25/08 23:26 UTC, blocco 46,121,624 |
| | `0xe29021e1b1017f2717d72233e6136290043dceb91fb7974474260198ac05bc1b` |
| **vendita nel pool** | 25/08 23:26 UTC, blocco 46,121,748 — 13 secondi dopo |
| | `0xa9d98d10139411870562fb81ecf8fa63fc801f644405d470be1d48d442edca44` |
| gettoni venduti / comprati | **1.0** |

## Caso 2

| | |
|---|---|
| portafoglio | `0x59d173dd7606d1d172c186e9edf59e83a39e013f` |
| moneta | `0xc4f36c7c1d00dcaab1d01159466afa189bfc7161` |
| gettoni comprati sulla curva | **2,412,119** |
| **acquisto sulla curva** | 27/08 16:45 UTC, blocco 47,595,425 |
| | `0x84ee83423bd0135128f5a6c8c2dd70b373dfd0cc79a4891ebece1aa8cd08e9ea` |
| **vendita nel pool** | 27/08 16:45 UTC, blocco 47,595,459 — 3 secondi dopo |
| | `0xe1e6fe1095f4808fa5bbd5578fac09b638672fb2f1d6359cc72646f35a2ed08c` |
| gettoni venduti / comprati | **1.0** |

## Caso 3

| | |
|---|---|
| portafoglio | `0xffe55d878f234a89755fc0fcb6a9651b1d814c27` |
| moneta | `0x56b5b96e31ebebcb35937835df7c700b881b1986` |
| gettoni comprati sulla curva | **27,528,583** |
| **acquisto sulla curva** | 01/09 05:55 UTC, blocco 51,485,787 |
| | `0x3f75538c89a6af5bb4759fb01b4be53e77460b928dcbcbb654cde84892c7aebd` |
| **vendita nel pool** | 01/09 06:13 UTC, blocco 51,496,612 — 18 minuti dopo |
| | `0xc2bb42418b49047c5537c55c7eee366c26d9b9988639cc76ee488a7e5cadbcc2` |
| gettoni venduti / comprati | **1.0** |

## Caso 4

| | |
|---|---|
| portafoglio | `0x1d05f7edae2ad5df71e67b64d4ca335f20f6ad5c` |
| moneta | `0x03418705b732cdce195e776ed9b8331949178857` |
| gettoni comprati sulla curva | **3,253,827** |
| **acquisto sulla curva** | 04/09 22:38 UTC, blocco 54,627,180 |
| | `0xb2d87515b072260a932b62a35cbc848ef6dd08a826cce442a14b1801fbc78906` |
| **vendita nel pool** | 04/09 23:16 UTC, blocco 54,649,720 — 38 minuti dopo |
| | `0xad91f59934e5b1fc793290ea9fa6a585b57673ee6ba5ef6bb067e56e73980b95` |
| gettoni venduti / comprati | **1.0** |

## Caso 5

| | |
|---|---|
| portafoglio | `0xffe55d878f234a89755fc0fcb6a9651b1d814c27` |
| moneta | `0xbacd39ade9a69147251b601603c11247ceacf849` |
| gettoni comprati sulla curva | **6,859,096** |
| **acquisto sulla curva** | 12/09 22:20 UTC, blocco 61,454,776 |
| | `0x3e43b2398ee0dff01df0b404729c06c279beede94e60a476f9f08d9b24148574` |
| **vendita nel pool** | 12/09 22:20 UTC, blocco 61,455,138 — 37 secondi dopo |
| | `0xb3e5bd822eaf1418842752f881a78fb0d32c3ca8d38e15b5c762a3b39decb493` |
| gettoni venduti / comprati | **1.0** |

## Caso 6

| | |
|---|---|
| portafoglio | `0x8f60800324387613070ad3433a14a6d079f164d3` |
| moneta | `0xb7b0cad6e560bda279f238a42c695cb2b1681227` |
| gettoni comprati sulla curva | **16,246,441** |
| **acquisto sulla curva** | 13/09 05:09 UTC, blocco 61,697,248 |
| | `0x18a187aa9a8343ecc5043dbc5603fe2a4b17ff1022f356e70609d2d8b71d2249` |
| **vendita nel pool** | 13/09 05:21 UTC, blocco 61,703,863 — 11 minuti dopo |
| | `0xcb98fd20f99404e61cfeb84dc338bcc4cce6608af474de21a83e981442a6aacb` |
| gettoni venduti / comprati | **1.0** |

---

## Un avvertimento sulla scelta di questi sei

Li ho scelti perché il rapporto è **esattamente 1,0**: un solo acquisto, una sola vendita, niente
di ambiguo. Sono i più facili da verificare, e proprio per questo **non sono i più
rappresentativi**: i giri semplici tendono a essere anche i più veloci. La tenuta mediana misurata
su tutta la popolazione è di **5,5 ore**, non di pochi minuti come in questi sei.

È lo stesso errore che avevo fatto stamattina mostrando un singolo caso da 13 secondi come se
fosse la norma. Scegliere per verificabilità non è scegliere per tipicità, e va detto ogni volta.

## E cosa NON dicono questi casi

Che i gettoni tornano — cioè che i dati sono veritieri. **Non** che si guadagna: il conto onesto
sul capitale, con il gas dentro e contando le posizioni mai vendute come perdita, resta **sotto 1
in ogni posizione della fila** (vedi `ENTRARE_PRIMI_NON_PAGA.md`).
