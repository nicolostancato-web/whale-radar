# Organizzazione: chi scrive cosa, dove e quando

*generato da `agents/mappa_organizzazione.py` leggendo i file di corsia e i sorgenti. Non e' una dichiarazione di intenti: e' quello che il sistema fa davvero oggi.*

**73 corsie, 14 accese.** 2 file sono scritti da piu' di una corsia accesa, 1 corsie accese non hanno un orologio, 2 non consegnano niente.

## Le corsie accese

| corsia | orologio | scrive | consegna |
|---|---|---|---|
| `astra` | 10 6,13,20 * * * | `CONSULENZA_<x>.md`, `data/consulenze/contatore.json`, `data/multichain/<x>/<x>`, `data/rilanci.json` | allegato |
| `deposito` | 37 */6 * * * | `data/rilanci.json` | NIENTE |
| `guardia` | 19 * * * * | — | NIENTE |
| `guardiani` | 32 */3 * * * | `CFO.md`, `SECURITY.md`, `data/cfo_flags.json`, `data/security_flags.json` | spinge |
| `heartbeat` | 48 */2 * * * | `HEARTBEAT.md` | spinge |
| `ispezione` | 28 * * * * | `ISPEZIONE.md`, `data/ispezione.json` | spinge |
| `nascite` | 27 * * * * | `data/<x>_mai_letti.json`, `data/multichain/<x>/<x>`, `data/multichain/<x>/<x>/<x>.jsonl.gz`, `data/multichain/<x>/nascita_vera.json` | allegato |
| `prova_avanti` | 50 5 * * * | `data/loop1/<x>`, `data/loop1/insieme_<x><x>.jsonl.gz`, `data/loop1/insieme_<x>_sc5.jsonl.gz`, `data/loop1/prova_avanti_<x>.json` | allegato |
| `pubblicatore` | */20 * * * * | `data/multichain/<chain>/arbitraggi.json.gz`, `data/multichain/<x>`, `data/multichain/<x>/iniziatori.json.gz`, `data/multichain/<x>/iniziatori_nuovi.json` | spinge |
| `repo_gc` | 0 3 * * * | — | spinge |
| `sentinella` | 45 */6 * * * | `data/allarmi_da_leggere.jsonl`, `data/loop1/sentinella.json` | spinge |
| `soccorso` | 5 * * * * | — | spinge |
| `vivo` | 9 * * * * | `data/multichain/<x>/coda_ckpt.json`, `data/multichain/<x>/universo.jsonl.gz`, `data/multichain/<x>/vivo/<x>.jsonl.gz` | allegato |
| `workflow_watchdog` | **nessuno** | `WATCHDOG.md`, `data/rilanci.json` | spinge |

## Scritti da più di una corsia (qui nascono le sovrascritture)

- `data/multichain/<x>/<x>` ← `astra`, `nascite`
- `data/rilanci.json` ← `astra`, `deposito`, `workflow_watchdog`
