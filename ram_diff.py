import sys
import struct
from collections import defaultdict

# ---- CONFIG ----
BASE_ADDR = 0x80000000  # MEM1 base
CLUSTER_WINDOW = 0x40   # group changes within this many bytes

# DOL ranges you already confirmed
TEXT_RANGES = [
    (0x80003100, 0x800055FF),
    (0x800056C0, 0x803027BF),
]

DATA_RANGES = [
    (0x80005600, 0x800056BF),
    (0x803027C0, 0x80346B5F),
    (0x80346B60, 0x80408EC1),
]

def classify(addr):
    for s, e in TEXT_RANGES:
        if s <= addr <= e:
            return "DOL_TEXT"
    for s, e in DATA_RANGES:
        if s <= addr <= e:
            return "DOL_DATA"
    return "HEAP/OTHER"

def cluster_changes(addrs):
    addrs = sorted(addrs)
    clusters = []
    current = [addrs[0]]

    for a in addrs[1:]:
        if a - current[-1] <= CLUSTER_WINDOW:
            current.append(a)
        else:
            clusters.append(current)
            current = [a]

    clusters.append(current)
    return clusters

def main(f1, f2):
    with open(f1, "rb") as a, open(f2, "rb") as b:
        mem1 = a.read()
        mem2 = b.read()

    if len(mem1) != len(mem2):
        print("Dump sizes differ.")
        return

    changes = []
    for i in range(len(mem1)):
        if mem1[i] != mem2[i]:
            addr = BASE_ADDR + i
            changes.append(addr)

    if not changes:
        print("No differences.")
        return

    clusters = cluster_changes(changes)

    print(f"\nTotal changed bytes: {len(changes)}")
    print(f"Clusters found: {len(clusters)}\n")

    for c in clusters:
        start = c[0]
        end = c[-1]
        region = classify(start)
        print(f"{region}  0x{start:08X} - 0x{end:08X}  ({len(c)} bytes)")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ram_diff.py before.bin after.bin")
    else:
        main(sys.argv[1], sys.argv[2])