# Ricerca Grok — 2026-10-07 19:19 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 428s

---

La domanda parla di «questo mestiere» senza definirlo qui. Prima recupero il contesto della sessione, poi cerco solo fonti primarie.Il fascicolo precedente su chi fa questo di mestiere è stato scartato perché troppo corto. Leggo il formato richiesto e le ricerche già chiuse, così non ripeto numeri già bocciati.Il mestiere è la coltivazione industriale di identità per le distribuzioni gratuite. Cerco annunci, liste e studi firmati da chi li ha pubblicati, non riassunti.Un registro pubblico di chi fa questo mestiere, col nome e col numero di identità, non risulta. I documenti ufficiali identificano indirizzi e gruppi di indirizzi. Non nominano le persone né le società che li muovono. Su Base non c’è una lista di esclusi, perché non c’è una distribuzione: il post di BaseCamp 2025 esplora un token di rete senza allocazione, senza claim e senza criteri. [The State of Base at BaseCamp 2025](https://blog.base.org/the-state-of-base-at-basecamp-2025).

Tre cose si possono verificare.

## 1. LayerZero: la scala, e la lista che oggi non si apre

Il post ufficiale definisce il mestiere industriale come «a single entity with tens, hundreds, or thousands of addresses». Nello stesso testo: NFT senza valore spostati solo per toccare le chain, ponti da 0,01 dollaro, e l’uso di applicazioni di farming (Merkly, L2Pass, L2Marathon). Chi si autodenuncia entro il 17 maggio 2024, 23:59 UTC, tiene il 15% dell’allocazione prevista. Chi viene identificato e non si è autodenunciato riceve zero. Per i gruppi industriali il post prevede un’API di denuncia in massa, non solo il collegamento di un portafoglio alla volta. [Addressing Sybil Activity](https://medium.com/layerzero-official/addressing-sybil-activity-a2f92218ddd3).

Il 18 maggio 2024, 00:10 UTC, l’account ufficiale scrive che l’autodenuncia più l’analisi di LayerZero, Chaos Labs e Nansen ha segnato **803.093 indirizzi** come sybil potenziali. La stessa analisi aveva marcato oltre 2 milioni di indirizzi e poi ha stretto il criterio per ridurre i falsi positivi. Il post dice che la lista è preliminare, che serve a togliere i grandi gruppi dalla caccia con taglia, e che non è definitiva fino al rapporto finale. La taglia, dal 18 maggio 02:00 UTC al 31 maggio 23:59 UTC, richiede almeno 20 indirizzi e paga il 10% dell’allocazione prevista. [Post del 18 maggio 2024](https://x.com/LayerZero_Core/status/1791622471965163597).

Il link di quel post porta a `github.com/LayerZero-Labs/sybil-report`, file `initialList.csv.zip`. Il 7 ottobre 2026 quella pagina risponde «Page not found». Il CSV provvisorio successivo, pubblicato dal CEO su `lzprovisionalsybil.s3.amazonaws.com/provisionalSybilList2.0.csv`, lo stesso giorno risponde 403. Il conteggio finale degli indirizzi esclusi non è nel post di lancio.

Quel post, del 20 giugno 2024, dice un’altra cifra: fra autodenunce, taglie e il lavoro con Nansen e Chaos Labs sono stati tenuti fuori **circa 10.000.000 ZRO, circa l’1% dell’offerta** (offerta fissa: 1 miliardo). Non riconcilia questo importo con i 803.093 indirizzi, e non pubblica il numero finale di indirizzi. Nello stesso testo, le transazioni sotto 1 dollaro e gli NFT senza valore pesano l’80% in meno nel calcolo dell’allocazione. [Introducing ZRO](https://info.layerzero.foundation/introducing-zro-d39df554a9b7).

## 2. ZKsync: la regola scritta, senza la lista dei tolti

La pagina ufficiale, letta il 7 ottobre 2026, toglie i gruppi di conti esterni con **più di 20 indirizzi** legati da uno di due criteri.

* Stesso indirizzo di deposito su un exchange centralizzato, in una finestra di un anno. L’exchange dà in genere un deposito per cliente: più indirizzi che versano lì sono trattati come la stessa mano.
* Stesso finanziatore ultimo, con importi simili dentro una finestra di tempo. La pagina non pubblica né la durata della finestra né lo scarto di importo ammesso. L’esempio disegnato è uno sciame di **1.029 conti**, finanziati in ultima istanza attraverso un exchange.

Lo snapshot è il 24 marzo 2024, 00:00 UTC (blocco Era 29.710.983). I portafogli idonei pubblicati sono **695.232**, nel file `eligibility_list.csv`. È la lista di chi resta, non di chi è stato tolto. Senza l’universo precedente al filtro, gli esclusi non si ricostruiscono. [ZK Airdrop](https://docs.zknation.io/zk-token/zk-airdrop), [elenco idonei](https://github.com/ZKsync-Association/zknation-data/blob/main/eligibility_list.csv).

La stessa pagina esclude, a prescindere dal comportamento, chi risulta negli Stati Uniti e chi risulta in Cuba, Iran, Corea del Nord, Russia, Siria e nelle regioni ucraine di Crimea, Donetsk e Luhansk, per le sanzioni OFAC, ONU, UE e Regno Unito.

## 3. Hop: l’unica lista di indirizzi ancora scaricabile, e lo studio che misura come sono finanziati

Il file ufficiale `eliminatedSybilAttackers.csv`, letto il 7 ottobre 2026 dal repository di Hop, ha un’intestazione `address` e **14.195 indirizzi unici**, tutti nel formato di un indirizzo EVM. [File](https://github.com/hop-protocol/hop-airdrop/blob/master/src/data/eliminatedSybilAttackers.csv), [regole di segnalazione](https://github.com/hop-protocol/hop-airdrop): un rapporto vale se contiene almeno 10 indirizzi ancora idonei; il programma dei fornitori di liquidità non è stato filtrato, perché pagava in proporzione a capitale e tempo.

La proposta della DAO del 24 maggio 2023 dice che quelle esclusioni hanno lasciato alla DAO quasi 3,5 milioni di HOP, e mette in distribuzione il 25% di quanto risparmiato: **869.566,51 HOP** a 35 segnalatori. [RFC](https://forum.hop.exchange/t/rfc-hop-airdrop-sybil-hunter-distribution/899).

Lo studio di Luo, Kang, Zheng e Liu (McGill, arXiv, inviato il 18 marzo 2025) misura 150 gruppi chiusi nelle issue di quel repository: **3.551 indirizzi unici**. Non è il CSV intero. Sul loro campione: in **83 gruppi su 150** un solo finanziatore iniziale copre più dell’80% degli indirizzi; in **61 su 150** un solo finanziatore tocca tutti gli altri. Il ricevente comune, cioè l’indirizzo verso cui i fondi tornano, copre più dell’80% in 46 gruppi su 150 e il 100% in 31 su 150. [arXiv:2503.14316](https://arxiv.org/abs/2503.14316).

Lo stesso studio legge anche 198 gruppi segnalati su LayerZero, **7.681 indirizzi**, dopo avere escluso le liste iniziali. In 161 gruppi su 198 più di metà degli indirizzi sta in trasferimenti sequenziali di importo quasi uguale. La media, su quel campione, è 129 transazioni per indirizzo. La repository LayerZero da cui hanno preso i gruppi oggi non si apre. I profitti in dollari del paper sono un modello su un prezzo del token scelto dagli autori, per indirizzi che di fatto sono stati esclusi e non hanno incassato. Non li riporto.

Arbitrum ha riusato quella lista di Hop e non ha pubblicato la propria. Il repository ufficiale contiene il metodo e quattro esempi (gruppi da 110, 56, 121 e 65 indirizzi idonei). Non contiene un file di indirizzi: il 7 ottobre 2026 ci sono solo il README e una cartella di immagini. [Repository](https://github.com/ArbitrumFoundation/sybil-detection).

La regola, nella documentazione della DAO: i gruppi molto connessi nel grafo delle transazioni vengono **collassati in un solo destinatario**, non azzerati uno per uno. Gli indirizzi già segnati nella taglia di Hop sono invece **squalificati**. Si toglie un punto se tutte le transazioni stanno in 48 ore. Si toglie un punto se il saldo è sotto 0,005 ETH e il portafoglio ha toccato non più di un contratto. Sotto 3 punti non si è idonei. Lo snapshot è il 6 febbraio 2023, blocco 58.642.080 su Arbitrum One. La stessa documentazione dice che non hanno usato una prova di persona, perché l’uso pseudonimo è una proprietà del sistema. [Conti sybil](https://docs.arbitrum.foundation/concepts/sybil-account), [idoneità](https://docs.arbitrum.foundation/airdrop-eligibility-distribution).

## Cosa non si può avere

Il numero di identità per operatore, fuori dagli esempi sopra, non è pubblicato. LayerZero dice «decine, centinaia o migliaia» come definizione, non come censimento. ZKsync pubblica la soglia (sopra 20) e un esempio (1.029). Non pubblica quanti gruppi da 20 o meno siano passati, né la finestra e lo scarto di importo del finanziatore comune.

Una lista di indirizzi esclusi scaricabile oggi, fra quelle cercate, è quella di Hop. Quella preliminare di LayerZero no. ZKsync pubblica chi ha ricevuto. Arbitrum pubblica il metodo. La documentazione attuale di Linea sulla Proof of Humanity, aggiornata al 27 settembre 2026, è un controllo per indirizzo: l’API `poh-api.linea.build` risponde vero o falso, con attestazione Sumsub scritta nel registro Verax. Non è un elenco di esclusi. [Verify users with Proof of Humanity](https://docs.linea.build/network/how-to/verify-users-with-proof-of-humanity).

Scroll, nell’annuncio del primo airdrop, non pubblica una lista sybil. Il contratto di termini, aggiornato al 22 ottobre 2024, esclude le persone vietate, le persone statunitensi, e gli IP che la geolocalizzazione colloca in giurisdizioni sanzionate o dove la distribuzione è vietata, compresi proxy. [Annuncio](https://scroll.io/blog/introducing-scrolls-first-airdrop-a-celebration-of-the-global-community), [termini](https://scroll.io/files/airdrop/terms-and-conditions.pdf).

COSA USEREI DOMANI: la regola già scritta da chi ha pagato — stesso finanziatore o stesso deposito su exchange, e sopra 20 indirizzi collegati si viene tolti — e il file di Hop come unico elenco ancora apribile.
COSA NON VALE LA PENA: cercare il nome di chi lo fa, o usare le 14.195 di Hop e le 803.093 di LayerZero come mappa di chi opera oggi su Base. La prima è un airdrop del 2022. La seconda è un conteggio preliminare del 18 maggio 2024 il cui file, il 7 ottobre 2026, non si apre.
