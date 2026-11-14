# Grok (grok-4-1-fast-reasoning) — stato — 2026-11-05

costo $0.0007, 7s, 821 token di risposta

---

1. Spiegazione comoda, non regge.  
Controlla inclusion rate per builder su tutti i pacchetti inviati negli ultimi 7 giorni; misura % di bundle che arrivano a beaverbuild/BuilderNet vs Flashbots e confronta con vincitori reali.

2. Traccia transfer a coinbase nelle tx vincenti note + calcola effective gas price pagato.  
Estrai dalle tx di liquidazione vinte negli ultimi 30 giorni il valore trasferito a block.coinbase e il gas usato; confronta con premio per stimare mancia implicita.

3. Aggiungi pagamento builder dal ricavato nella stessa tx e testa su una liquidazione >$500.  
Non aumentare offerte a Flashbots né distribuire nuovo contratto; misura solo se il bundle ora viene incluso da beaverbuild.

4. Nessuna misurazione di competing bundles dagli altri 35 vincitori ripetuti.  
Aggiungi traccia delle tx concorrenti nello stesso blocco per vedere priority fee e coinbase transfer reali.
