from base58 import b58encode
import os
import sys
import time

from .rpc import SolanaRPC
from .util import bundle_full_path, \
    get_programdata_address, init_bundle, write_to_bundle_csv

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

def clone(bundle_name, url, rate_limit_buffer):
    rpc = SolanaRPC(url)
    version = rpc.get_version()

    print("Downloading all Solana programs...")
    print(f"    RPC URL         : {url}")
    print(f"    Solana Version  : {version}")
    print(f"    Bundle Name     : {bundle_name}")

    init_bundle(bundle_name)

    # BPF Loader Program Accounts.
    print("Downloading BPF Loader program accounts...")
    time.sleep(rate_limit_buffer)
    bpf_loader_keys = list(rpc.get_program_account_keys(
        BPF_LOADER_PUBKEY,
        [BPF_LOADER_FILTER],
    ));
    print(f"Found {len(bpf_loader_keys)} BPF Loader program keys")
    write_to_bundle_csv(
        bundle_name,
        "bpf_loader.csv",
        [[str(k)] for k in bpf_loader_keys],
    )
    
    # BPF Loader 2 Program Accounts.
    print("Downloading BPF Loader 2 program accounts...")
    time.sleep(rate_limit_buffer)
    bpf_loader_2_keys = list(rpc.get_program_account_keys(
        BPF_LOADER_2_PUBKEY,
        [BPF_LOADER_FILTER],
    ));
    print(f"Found {len(bpf_loader_2_keys)} BPF Loader 2 program keys")
    write_to_bundle_csv(
        bundle_name,
        "bpf_loader_2.csv",
        [[str(k)] for k in bpf_loader_2_keys],
    )
    
    # BPF Loader 3 Program Accounts.
    print("Downloading BPF Loader 3 program accounts...")
    time.sleep(rate_limit_buffer)
    bpf_loader_3_keys = list(rpc.get_program_account_keys(
        BPF_LOADER_3_PUBKEY,
        [BPF_LOADER_3_PROGRAM_FILTER],
    ));
    print(f"Found {len(bpf_loader_3_keys)} BPF Loader 3 program keys")
    write_to_bundle_csv(
        bundle_name,
        "bpf_loader_3.csv",
        [[str(k)] for k in bpf_loader_3_keys],
    )

    # BPF Loader 3 Program Accounts with Program Data Accounts.
    bpf_loader_3_keys_with_data_keys = [
        (k, get_programdata_address(str(k)))
        for k in bpf_loader_3_keys
    ]
    bpf_loader_3_data_keys = [
        dk for (k, dk) in bpf_loader_3_keys_with_data_keys
    ]
    write_to_bundle_csv(
        bundle_name,
        "bpf_loader_3_with_data_keys.csv",
        [[str(k), str(dk)] for (k, dk) in bpf_loader_3_keys_with_data_keys],
    )
    
    # BPF Loader ELFs.
    print("Downloading BPF Loader ELFs...")
    time.sleep(rate_limit_buffer)
    bpf_loader_elfs = list(rpc.get_multiple_programs(
        bpf_loader_keys,
        rate_limit_buffer,
    ))
    print(f"Found {len(bpf_loader_elfs)} BPF Loader ELFs")
    for (program_id, elf) in bpf_loader_elfs:
        dir = bundle_full_path(bundle_name) / "bpf_loader"
        dir.mkdir(parents=True, exist_ok=True)
        file_name = dir / f"{program_id}.elf"
        with open(file_name, "wb") as program_file:
            program_file.write(elf)

    # BPF Loader 2 ELFs.
    print("Downloading BPF Loader 2 ELFs...")
    time.sleep(rate_limit_buffer)
    bpf_loader_2_elfs = list(rpc.get_multiple_programs(
        bpf_loader_2_keys,
        rate_limit_buffer,
    ))
    print(f"Found {len(bpf_loader_2_elfs)} BPF Loader 2 ELFs")
    for (program_id, elf) in bpf_loader_2_elfs:
        dir = bundle_full_path(bundle_name) / "bpf_loader_2"
        dir.mkdir(parents=True, exist_ok=True)
        file_name = os.path.join(dir, f"{program_id}.elf")
        with open(file_name, "wb") as program_file:
            program_file.write(elf)

    # BPF Loader 3 ELFs.
    print("Downloading BPF Loader 3 ELFs...")
    time.sleep(rate_limit_buffer)
    bpf_loader_3_elfs = list(rpc.get_multiple_programs(
        bpf_loader_3_data_keys,
        rate_limit_buffer,
        offset=45,
    ))
    if len(bpf_loader_3_elfs) != len(bpf_loader_3_data_keys):
        print(
            f"Expected {len(bpf_loader_3_data_keys)} BPF Loader 3 ELFs, but "
            f"found {len(bpf_loader_3_elfs)}",
            sys.stderr,
        )
    print(f"Found {len(bpf_loader_3_elfs)} BPF Loader 3 ELFs")
    for i, (_, elf) in enumerate(bpf_loader_3_elfs):
        program_id = bpf_loader_3_keys[i]
        dir = bundle_full_path(bundle_name) / "bpf_loader_3"
        dir.mkdir(parents=True, exist_ok=True)
        file_name = os.path.join(dir, f"{program_id}.elf")
        with open(file_name, "wb") as program_file:
            program_file.write(elf)