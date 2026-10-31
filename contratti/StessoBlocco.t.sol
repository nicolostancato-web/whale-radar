// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

/// La liquidazione avviene nello STESSO blocco in cui la posizione diventa
/// liquidabile? E' la domanda che decide se possiamo vincerne una.
///
/// Si guarda la salute alla FINE del blocco precedente. Se e' ancora sopra
/// 1, vuol dire che il prezzo che ha aperto l'occasione e' arrivato nello
/// stesso blocco della liquidazione: una corsa che con sei letture al
/// secondo non si vince.
contract StessoBlocco is Test {
    address constant POOL = 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2;

    function _salute(address u) internal view returns (uint256 hf) {
        (bool ok, bytes memory r) = POOL.staticcall(
            abi.encodeWithSignature("getUserAccountData(address)", u));
        if (!ok) return type(uint256).max;
        (, , , , , hf) = abi.decode(r,
            (uint256,uint256,uint256,uint256,uint256,uint256));
    }

    function _controlla(uint256 blocco, address utente, string memory eti) internal {
        vm.createSelectFork(vm.envString("RPC_ARCHIVIO"), blocco - 1);
        uint256 hf = _salute(utente);
        console2.log(eti);
        console2.log("   salute alla fine del blocco precedente (1e18):", hf);
        console2.log(hf < 1e18
            ? "   GIA' LIQUIDABILE PRIMA: c'era una finestra"
            : "   non ancora liquidabile: stesso blocco, corsa persa");
    }

    function test_cinqueCasi() public {
        _controlla(26198343, 0x0Ed0eA598e89765471e86A060bd91F4BB2dc1fB0, "A) premio 79.010 EUR");
        _controlla(25922641, 0xb7040FFaDB77219D9BC7d5fC9E9F848C83cC96f7, "B) premio 1.276 EUR");
        _controlla(26194930, 0xd6128ea5A807C4Ae8Ac710ab4fb2179C6b394cd4, "C) premio 186 EUR");
        _controlla(26263314, 0x260865391d9259fB7ceb52Ef41bEcAb9dF5ABda7, "D) premio 148 EUR");
        _controlla(26194900, 0xAAeFC37b2E620269c3af5Dc34B77C5d2D8622a23, "E) premio 90 EUR");
    }
}
