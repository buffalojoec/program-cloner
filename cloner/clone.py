import os
import sys
import time

from cloner.filters import BPF_LOADER_2_PUBKEY, BPF_LOADER_3_PROGRAM_FILTER, \
    BPF_LOADER_3_PUBKEY, BPF_LOADER_FILTER, BPF_LOADER_PUBKEY

from .rpc import SolanaRPC
from .util import bundle_full_path, \
    get_programdata_address, init_bundle, write_to_bundle_csv

def clone(bundle_name, url, rate_limit_buffer):
    rpc = SolanaRPC(url)
    version = rpc.get_version()
    now = time.localtime()

    print("Downloading all Solana programs...")
    print(f"    RPC URL         : {url}")
    print(f"    Solana Version  : {version}")
    print(f"    Bundle Name     : {bundle_name}")
    print(f"    Date            : {time.strftime('%Y-%m-%d', now)}")

    init_bundle(bundle_name)

    # Write both the date and the Solana version to "version.txt".
    version_file = bundle_full_path(bundle_name) / "version.txt"
    with open(version_file, "w") as version_file:
        version_file.write(f"Date: {time.strftime('%Y-%m-%d', now)}\n")
        version_file.write(f"Solana Version: {version}\n")

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
        dk for (_, dk) in bpf_loader_3_keys_with_data_keys
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
    for (data_key, elf) in bpf_loader_3_elfs:
        # Find the program key associated with the data key.
        program_key = None
        for (program_key, data_key_) in bpf_loader_3_keys_with_data_keys:
            if data_key == data_key_:
                break
        if program_key is not None:
            dir = bundle_full_path(bundle_name) / "bpf_loader_3"
            dir.mkdir(parents=True, exist_ok=True)
            file_name = os.path.join(dir, f"{program_id}.elf")
            with open(file_name, "wb") as program_file:
                program_file.write(elf)