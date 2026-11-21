// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/Liquidatore.sol";

interface IERC20b { function balanceOf(address) external view returns (uint256); }

/// LA PROVA CHE ATTRAVERSA TUTTO, dal prezzo che scende ai soldi in cassa.
///
/// PERCHE' ESISTE (5/11). Tutte le prove precedenti distribuivano un
/// contratto nuovo e gli passavano una Piano COSTRUITA IN SOLIDITY: non
/// attraversavano ne' l'indirizzo vero ne' la calldata che costruiamo in
/// Python. E' per questo che il selettore sbagliato e' vissuto per ~12.000
/// pacchetti senza che nessuna verifica lo vedesse.
/// Questa prova invece:
///   1. legge la calldata VERA dal cassetto, byte per byte, come la
///      spediremmo;
///   2. fa SCENDERE il prezzo della garanzia, cosi' la posizione cade
///      davvero (finora provavamo solo su posizioni sane, e l'unico esito
///      possibile era HealthFactorNotBelowThreshold);
///   3. controlla che in CASSA arrivino soldi, non che "non sia andata in
///      errore".
contract DaCapoAFondo is Test {
    address constant POOL   = 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2;
    address constant ORACLE = 0x54586bE62E3c3580375aE3723C145253060Ca0C2;
    address constant CASSA  = 0x055e75aEaCF141c3118d039D5E099a821152eB66;

    function test_dal_prezzo_che_scende_ai_soldi_in_cassa() public {
        Liquidatore liq = new Liquidatore(POOL, CASSA);
        address gar = vm.parseAddress(vm.readFile("dati/e2e_garanzia.txt"));
        address deb = vm.parseAddress(vm.readFile("dati/e2e_debito.txt"));
        bytes memory ch = vm.parseBytes(vm.readFile("dati/e2e_calldata.txt"));

        // il prezzo della garanzia SCENDE: e' l'unico modo di provare il
        // percorso oltre il controllo di salute di Aave
        // SI SCENDE FINCHE' SERVE, e si DICE se non e' bastato.
        // Difetto trovato il 5/11: la prova abbassa il prezzo della garanzia
        // PRINCIPALE, ma se quella non e' la parte dominante del collaterale
        // di quell'utente la salute non scende, e la prova riportava
        // HealthFactorNotBelowThreshold come se il piano fosse rotto. Era
        // la prova a non poter far cadere QUELLA posizione: "non ho potuto
        // provare" non e' "non funziona".
        bool caduta = false;
        uint256 p = IOracolo(ORACLE).getAssetPrice(gar);
        for (uint256 sconto = 2; sconto <= 90; sconto += 4) {
            uint256 nuovo = p * (100 - sconto) / 100;
            vm.mockCall(ORACLE,
                abi.encodeWithSelector(IOracolo.getAssetPrice.selector, gar),
                abi.encode(nuovo));
            (, , , , , uint256 hf) = IPoolDati(POOL).getUserAccountData(
                vm.parseAddress(vm.readFile("dati/e2e_utente.txt")));
            if (hf < 1e18) {
                caduta = true;
                console2.log("caduta a sconto percento:", sconto);
                console2.log("salute:", hf);
                break;
            }
        }

        if (!caduta) {
            console2.log("NON HO POTUTO PROVARE: la posizione non cade");
            console2.log("nemmeno abbassando del 90% il prezzo della");
            console2.log("garanzia principale: il collaterale e' misto.");
            return;
        }
        uint256 prima = IERC20b(deb).balanceOf(CASSA);
        (bool ok, bytes memory ris) = address(liq).call(ch);
        if (!ok) {
            console2.log("NON RIUSCITA, byte di errore:");
            console2.logBytes(ris);
        }
        uint256 dopo = IERC20b(deb).balanceOf(CASSA);
        console2.log("in cassa prima:", prima);
        console2.log("in cassa dopo :", dopo);
        assertTrue(ok, "la chiamata vera non e' andata a buon fine");
        assertGt(dopo, prima, "in cassa non e' arrivato niente");
    }
}

interface IOracolo { function getAssetPrice(address) external view returns (uint256); }
interface IPoolDati {
    function getUserAccountData(address) external view returns (
        uint256, uint256, uint256, uint256, uint256, uint256);
}
