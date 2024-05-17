from base64 import b64decode
import csv
import os
from pathlib import Path
from solders.pubkey import Pubkey

from cloner.filters import BPF_LOADER_3_PUBKEY

def get_programdata_address(program_address):
    program_id = Pubkey.from_string(str(program_address))
    loader_id = Pubkey.from_string(BPF_LOADER_3_PUBKEY)
    pda = Pubkey.find_program_address([bytes(program_id)], loader_id)
    return str(pda[0])

def bundle_full_path(bundle_name) -> Path:
    return Path(os.getcwd()) / "bundles" / bundle_name

def init_bundle(bundle_name):
    full_path = bundle_full_path(bundle_name)
    full_path.mkdir(parents=True, exist_ok=True)
    print(f"Initialized bundle '{bundle_name}'.")

def write_to_bundle_csv(bundle_name, filename, data_list):
    full_path = bundle_full_path(bundle_name) / filename
    with open(full_path, 'w', newline='') as file:
        writer = csv.writer(file)
        for data in data_list:
            writer.writerow(data)

def le_to_u64(data) -> int:
    return int.from_bytes(data, byteorder='little')

def profile_full_path(profile_name) -> Path:
    return Path(os.getcwd()) / "profiles" / profile_name

def init_profile(profile_name):
    full_path = profile_full_path(profile_name)
    full_path.mkdir(parents=True, exist_ok=True)
    print(f"Initialized profile '{profile_name}'.")

def write_to_profile_csv(profile_name, filename, data_list):
    full_path = profile_full_path(profile_name) / filename
    with open(full_path, 'w', newline='') as file:
        writer = csv.writer(file)
        for data in data_list:
            writer.writerow(data)