#!/bin/bash
# Installa in Ethereum la versione NUOVA del liquidatore.
# Lanciarlo cosi':   bash DISTRIBUISCI.sh
#
# Cosa fa: una sola transazione, ~1,07 milioni di gas (circa 1,10-1,45 $ al
# gas di stanotte). La chiave si legge dal file credenziali e non viene
# stampata. La cassa resta quella di Nicolo': il contratto nuovo nasce
# puntando allo stesso indirizzo di cassa e allo stesso pool di Aave.
set -e
cd "$(dirname "$0")/liquidatore"
POOL=0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2
CASSA=0x055e75aEaCF141c3118d039D5E099a821152eB66
K=$(grep -oE "Private key wallet 1 0x[a-fA-F0-9]{64}" ~/Documents/b2b-finder-credentials.txt | awk '{print $NF}')
if [ -z "$K" ]; then echo "FERMO: chiave non trovata nel file credenziali"; exit 1; fi
echo "gas base adesso: $(~/.foundry/bin/cast base-fee --rpc-url https://ethereum-rpc.publicnode.com) wei"
~/.foundry/bin/forge create --broadcast \
  --rpc-url https://ethereum-rpc.publicnode.com \
  --private-key "$K" \
  src/Liquidatore.sol:Liquidatore \
  --constructor-args "$POOL" "$CASSA" | grep -viE "private|key"
echo
echo "FATTO. Copia la riga 'Deployed to: 0x...' e incollala a Claude."
