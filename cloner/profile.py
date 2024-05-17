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
        dk for (_, dk) in bpf_loader_3_keys_with_data_keys
    ]
    write_to_profile_csv(
        profile_name,
        "bpf_loader_3_with_data_keys.csv",
        [[str(k), str(dk)] for (k, dk) in bpf_loader_3_keys_with_data_keys],
    )

    print("Profiling BPF Loader 3 slots...")
    time.sleep(rate_limit_buffer)

    # BPF Loader 3 Program Data accounts with slots.
    bpf_loader_3_data_keys_with_slots = list(rpc.get_multiple_programs(
        bpf_loader_3_data_keys,
        rate_limit_buffer,
        offset=4,
        length=8,
    ))
    write_to_profile_csv(
        profile_name,
        "bpf_loader_3_data_keys_with_slots.csv",
        sorted(
            [[str(k), le_to_u64(s)] for (k, s) in bpf_loader_3_data_keys_with_slots],
            key=lambda x: x[1],
        ),
    )

    # BPF Loader 3 Program accounts with slots.
    bpf_loader_3_keys_with_slots = [
        (str(k), le_to_u64(s))
        for (k, kdk) in bpf_loader_3_keys_with_data_keys
        for (ddk, s) in bpf_loader_3_data_keys_with_slots
        if kdk == ddk
    ]
    write_to_profile_csv(
        profile_name,
        "bpf_loader_3_keys_with_slots.csv",
        sorted(
            [[str(k), s] for (k, s) in bpf_loader_3_keys_with_slots],
            key=lambda x: x[1],
        ),
    )