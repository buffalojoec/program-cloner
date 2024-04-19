import sys
import time

from .rpc import SolanaRPC
from .util import bundle_full_path, write_to_bundle_csv

def sort(bundle_name, url, rate_limit_buffer):
    if not bundle_full_path(bundle_name).exists:
        print(f"Bundle '{bundle_name}' does not exist.", sys.stderr)

    rpc = SolanaRPC(url)

    print("Sorting programs by last execution slot...")
    print(f"    RPC URL         : {url}")
    print(f"    Bundle Name     : {bundle_name}")

    program_keys = []
    program_keys_with_slot = []

    # BPF Loader Programs.
    file_name = bundle_full_path(bundle_name) / "bpf_loader.csv"
    if not file_name.exists:
        print(f"File '{file_name}' does not exist.", sys.stderr)
    with open(file_name, 'r') as file:
        for line in file:
            program_keys.append((line.strip(), 1))
    
    # BPF Loader 2 Programs.
    file_name = bundle_full_path(bundle_name) / "bpf_loader_2.csv"
    if not file_name.exists:
        print(f"File '{file_name}' does not exist.", sys.stderr)
    with open(file_name, 'r') as file:
        for line in file:
            program_keys.append((line.strip(), 2))

    # BPF Loader 3 Programs.
    file_name = bundle_full_path(bundle_name) / "bpf_loader_3.csv"
    if not file_name.exists:
        print(f"File '{file_name}' does not exist.", sys.stderr)
    with open(file_name, 'r') as file:
        for line in file:
            program_keys.append((line.strip(), 3))
    
    # Using `GetSignaturesForAddress`, get the last execution slot for each
    # program.
    total_programs_to_sort = len(program_keys)
    current_program = 0
    chunk = 0
    for program in program_keys:
        slot = rpc.get_last_slot_for_address(program[0])
        program_keys_with_slot.append((slot, program[0], program[1]))
        if chunk % 10 == 0:
            print(f"    Sorted {current_program}/{total_programs_to_sort} programs")
        chunk += 1
        current_program += 1
        time.sleep(rate_limit_buffer)

    # Sort by slot.
    program_keys_with_slot.sort(key=lambda x: x[0], reverse=True)

    # Write sorted programs to a new file.
    file_name = bundle_full_path(bundle_name) / "sorted_programs.csv"
    with open(file_name, 'w') as file:
        write_to_bundle_csv(
            bundle_name,
            "sorted_programs.csv",
            program_keys_with_slot,
        )