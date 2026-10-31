# Ricerca Grok — dove_stanno_le_x

Modello grok-4.7. Costo: ZERO (abbonamento, nessuna chiave API). Tempo: 265s. 3/3 sotto-domande con risposta.

---

### Esistono misure pubblicate sul percorso del prezzo delle memecoin DOPO la graduazione su piattaforme di lancio EVM: quota che supera 2x, 5x, 10x? Dammi fonti e numeri.

Cerco studi e dataset pubblicati sul prezzo delle memecoin dopo la graduazione su launcher EVM, con le quote che superano 2x, 5x e 10x.I dati più citati sono quasi tutti su Solana. Cerco misure specifiche per i launcher EVM (four.meme, Flap, Virtuals, Base) e se qualcuno pubblica proprio le soglie 2x, 5x e 10x.No. Non risulta pubblicato uno studio che, sulle memecoin graduate da un launchpad EVM, dica quale quota ha poi fatto 2×, 5× o 10× rispetto al prezzo di graduazione. Il buco è proprio quello: i numeri 2×/5×/10× che circolano sono su Solana, e misurano un’altra cosa.

## Cosa è pubblicato sugli EVM

**Sopravvivenza dopo la graduazione, soglia 1× a orario fisso, non il picco.** Lo studio MemeFees (data version 2026-10-01, aggiornato live) confronta la market cap a +1 h, +24 h e +7 giorni con quella alla graduazione. Non pubblica 2×, 5× o 10×, né il massimo raggiunto.

Sul campione misurabile, quasi tutto Solana:

| Orizzonte | Ancora ≥ market cap di graduazione | Mediana pump.fun |
|---|---|---|
| +1 h | 31,8% di 22.579 | 0,23× (n=22.491) |
| +24 h | 9,2% di 21.423 | 0,04×, cioè −96,4% (n=21.337) |
| +7 giorni | 2,9% di 5.273 | 0,04× (n=5.232) |

