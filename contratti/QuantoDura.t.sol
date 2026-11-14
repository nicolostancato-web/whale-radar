// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

/// Quanto e' durata la finestra? Due delle cinque liquidazioni erano gia'
/// possibili al blocco prima. Se la posizione era liquidabile da dieci
/// minuti e nessuno l'aveva presa, quella e' un'occasione raggiungibile
/// anche da chi legge sei posizioni al secondo.
contract QuantoDura is Test {
    address constant POOL = 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2;

    function _salute(address u) internal view returns (uint256 hf) {
        (bool ok, bytes memory r) = POOL.staticcall(
            abi.encodeWithSignature("getUserAccountData(address)", u));
        if (!ok) return type(uint256).max;
        (, , , , , hf) = abi.decode(r,
            (uint256,uint256,uint256,uint256,uint256,uint256));
    }

    /// cerca all'indietro il primo blocco in cui la salute era gia' sotto 1
    function _quantoPrima(uint256 blocco, address u, string memory eti) internal {
        console2.log(eti);
        uint256[6] memory passi = [uint256(1), 5, 25, 100, 400, 1600];
        uint256 ultimoSotto = 0;
        for (uint256 i = 0; i < passi.length; i++) {
            uint256 b = blocco - passi[i];
            vm.createSelectFork(vm.envString("RPC_ARCHIVIO"), b);
            uint256 hf = _salute(u);
            console2.log("   blocchi prima:", passi[i], " salute:", hf);
            if (hf < 1e18) ultimoSotto = passi[i];
            else break;   // risalita sopra 1: la finestra comincia qui
        }
        console2.log("   -> era gia' liquidabile da almeno", ultimoSotto, "blocchi");
        console2.log("   -> cioe' circa", ultimoSotto * 12 / 60, "minuti");
    }

    function test_leDueConFinestra() public {
        _quantoPrima(26194930, 0xd6128ea5A807C4Ae8Ac710ab4fb2179C6b394cd4, "C) premio 186 EUR");
        _quantoPrima(26194900, 0xAAeFC37b2E620269c3af5Dc34B77C5d2D8622a23, "E) premio 90 EUR");
    }
}
