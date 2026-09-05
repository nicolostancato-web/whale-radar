# 🔒 TEAM · SECURITY
*2026-09-05 09:02 UTC · il repo e' PUBBLICO: chiunque legge tutto*

## 🟢 **PULITO** — nessuna credenziale esposta nel repo pubblico

**Controlli passati:**

- nessun token GitHub / Anthropic / OpenAI / Supabase / Google in chiaro nei file
- nessun JWT nei file versionati
- i workflow prendono le credenziali dai secret di GitHub, non dal codice
- nessun workflow usa `pull_request_target` (che esporrebbe i secret a PR esterni)

> Il team corre veloce e committa ogni 30 minuti: questo ruolo esiste perche' un segreto
> scritto per sbaglio, in un repo pubblico, e' bruciato nel momento stesso in cui viene pushato.