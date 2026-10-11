"""IL CUSTODE DELLA MEMORIA — ogni salvataggio passa da qui.

NATO IL 10/10 PER ORDINE DI NICOLO':
«Mi fai un database manager. Ogni volta che mi salvi dei dati deve sempre passare da sto
revisore di memoria. Deve essere un CEO della memoria. Lui ha due database, GitHub e poi
l'altro da 100. GitHub ha solo 10 GB, l'altro 100. E soprattutto la memoria deve essere fatta
in un certo modo: noi stiamo salvando delle transazioni, non dei video. Arrivare a 100 GB con
wallet e transazioni e' veramente difficile, vuol dire che stiamo facendo degli errori.»

Aveva ragione, ed ecco la prova misurata il giorno in cui l'ha detto:

    file                      peso     record   byte/record
    curva_lanci.json.gz      52 MB          1    52.213.102   <- malato
    coppie.json            16,6 MB          4     4.141.866   <- malato
    serie_pool.jsonl       15,6 MB      1.216        12.820   <- grasso
    diplomate_vere.jsonl    5,7 MB     69.966            81   <- SANO

Settantamila transazioni stanno in 5,7 MB. Il problema non e' la quantita' di informazione:
e' il FORMATO. Un oggetto unico da 52 MB va riscritto INTERO per aggiungere un dato, e ogni
riscrittura entra per intero nella storia di git, per sempre. Cosi' 9 GB su 10 si riempiono
con dati che, scritti bene, starebbero in qualche centinaio di megabyte.

LE REGOLE, scritte in positivo (cosa fare, non cosa evitare):

  1. Un dato che CRESCE si scrive a RIGHE, una per record (.jsonl), e si aggiunge in coda.
     Cosi' il salvataggio costa i byte nuovi, non l'intero archivio.
  2. Un record porta i suoi campi, non le serie: una serie di prezzi sta in un file suo,
     riferita da una chiave. Sopra ~4 KB per record, l'informazione va separata.
  3. Gli archivi si comprimono una volta FERMI (mai .gz in aggiunta: un'interruzione lo
     rende illeggibile per intero — lezione del 28/09).
  4. Il posto giusto dipende dalla taglia: fino a 5 MB su GitHub, che e' versionato e si
     legge dal codice; sopra, nel deposito R2, che ha 100 GB e non tiene la storia.
  5. Il margine si guarda PRIMA di scrivere, non dopo il blocco.

COME SI USA (e' un cancello, come il CFO):
    import custode_memoria as C
    ok, motivo = C.controlla("data/x.json")     # prima di salvare o pubblicare
    C.dove_va("data/x.jsonl")                   # "github" o "deposito"
    python3 agents/custode_memoria.py           # il referto su tutta la memoria
"""
import json
import os
import re
import sys
import time

GITHUB_LIMITE_GB = 10.0
DEPOSITO_LIMITE_GB = 100.0

SOGLIA_OGGETTO_UNICO = 2_000_000     # oltre questo, un oggetto unico va spezzato in righe
SOGLIA_SU_GITHUB = 5_000_000         # oltre questo, il posto e' il deposito
SOGLIA_BYTE_PER_RECORD = 4_000       # oltre questo, il record porta dentro una serie


def _record(percorso):
    """Quanti record contiene, e quanto costa ciascuno. None se non so leggerlo."""
    try:
        if percorso.endswith(".jsonl"):
            with open(percorso, errors="replace") as f:
                return sum(1 for r in f if r.strip())
        if percorso.endswith(".json"):
            d = json.load(open(percorso, errors="replace"))
            if isinstance(d, list):
                return len(d)
            if isinstance(d, dict):
                # I RECORD VERI STANNO DENTRO (10/10). Contare le chiavi di primo livello faceva
                # dire che prova_in_avanti.json costa 99 KB per record: ha 11 chiavi, ma una di
                # quelle contiene 323 posizioni. Un custode che grida al lupo sul file della demo
                # si impara a ignorare, ed e' allora che smette di servire.
                dentro = [len(v) for v in d.values() if isinstance(v, (list, dict))]
                return max(dentro) if dentro and max(dentro) > len(d) else len(d)
            return 1
    except Exception:
        return None
    return None


def riscritture(percorso, giorni=7):
    """Quante volte e' stato riscritto negli ultimi giorni.

    PERCHE' SERVE (10/10). Il primo referto metteva in cima `curva_lanci.json.gz`: 52 MB in un
    oggetto unico, formalmente il peggiore. Ma se quel file e' FERMO non costa piu' niente — la
    sua storia e' gia' stata pagata. Il costo vero e' peso x riscritture: `coppie.json` da 9 MB
    riscritto 49 volte in un giorno costa 441 MB, nove volte piu' di un file da 52 MB che non si
    muove. Un custode che ordina per forma invece che per costo manda a riscrivere la cosa
    sbagliata — ed e' la stessa famiglia dell'errore «ordinare per rapporto seleziona gli
    artefatti»: la classifica decide cosa si guarda, quindi la classifica deve misurare il danno.
    """
    import json as _j
    import urllib.request
    tok = os.environ.get("WR_PAT") or os.environ.get("GITHUB_TOKEN")
    if not tok:
        c = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")
        if os.path.exists(c):
            m = re.search(r"ghp_[A-Za-z0-9]+", open(c, encoding="utf-8", errors="ignore").read())
            tok = m.group(0) if m else None
    if not tok:
        return None
    da = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - giorni * 86400))
    u = ("https://api.github.com/repos/nicolostancato-web/whale-radar/commits"
         f"?path={percorso}&since={da}&per_page=100")
    try:
        r = urllib.request.Request(u, headers={"Authorization": f"token {tok}"})
        c = _j.load(urllib.request.urlopen(r, timeout=60))
        # i commit di FUSIONE rielencano il file senza cambiarlo, e git un contenuto identico
        # lo conserva una volta sola: contarli gonfiava la stima di quattro volte (10/10)
        return sum(1 for x in c if len(x.get("parents", [])) < 2)
    except Exception:
        return None


