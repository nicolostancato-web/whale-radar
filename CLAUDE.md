# CLAUDE.md — istruzioni per l'agente (whale-radar)

## CONTESTO
Ricerca-dati sui grandi acquisti chain Robinhood (EVM) per capire se c'è edge PRIMA di rischiare soldi.
Founder solo, budget piccolo, tutto gratis (GitHub pubblico + Actions + API free). Precedente fallimento
per DISORGANIZZAZIONE → **ORDINE = priorità #1**.

## REGOLE ASSOLUTE
1. NO over-engineering (KISS). NO astronavi.
2. NO script sparsi: solo in `agents/` (reparti schedulati), `lib/` (condiviso), `analysis/` (on-demand).
3. Dati SEMPRE compressi + immutabili. 1 solo scrittore per cartella. RAW è sacro.
4. Ogni decisione → `DECISIONS.md`. Ogni esperimento → `EXPERIMENTS.md`. Ogni task → `TASKS.md`.
5. Zero soldi reali finché il paper live non conferma l'edge.
6. Costo AI con tetto €1/giorno, loggato in `costs_log.txt`.
7. Decisioni di struttura/organizzazione → parti da un deep-search (CometAPI economico).

## COME LAVORARE
1. Leggi ARCHITECTURE.md + DECISIONS.md prima di iniziare.
2. Codice nella cartella giusta, nome `verbo_sostantivo.py`.
3. Aggiorna i doc. Commit atomico. Push.

## STRUTTURA → vedi ARCHITECTURE.md (il master blueprint).