Fonte: [Memecoin survival study 2026](https://memefees.com/research/memecoin-survival-2026) e [tabella live](https://memefees.com/stats/survival) (snapshot 8 ottobre 2026: pump.fun a +24 h ancora 9%, mediana 0,04×, n=27.869). I controlli senza pool su DexScreener sono esclusi, non contati come fallimento. A 7 giorni i “no pool” (17.252) superano i prezzi trovati.

**four.meme (BNB Chain), il launchpad EVM con bonding curve che tracciano, è a zero.** La pagina dedicata dice esplicitamente “not yet measured”: 0 token misurati a +1 h, +24 h e +7 giorni. Nello studio del 1° ottobre 2026, four.meme ha 1 graduazione in 7 giorni e il feed è marcato “sample only”. Flap.sh non ha proprio una serie di graduazione in quella metodologia. Clanker e Zora non graduano: il token nasce già in una pool Uniswap.

**Tasso di graduazione, cioè quanti ci arrivano, non cosa fanno dopo.**

| Fonte | Piattaforma | Creati | Graduati | Tasso |
|---|---|---|---|---|
| Dune citato da [ChainCatcher, 11 ott 2025](https://www.chaincatcher.com/en/article/2211908) | four.meme | 534.300 | 7.532 | 1,4% |
| Phemex, riportato a ottobre 2025 | four.meme | >384.000 | ~5.150 | ~1,34% |
| [Query Dune 7838277](https://dune.com/queries/7838277/11810650), cumulato al 18 ago 2026 | four.meme | 1.600.960 | 15.497 | 0,97% |
| Stessa query | Flap (BNB) | 2.211.592 | 4.662 | 0,21% |

Esistono query Dune che listano i graduati four.meme e la market cap corrente (circa 15.500 righe), ma nessuno ha pubblicato la distribuzione (ATH o prezzo successivo) / prezzo di graduazione in fasce 2×, 5×, 10×.

**A che market cap si gradua, così si sa cosa varrebbe un 2×.** [Sumo, 12 agosto 2026](https://blog.sumo.trade/what-is-a-bonding-curve/), dollari che si muovono col prezzo di BNB/ETH: four.meme circa 50.000 $ (18 BNB raccolti), Flap circa 41.000 $ (16 BNB), Pons V2 su Robinhood Chain circa 39.000 $. Sono soglie meccaniche della curva, non esiti.

**Virtuals su Base.** Il [whitepaper](https://whitepaper.virtuals.io/about-virtuals/capital-formation-layer/virtuals-launch-mechanics) dice che oltre il 75% dei token ha il giorno di volume massimo proprio alla graduazione. [Blokz, 15 giugno 2026](https://blokz.dev/articles/agent-token-bonding-curve/), leggendo il contratto: la pool Uniswap apre il 12,5% sotto l’ultimo prezzo della curva. [ChainWard, aprile 2026](https://chainward.ai/decodes/agdp-fdv-disconnect/), su 33 agent con dati: 13 graduati, FDV mediana 218.000 $ contro 35.000 $ dei 20 non graduati. Campione piccolo, snapshot dei sopravvissuti, non una quota che ha fatto 2×/5×/10× dal prezzo di graduazione.

## L’unico conteggio 2× / 5× / 10× è Solana, e parte da 700.000 $, non dalla graduazione

Ivan Labrie, [Binance Square](https://www.binance.com/en/square/post/370617558399456): tutti i 14.496 token graduati da pump.fun a gennaio 2026 (graduazione intorno a 69.000 $ di market cap). 171 (1,2%) hanno toccato 700.000 $, cioè già circa 10× dalla graduazione. Da quel livello, al picco:

| Multiplo di 700.000 $ | Token | Su 171 | Su tutti i 14.496 graduati |
|---|---|---|---|
| 2× | 97 | 57% | 0,67% |
| 5× | 34 | 20% | 0,23% |
| 10× | 10 | 6% (~1 su 17; lui scrive “circa 1 su 20”) | 0,07% |
| 100× | 1 (PENGUIN) | — | — |

Tre settimane dopo il lancio, 85 su 14.496 erano sopra 100.000 $ e 12 sopra 1 milione. Otto mesi dopo: 26 e 7. Non è un percorso di prezzo EVM e non è “quota dei graduati che ha fatto 2× dal fill della curva”.

Stesso limite per Coin Metrics / Talos, [State of the Network n. 384, 6 ottobre 2026](https://coinmetrics.substack.com/p/state-of-the-network-issue-384): 150–151 memecoin dell’era Solana che hanno un prezzo su almeno un CEX. L’81% è sceso almeno del 90% dal massimo; la mediana tocca il massimo a 17,2 giorni e poi perde il 95% in 370 giorni; 5 token su 151 sono sopra il prezzo del primo giorno. Gli autori scrivono che il campione sovrastima la vita tipica, perché esclude chi non esce dal launchpad.

In sintesi: su EVM è pubblicato il filtro di ingresso (circa l’1% dei lanci four.meme gradua, circa lo 0,2% su Flap) e, per analogia Solana, il fatto che a 24 ore la mediana dei graduati vale il 4% della market cap di graduazione. La quota che dopo la graduazione supera 2×, 5× o 10×, su four.meme, Flap, Virtuals o gli altri launcher EVM, non è stata pubblicata.

### Qual e' la quota di memecoin che va praticamente a zero dopo la graduazione, secondo misure pubblicate? Col metodo dichiarato e il link.

Cerco misure pubblicate sulla quota di memecoin che va a zero dopo la graduazione, con il metodo dichiarato e la fonte.Le misure sulla graduazione da sole non bastano: cerco quelle che seguono il prezzo dopo la migrazione, con il criterio usato per dire “praticamente a zero”.**L’82,4%** dei token che hanno graduato, in una misura pubblicata, scambia oggi sotto i **5.000 dollari**.

È il dato di Cabal Hunter del 14 agosto 2026: su **817** lanci che hanno toccato circa **69.000 dollari** di market cap (la soglia che usano come graduazione), **673** sono sotto i 5.000 dollari. Partire da ~69.000 e finire sotto 5.000 è un drawdown di oltre il 90%.

**Metodo dichiarato**

* Corpus: 14.597 wallet deployer osservati da Cabal Hunter tra il 14 giugno e il 14 agosto 2026. Entrano perché qualcuno li ha fatti scansionare, quindi non è un campione casuale della chain.
* Picco: massimo dell’high orario delle candele pump.fun in dollari, per tutta la vita del token, moltiplicato per la supply standard di 1 miliardo.
* Market cap attuale: coppia con più liquidità su DexScreener, snapshot del 14 agosto 2026.
* Soglia di graduazione fissata a 69.000 dollari (il valore reale si muove col prezzo di SOL).
* Campione usato: 32.260 lanci di 2.852 wallet con picco osservato dalle candele. Esclusi i lanci senza candele o con fallback “picco = valore attuale” (circa il 18%).

Loro stessi scrivono che il tasso descrive questo corpus, non un censimento di pump.fun, e che “ora sotto i 5.000” è uno snapshot: i lanci recenti hanno avuto meno tempo per crollare.

Link: https://cabal-hunter.com/blog/pumpfun-graduation-is-not-safety

### Quanto tempo passa in mediana fra la graduazione e il prezzo massimo, secondo misure pubblicate? Col link.

Cerco nel contesto del lavoro e nelle misure pubblicate il tempo mediano fra graduazione e prezzo massimo.La mediana fra la graduazione e il prezzo massimo non è pubblicata. Le misure uscite misurano un altro intervallo, e non la ricavo per differenza.

La misura più vicina è di Coin Metrics (Victor Ramirez, *State of the Network* n. 384, 6 ottobre 2026): su 150 memecoin Solana con un prezzo su almeno un exchange centralizzato, dal dicembre 2023, il massimo arriva **17,2 giorni dopo il primo scambio**, e un quarto dei token lo tocca entro **1,6 giorni**. L’orologio parte dal primo scambio, non dalla graduazione. Il campione esclude chi non arriva mai su un exchange centralizzato, quindi allunga la vita rispetto a un token rimasto sul launchpad.

https://coinmetrics.substack.com/p/state-of-the-network-issue-384
