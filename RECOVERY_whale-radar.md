# RECOVERY — crypto / mercati

Aggiornato: **29 ottobre 2026, notte**.

## Stato: IN ATTESA DI UNA DECISIONE DI NICOLÒ

Il candidato «liquidazioni» è stato misurato fino in fondo. Tutto quello che
si poteva sapere si sa. **Serve la sua scelta fra tre opzioni**, in
`IL_PUNTO_DI_DECISIONE_29OTT.md`:

1. costruirlo comunque (settimane, bassa probabilità, zero soldi a rischio)
2. fermarsi e prendere la misura come risposta
3. **cercare altrove** portandosi dietro quello che si è imparato ← io propendo

**Cassa: €52,16.** Mai toccata. Costo totale della ricerca: **zero euro**.

## Il verdetto in una riga

L'occasione è reale (€5.219/giorno nel mondo, €2.958 non presidiati), non
serve capitale e i tentativi sbagliati non costano nulla — ma **la finestra
per agire è di 12 secondi** e la vince chi ha infrastruttura dedicata.

## Come si è arrivati lì (tutto verificato, un numero per riga)

- cancello di capitale: **nessuno**, prestito istantaneo 0,05% letto dal contratto
- asta per il premio: **nessuna**, €98.150 presi con €0,20 di gas
- congestione nei giorni che pagano: **assente**, 0,4 gwei
- parti collegate: **escluse**, 16 su 16 contratti professionali
- garanzia «scomoda»: **si vende**, 0,01-0,23% su €200.000
- nicchia scoperta: wstETH, sUSDe, WBTC = 86% del valore libero
- **la prova che ha ucciso tutto**: riproduzione su copia locale, salute
  1,0043 al blocco prima → occasione nata e presa nello STESSO blocco

## Cosa resta costruito e funzionante

- `contratti/Liquidatore.sol` — compila senza avvisi, si annulla se il
  guadagno è sotto soglia, non tiene mai fondi
- `liquidatore/` — progetto Foundry con le tre prove su copia locale
  (forge/anvil in `~/.foundry/bin`, RPC d'archivio: `https://eth.drpc.org`)
- `data/liquidazioni/` — 60 giorni di storia completa, prezzi d'oracolo,
  creatori dei liquidatori, 1.801 debitori raccolti
- canale gratuito verificato: MEV-Share (indizi) + Flashbots (pacchetti
  annullati gratis)

## Se si riprende

Leggere `IL_PUNTO_DI_DECISIONE_29OTT.md`, poi
`LA_FINESTRA_E_DI_12_SECONDI_28OTT.md`. Non ricominciare le misure: sono
finite. La domanda aperta è solo quale delle tre strade prendere.

## Risorse

- Repo: `nicolostancato-web/whale-radar` | cartella `wr4`, `.venv_bot2/bin/python`
- Pubblicare: `.venv_bot2/bin/python agents/pubblica_file.py "motivo" file...`
- Fonti gratuite: Blockscout (archivio, **max 5 finestre per giro**),
  publicnode (recente), drpc.org (archivio per i fork)
- Se lo scratchpad si svuota: `curl https://raw.githubusercontent.com/nicolostancato-web/whale-radar/main/agents/<file>`
