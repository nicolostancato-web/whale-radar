# RECOVERY — whale-radar (snapshot 2026-08-22)

## Cosa stiamo facendo (1 frase)
Macchina auto-apprendente multi-chain che indovina quali memecoin pumperanno, per guadagnarci, senza rischiare
soldi finche' l'edge non e' provato robusto. €0 (repo PUBBLICO = Actions gratis, MAI privato). PC spento.

## NUMERO-VERITA' OGGI
Robinhood MEDIA STRATEGIA **+26% per token** · AFFIDABILE (+8% senza i 3 mostri top) · 152 token · walk-forward, costi reali.
Cresce e si rafforza coi dati (era +23%/+4%). Il numero VERO e' in EDGE.md. A "news?" leggo EDGE.md + MULTICHAIN.md.

## COME COMUNICARE I NUMERI (regole di Nicolo)
- Sempre "MEDIA STRATEGIA: +X% per token" (assoluto), MAI "+X% in piu' dell'edge".
- +X% = per SINGOLO token, sulla sua VITA (giorni-settimane), NON al giorno. €2 -> €2,X.
- Mostrare AFFIDABILITA (media senza i 3 mostri top): se resta positiva = solida, non 2 colpi fortunati.
- Numero affidabile = resta stabile/cresce col crescere dei token.

## I DUE MOTORI (auto-learn)
1. SELEZIONE (quali token): learner.py, auto-impara ogni giorno (AUC ~0.73). AUTOMATICO.
2. STRATEGIA (entrata/uscita): strategy_optimizer.py, prova strategie ogni 12h e APPLICA la piu' robusta da sola
   (solo se robusta migliora >2pt, MAI peggiora). Scrive data/strategy.json che edge_eval legge. AUTOMATICO.
   Guardrail: sceglie per robustezza (senza top3) = anti curve-fitting. Rischio overfitting -> si guarda il forward.

## MULTICHAIN (4 chain: solana/bsc/base/robinhood)
Collector candele+trade via GeckoTerminal (matrix 4 chain, ORARIO per tenere basso il gross - vedi sotto).
Dati ormai pieni. Numeri veri: robinhood +26% (feature RICCHE/RPC), base ~0%, solana -3% (MA 15 mostri!), bsc -31%.
LEZIONE: le nuove chain sono negative NON perche' scarse ma perche' le FEATURE multichain (GeckoTerminal) sono
DEBOLI vs quelle RPC di Robinhood. Solana ha 15 mostri non catturati = potenziale. PROSSIMA MANOVELLA:
feature ricche per le nuove chain (storia trade profonda + first-buyers veri) -> poi possono avvicinare Robinhood.

## COSTI (CFO) — falso allarme risolto 21/08
Paghiamo €0. Il "€10/giorno" era il GROSS dei minuti Actions, scontato al 100% perche' repo PUBBLICO (net $0.00).
Regola: repo SEMPRE pubblico. Guardare solo il NET sul dashboard, mai il gross. Tetto €100/mese, siamo a €0.
Matrici multichain messe ORARIE per tenere basso il gross (peace of mind).

## MINDSET (Nicolo)
Mai proporre di mollare (decide LUI). Push in LOOP come bestie fino al goal. Onesto sui numeri, implacabile
sull'obiettivo. Solana/BNB: SEMPRE costi reali (slippage/gas/fee) + entrata/uscita realistiche (+Xh, non "momento
perfetto"). Ricorda l'errore Solana: simulazione troppo precisa = illusione.

## Come riprendere
Leggi questo + TRADER.md. A "news?": EDGE.md (Robinhood, numero vero) + MULTICHAIN.md (per chain) + STRATEGY_LOG.md.