def controlla(percorso):
    """IL CANCELLO. (True, nota) se il salvataggio e' sano, (False, motivo) se va cambiato."""
    if not os.path.exists(percorso):
        return True, "non esiste ancora: niente da controllare"
    peso = os.path.getsize(percorso)
    if peso < 200_000:
        return True, f"{peso/1000:.0f} KB: piccolo, va bene"

    n = _record(percorso)

    # REGOLA 3 — la compressione in aggiunta non si fa
    if percorso.endswith(".gz") and peso > SOGLIA_OGGETTO_UNICO:
        return False, (f"{peso/1e6:.1f} MB compressi in un pezzo solo. Si comprime quando "
                       f"l'archivio e' FERMO; finche' cresce va a righe in .jsonl, "
                       f"altrimenti ogni aggiunta riscrive {peso/1e6:.0f} MB nella storia.")

    # REGOLA 1 — un dato che cresce si scrive a righe
    if percorso.endswith(".json") and peso > SOGLIA_OGGETTO_UNICO:
        q = f"{n} chiavi" if n else "un oggetto"
        return False, (f"{peso/1e6:.1f} MB in {q}: per aggiungere un dato si riscrive tutto, e "
                       f"ogni riscrittura entra INTERA nella storia. Va spezzato in {percorso[:-5]}"
                       f".jsonl, una riga per record, aggiunta in coda.")

    # REGOLA 2 — il record non porta dentro le serie
    if n and peso / n > SOGLIA_BYTE_PER_RECORD:
        return False, (f"{peso/n:,.0f} byte per record su {n:,} record. Un record porta i suoi "
                       f"campi, non le serie: sposta la serie in un file suo e tieni la chiave. "
                       f"Per confronto, diplomate_vere.jsonl costa 81 byte per record.")

    nota = f"{peso/1e6:.1f} MB"
    if n:
        nota += f", {n:,} record, {peso/n:,.0f} byte l'uno"
    return True, nota + ": sano"


def dove_va(percorso):
    """REGOLA 4. GitHub e' versionato e si legge dal codice, ma ha 10 GB e tiene la storia.
    Il deposito ha 100 GB e non la tiene: e' il posto degli archivi."""
    if not os.path.exists(percorso):
        return "github"
    return "deposito" if os.path.getsize(percorso) > SOGLIA_SU_GITHUB else "github"


def margini():
    """REGOLA 5. Quanto spazio resta nei due depositi. Si guarda PRIMA di scrivere."""
    fuori = {}
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import quanto_pesa
        gb = quanto_pesa.peso_ora(quanto_pesa.chiave())
        fuori["github"] = (gb, GITHUB_LIMITE_GB)
    except Exception as e:
        fuori["github"] = (None, GITHUB_LIMITE_GB)
    try:
        import deposito
        el = deposito.elenco()
        fuori["deposito"] = (sum(s for _, s, _ in el) / 1e9, DEPOSITO_LIMITE_GB)
    except Exception:
        fuori["deposito"] = (None, DEPOSITO_LIMITE_GB)
    return fuori


def referto(radice="data"):
    """Il giro di tutta la memoria: chi e' sano, chi va riscritto, e quanto costa."""
    malati, sani, pesomal = [], 0, 0
    for r, _, ff in os.walk(radice):
        for x in ff:
            p = os.path.join(r, x)
            try:
                if os.path.getsize(p) < 200_000:
                    continue
            except OSError:
                continue
            ok, motivo = controlla(p)
            if ok:
                sani += 1
            else:
                peso = os.path.getsize(p)
                n = riscritture(p)
                costo = peso * n / 7 if n else 0.0     # MB al giorno aggiunti alla storia
                malati.append((costo, peso, n, p, motivo))
                pesomal += peso
    malati.sort(reverse=True)
    print("CUSTODE | i due depositi:")
    for nome, (usato, lim) in margini().items():
        if usato is None:
            print(f"   {nome:9} non leggibile da qui")
        else:
            print(f"   {nome:9} {usato:6.2f} GB su {lim:5.0f} — margine {lim-usato:6.2f} GB "
                  f"({100*usato/lim:.0f}% pieno)")
    print(f"\nCUSTODE | {sani} file sani, {len(malati)} da riscrivere "
          f"({pesomal/1e6:.0f} MB fatti nel modo sbagliato)")
    print("   (in ordine di COSTO: peso x riscritture, non di peso)")
    for costo, peso, nn, p, m in malati[:12]:
        q = f"{nn} riscritture/7gg" if nn is not None else "riscritture sconosciute"
        c = f"{costo/1e6:.0f} MB/giorno" if costo else "fermo: non costa piu' niente"
        print(f"\n   {peso/1e6:7.1f} MB  {p}")
        print(f"            {q} -> {c}")
        print(f"            {m}")
    return len(malati)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ok, motivo = controlla(sys.argv[1])
        print(("SANO | " if ok else "DA RISCRIVERE | ") + motivo)
        sys.exit(0 if ok else 1)
    sys.exit(0 if referto() == 0 else 0)
