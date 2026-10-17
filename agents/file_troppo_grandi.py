"""Nessun file deve avvicinarsi al limite di GitHub: uno solo blocca TUTTO il repository.

IL GUASTO DEL 29/09. `data/loop1/segnali.jsonl` e' arrivato a 104,8 MB contro i 100 di limite
per file. Non ha rallentato niente: ha reso IMPOSSIBILE ogni spinta sul repository, da parte di
qualunque corsia. Per ore ho letto i registri e ho visto «contesa sul ramo», che era il sintomo;
la causa era un file solo, cresciuto piano, che nessuno guardava.

Compresso: 5,6 MB, 175.845 righe intatte. Il problema era il formato, non l'informazione.

Questa guardia protesta **prima** del limite, non dopo: a 60 MB si avvisa, a 90 si blocca.
Un guasto che si vede solo quando e' gia' successo non e' una guardia.
"""
import os
import sys

AVVISO = 60 * 1024 * 1024
BLOCCO = 90 * 1024 * 1024
SALTA = {".git"}


def principale(radice="."):
    grossi, fermi = [], []
    for base, cartelle, nomi in os.walk(radice):
        cartelle[:] = [c for c in cartelle if c not in SALTA]
        for nome in nomi:
            p = os.path.join(base, nome)
            try:
                d = os.path.getsize(p)
            except OSError:
                continue
            if d >= BLOCCO:
                fermi.append((p, d))
            elif d >= AVVISO:
                grossi.append((p, d))
    for p, d in sorted(grossi, key=lambda x: -x[1]):
        print(f"   {p}: {d/1e6:.1f} MB — si avvicina al limite, comprimilo prima che blocchi tutto",
              flush=True)
    for p, d in sorted(fermi, key=lambda x: -x[1]):
        print(f"   {p}: {d/1e6:.1f} MB — OLTRE SOGLIA: un file cosi' blocca OGNI spinta di TUTTE "
              f"le corsie. Comprimilo (.gz) invece di cancellarlo.", flush=True)
    if fermi:
        sys.exit(1)
    if not grossi:
        print("   nessun file vicino al limite di GitHub", flush=True)


if __name__ == "__main__":
    principale(sys.argv[1] if len(sys.argv) > 1 else ".")
