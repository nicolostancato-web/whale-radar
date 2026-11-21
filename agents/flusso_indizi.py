"""Esiste un canale GRATUITO alla coda delle transazioni?

La prova su copia locale ha mostrato che la finestra e' di 12 secondi e che
chi vince agisce nello stesso blocco dell'aggiornamento di prezzo. Per farlo
bisogna vedere quell'aggiornamento PRIMA che sia nel blocco.

Ipotesi da verificare: Flashbots pubblica gratis un flusso di INDIZI sulle
transazioni private (MEV-Share), apposta perche' qualcuno ci si attacchi
dietro. Se e' raggiungibile, la strada esiste; se no, e' chiusa.
"""
import json, time, urllib.request, sys
FONTI=[("MEV-Share Flashbots","https://mev-share.flashbots.net"),
       ("MEV-Share (eventi)","https://mev-share.flashbots.net/api/v1/events")]
for nome,u in FONTI:
    print(f"\n   {nome}: {u}")
    try:
        r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0",
                                             "accept":"text/event-stream"})
        with urllib.request.urlopen(r, timeout=25) as f:
            print(f"      connesso, tipo: {f.headers.get('content-type')}")
            t0=time.time(); righe=0; esempi=[]
            while time.time()-t0 < 18:
                l=f.readline()
                if not l: break
                s=l.decode("utf-8","ignore").strip()
                if not s: continue
                righe+=1
                if s.startswith("data:") and len(esempi)<3:
                    esempi.append(s[5:].strip()[:220])
            print(f"      {righe} righe in 18 secondi")
            for e in esempi: print(f"      esempio: {e}")
    except Exception as e:
        print(f"      non raggiungibile: {str(e)[:70]}")
