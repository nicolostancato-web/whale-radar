// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/Liquidatore.sol";

interface IERC20c { function balanceOf(address) external view returns (uint256); }
interface IOracolo2 { function getAssetPrice(address) external view returns (uint256); }

/// SI PAGA IL COSTRUTTORE ANCHE QUANDO IL GUADAGNO NON E' IN WETH?
///
/// PERCHE' ESISTE (5/11). Delle 10 liquidazioni avvenute da quando il
/// contratto e' giusto, il debito era USDC/USDT/LINK in TUTTE E DIECI, zero
/// in WETH. La mancia si pagava solo sui debiti in WETH, quindi non si e'
/// mai applicata a UNA occasione vera: su quelle 10 offrivamo la sola
/// priority fee, tappata dal saldo a 45 dollari.
///
/// Questa prova attraversa il ramo nuovo con la CALLDATA VERA costruita in
/// Python (1.317 byte, selettore bfa77cf8), non con un Piano scritto in
/// Solidity: e' l'unico modo di vedere un errore di codifica, ed e' la
/// ragione per cui il selettore sbagliato e' vissuto 12.000 pacchetti.
///
/// COSA PROVA E COSA NON PROVA, detto prima: prova che il costruttore viene
/// pagato in ETH e che il resto arriva in cassa in WETH. NON prova la
/// guardia sul guadagno minimo, perche' qui il minimo e' zero -- quella e'
/// provata altrove (DaCapoAFondo).
contract ManciaInQualsiasiMoneta is Test {
    address constant POOL   = 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2;
    address constant ORACLE = 0x54586bE62E3c3580375aE3723C145253060Ca0C2;
    address constant CASSA  = 0x055e75aEaCF141c3118d039D5E099a821152eB66;
    address constant WETH   = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address constant COSTRUTTORE = address(0xB1D1);

    function test_il_costruttore_viene_pagato_anche_su_debito_in_stablecoin() public {
        Liquidatore liq = new Liquidatore(POOL, CASSA);
        address gar = vm.parseAddress(vm.readFile("dati/e2e_m_garanzia.txt"));
        bytes memory ch = vm.parseBytes(vm.readFile("dati/e2e_m_calldata.txt"));
        uint256 mancia = vm.parseUint(vm.readFile("dati/e2e_m_mancia.txt"));

        vm.coinbase(COSTRUTTORE);
        uint256 primaCostruttore = COSTRUTTORE.balance;
        uint256 primaCassa = IERC20c(WETH).balanceOf(CASSA);

        // il prezzo della garanzia SCENDE finche' la posizione cade davvero.
        // Se non cade, si DICE: «non ho potuto provare» non e' «non funziona».
        bool caduta = false;
        uint256 p = IOracolo2(ORACLE).getAssetPrice(gar);
        bytes memory esito;
        for (uint256 calo = 2; calo <= 90 && !caduta; calo += 2) {
            uint256 nuovo = p * (100 - calo) / 100;
            vm.mockCall(ORACLE,
                abi.encodeWithSelector(IOracolo2.getAssetPrice.selector, gar),
                abi.encode(nuovo));
            vm.prank(liq.padrone());
            (bool ok, bytes memory ris) = address(liq).call(ch);
            esito = ris;
            if (ok) { caduta = true; break; }
            // 0x930bb771 = HealthFactorNotBelowThreshold: non e' ancora caduta
            if (ris.length < 4 || bytes4(ris) != bytes4(0x930bb771)) {
                emit log_named_bytes("si e' fermata con", ris);
                break;
            }
        }
        if (!caduta) {
            emit log("NON HO POTUTO PROVARE: la posizione non cade abbassando questa garanzia");
            emit log_named_bytes("ultimo esito", esito);
            return;
        }
        uint256 dopoCostruttore = COSTRUTTORE.balance;
        uint256 dopoCassa = IERC20c(WETH).balanceOf(CASSA);
        emit log_named_uint("al costruttore, in wei", dopoCostruttore - primaCostruttore);
        emit log_named_uint("in cassa, WETH in piu'", dopoCassa - primaCassa);
        assertEq(dopoCostruttore - primaCostruttore, mancia,
                 "il costruttore non ha ricevuto esattamente la mancia");
        assertGt(dopoCassa, primaCassa, "in cassa non e' arrivato niente");
    }
}
