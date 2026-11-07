// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Test.sol";

interface IER { function balanceOf(address) external view returns (uint256);
                function approve(address,uint256) external returns (bool); }
interface IP2 { function approve(address,address,uint160,uint48) external; }

/// Le due codifiche del pagamento in Uniswap v4, provate ESEGUENDO.
/// La scorciatoia "paga tutto fino a un massimo" funzionava su due pozze e
/// su una terza ha dato MustNotLeaveDust(). Qui si confronta col "paga
/// esattamente il dovuto", sulla pozza che ha fallito.
contract DueCodifiche is Test {
    address constant WEETH = 0xCd5fE23C85820F7B72D0926FC9b05b43E359b7ee;
    address constant P2    = 0x000000000022D473030F116dDEE9F6B43aC78BA3;
    address constant UR    = 0x66a9893cC07D91D95644AEDD05D03f95e1dBA8Af;

    function _prova(string memory quale, bytes memory cd) internal {
        address me = address(this);
        deal(WEETH, me, 1 ether);
        IER(WEETH).approve(P2, type(uint256).max);
        IP2(P2).approve(WEETH, UR, type(uint160).max, uint48(block.timestamp + 3600));
        uint256 eth0 = me.balance;
        uint256 w0 = IER(WEETH).balanceOf(me);
        (bool ok, bytes memory ris) = UR.call(cd);
        console2.log(quale);
        if (!ok) { console2.log("  NON RIUSCITA:"); console2.logBytes(ris); }
        else {
            console2.log("  riuscita. weETH speso:", w0 - IER(WEETH).balanceOf(me));
            console2.log("  ether ricevuto:", me.balance - eth0);
        }
    }

    function test_due_codifiche() public {
        _prova("A) paga-tutto con MASSIMO",
               vm.parseBytes(vm.readFile("dati/cd_A.txt")));
        _prova("B) paga ESATTO (delta aperto)",
               vm.parseBytes(vm.readFile("dati/cd_B.txt")));
    }
    receive() external payable {}
}
