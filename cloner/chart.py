import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cloner.util import profile_full_path

def chart_profiled_slots(profile_name):
    print("Creating chart of Loader V3 program slots...")
    print(f"    Profile Name    : {profile_name}")

    csv_path = profile_full_path(profile_name) / "bpf_loader_3_slots.csv"
    output_path = profile_full_path(profile_name) / "bpf_loader_3_slots.png"

    df = pd.read_csv(csv_path, header=None, names=['Program ID', 'Deployment Slot'])

    num_bins = 10
    min_slot = df['Deployment Slot'].min()
    max_slot = df['Deployment Slot'].max()
    bin_edges = np.linspace(min_slot, max_slot, num_bins + 1)
    bin_edges = np.round(bin_edges, -3)
    bins = pd.cut(df['Deployment Slot'], bins=bin_edges)

    binned_counts = bins.value_counts().sort_index()

    plt.figure(figsize=(14, 8))
    binned_counts.plot(kind='bar', color='purple')
    plt.xlabel('Deployment Slot Ranges')
    plt.ylabel('Count of Programs')
    plt.title('Loader V3 Program Deployment Slot Distribution')
    plt.xticks(rotation=45, ha='right')

    bin_labels = [f'{int(interval.left)} - {int(interval.right)}' for interval in binned_counts.index]
    plt.gca().set_xticklabels(bin_labels)
    plt.tight_layout()

    plt.savefig(output_path)