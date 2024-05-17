from base58 import b58encode

BPF_LOADER_PUBKEY = "BPFLoader1111111111111111111111111111111111"
BPF_LOADER_2_PUBKEY = "BPFLoader2111111111111111111111111111111111"
BPF_LOADER_3_PUBKEY = "BPFLoaderUpgradeab1e11111111111111111111111"

ELF_MAGIC = b"\x7fELF"

# BPF Loader and BPF Loader 2 Program Accounts.
# Program accounts for these loaders also contain ELFs.
BPF_LOADER_FILTER = {
    "memcmp": {"offset": 0, "bytes": b58encode(ELF_MAGIC).decode("utf-8")}
}
# BPF Loader 3 Program Accounts.
BPF_LOADER_3_PROGRAM_FILTER = {
    # Enum for `Program`
    "memcmp": {
        "offset": 0,
        "bytes": b58encode(b"\x02\x00\x00\x00").decode("utf-8"),
    },
}
# BPF Loader 3 Program Data Accounts.
BPF_LOADER_3_PROGRAMDATA_FILTER = {
    # Enum for `ProgramData`
    "memcmp": {
        "offset": 0,
        "bytes": b58encode(b"\x03\x00\x00\x00").decode("utf-8"),
    },
    # ELF
    "memcmp": {"offset": 45, "bytes": b58encode(ELF_MAGIC).decode("utf-8")},
}