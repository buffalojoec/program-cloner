import os
import sys
import time

from cloner.filters import BPF_LOADER_3_PROGRAM_FILTER, BPF_LOADER_3_PUBKEY

from .rpc import SolanaRPC
from .util import get_programdata_address, le_to_u64, profile_full_path, \
    init_profile, write_to_profile_csv

def profile_slots(profile_name, url, rate_limit_buffer):
    rpc = SolanaRPC(url)
    version = rpc.get_version()
    now = time.localtime()

    print("Profiling all Solana Loader V3 program slots...")
    print(f"    RPC URL         : {url}")
    print(f"    Solana Version  : {version}")
    print(f"    Profile Name    : {profile_name}")
    print(f"    Date            : {time.strftime('%Y-%m-%d', now)}")

    init_profile(profile_name)

    # Write both the date and the Solana version to "version.txt".
    version_file = profile_full_path(profile_name) / "version.txt"
    with open(version_file, "w") as version_file:
        version_file.write(f"Date: {time.strftime('%Y-%m-%d', now)}\n")
        version_file.write(f"Solana Version: {version}\n")
    
    # BPF Loader 3 Program Accounts.
    print("Downloading BPF Loader 3 program accounts...")
    time.sleep(rate_limit_buffer)
    bpf_loader_3_keys = list(rpc.get_program_account_keys(
        BPF_LOADER_3_PUBKEY,
        [BPF_LOADER_3_PROGRAM_FILTER],
    ));
    print(f"Found {len(bpf_loader_3_keys)} BPF Loader 3 program keys")
    write_to_profile_csv(
        profile_name,
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
    write_to_profile_csv(
        profile_name,
        "bpf_loader_3_with_data_keys.csv",
        [[str(k), str(dk)] for (k, dk) in bpf_loader_3_keys_with_data_keys],
    )

    # BPF Loader 3 Slots.
    print("Profiling BPF Loader 3 slots...")
    time.sleep(rate_limit_buffer)
    bpf_loader_3_slots = list(rpc.get_multiple_programs(
        bpf_loader_3_data_keys,
        rate_limit_buffer,
        offset=4,
        length=8,
    ))
    if len(bpf_loader_3_slots) != len(bpf_loader_3_data_keys):
        print(
            f"Expected {len(bpf_loader_3_data_keys)} BPF Loader 3 slots, but "
            f"found {len(bpf_loader_3_slots)}",
            sys.stderr,
        )
    print(f"Found {len(bpf_loader_3_slots)} BPF Loader 3 slots")
    bpf_loader_3_keys_with_slots = [
        (k, slot)
        for k, slot in zip(
            bpf_loader_3_keys,
            [le_to_u64(s) for (_, s) in bpf_loader_3_slots],
        )
    ]
    write_to_profile_csv(
        profile_name,
        "bpf_loader_3_slots.csv",
        [[str(k), s] for (k, s) in bpf_loader_3_keys_with_slots],
    )