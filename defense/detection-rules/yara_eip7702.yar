rule EIP7702_Sweeper_Bytecode
{
    meta:
        description = "Heuristic match for EIP-7702 sweeper contracts"
        author      = "exchange-breach-sim"
    strings:
        $a = "Sweeper" ascii nocase
    condition:
        uint32(0) == 0x3078 and $a
}
