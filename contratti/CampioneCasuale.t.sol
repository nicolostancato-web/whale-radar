// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Test.sol";

/// La prova che aveva ucciso il piano usava le CINQUE PIU' GROSSE: cioe' le
/// piu' contese per costruzione. Campione scelto dal soggetto, ed ero io il
/// soggetto. Qui si rifa' su otto occasioni prese A CASO fra quelle sopra
/// 100 EUR, che e' la popolazione per cui competeremmo davvero.
contract CampioneCasuale is Test {
    address constant POOL = 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2;
    uint256 conFinestra; uint256 totale;

    function _salute(address u) internal view returns (uint256 hf) {
        (bool ok, bytes memory r) = POOL.staticcall(
            abi.encodeWithSignature("getUserAccountData(address)", u));
        if (!ok) return type(uint256).max;
        (, , , , , hf) = abi.decode(r,(uint256,uint256,uint256,uint256,uint256,uint256));
    }

    function _controlla(uint256 blocco, address u, string memory eti) internal {
        vm.createSelectFork(vm.envString("RPC_ARCHIVIO"), blocco - 1);
        uint256 h1 = _salute(u);
        totale++;
        if (h1 < 1e18) {
            conFinestra++;
            vm.createSelectFork(vm.envString("RPC_ARCHIVIO"), blocco - 25);
            uint256 h25 = _salute(u);
            console2.log(eti, "FINESTRA; a 25 blocchi prima la salute era:", h25);
        } else {
            console2.log(eti, "stesso blocco (salute prima:", h1);
        }
    }

    function test_casuale() public {
        _controlla(26149038, 0x27f76e4A31d3AA3525145cD61806C89B78393Cef, "14.479 EUR");
        _controlla(26263356, 0x12915074b7057C4ab73Ea30A2464B2B39912B01b, " 4.374 EUR");
        _controlla(26149038, 0x1FbcadCc4c250cF1f6da6b360263A6EBC3967aA9, " 3.299 EUR");
        _controlla(26077167, 0xb10040870A0c3EbBf8724CFd3725C8CCaA96b77C, " 1.413 EUR");
        _controlla(26149038, 0xCDF0599802a9e203dE7293C045E9AF3620F46Fb0, "   412 EUR");
        _controlla(26263314, 0xC2F590E3e340aE550324A256f3C3489aD7e65541, "   308 EUR");
        _controlla(26263314, 0xf2B07a31316EE4ECa5c14C5f237a9903B4806236, "   139 EUR");
        _controlla(26194904, 0x92d95A4cB77857E82e9e6887F0b545F5A430eC38, "   138 EUR");
        console2.log("---");
        console2.log("con finestra:", conFinestra, "su", totale);
    }
}
