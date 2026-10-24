# Il repo è a 3,09 GB e cresce di ~700 MB al giorno

*19 settembre 2026 · trovato preparando i numeri per l'allargamento della raccolta*

## I numeri

| | |
|---|---|
| dati veri (i file che ci servono) | **301 MB** |
| repo su GitHub | **3.090 MB** |
| cartella `.git` in locale | 3,4 GB |
| commit il 16/09 | 3.800 |
| commit il 17/09 | 3.722 |
| commit il 18/09 | 1.786 |

**Dieci volte il peso dei dati è cronologia.**

Limiti dichiarati da GitHub: consigliato sotto 1 GB, avviso sopra 5 GB, oltre 10 GB si può essere
bloccati. Siamo a 3,09 e cresciamo di circa 700 MB al giorno nei giorni pieni.

**Proiezione: avviso in ~3 giorni, blocco in ~10.**

## Perché cresce così

I dati sono file `.gz`. Un file compresso cambiato anche di una riga è, per git, un blob
completamente nuovo: non esiste delta fra due gzip. Ogni corsia che scrive e committa produce
quindi un blob intero per ogni file toccato, e le corsie girano in continuazione.

Non è un difetto di una corsia: è il costo di tenere dati binari che cambiano ogni ora dentro una
cronologia che non dimentica.

## Perché blocca la decisione sull'allargamento

`COPERTURA_VERA.md` dice che teniamo il 4% della popolazione definita e che per arrivare al 95%
servirebbe un fattore venti sui pool. **Con questa curva, il fattore venti non è discutibile: il
repo morirebbe prima.** La decisione sull'allargamento non è più «quanto vogliamo raccogliere» ma
«dove mettiamo i dati».

## Le tre strade, coi loro costi veri

**1. Ramo separato per i dati, riscritto periodicamente.**
   I dati vivono su un ramo `dati` che non conserva storia: ogni settimana si riparte da uno stato
   solo. Il codice resta su `main` con la sua storia intatta.
   *Costo:* si perde la possibilità di rileggere lo stato di un giorno passato dai dati versionati.
   *Guadagno:* il repo torna intorno ai 300-400 MB e ci resta.

**2. Squash periodico della storia di `main`.**
   Una volta a settimana si riscrive la storia collassando i commit di dati.
   *Costo:* riscrittura distruttiva, tutti i cloni vanno rifatti; se sbagliata si perdono dati.
   *Guadagno:* stesso del punto 1, ma più rischioso.

**3. I dati escono da git.**
   Release di GitHub, o un bucket esterno.
   *Costo:* le corsie vanno riscritte, e un bucket esterno costa (fuori dalla regola CFO a €0).

## Cosa NON ho fatto

Non ho riscritto niente. Riscrivere la storia di un repo è irreversibile e non è una cosa che
prendo da solo mentre dodici corsie ci scrivono dentro.

## Cosa si può fare subito, a rischio zero

Ridurre la frequenza dei commit di dati (accumulare e committare una volta l'ora invece che a ogni
giro) rallenta la crescita ma **non la ferma**: è una pezza che compra giorni, non una soluzione.
