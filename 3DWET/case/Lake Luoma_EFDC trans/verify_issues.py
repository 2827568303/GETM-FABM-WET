"""Quick verification of two key conversion issues."""
import os
import numpy as np

EFDC_DIR = r"D:\00_数据\00_骆马湖-模型\LMH_Balanced_test_WL0 = 21.82"

print("=" * 70)
print("  VERIFICATION 1: cell.inp character set")
print("=" * 70)
cell_path = os.path.join(EFDC_DIR, 'cell.inp')
char_count = {}
total_water = 0
total_cells = 0
sample_lines = []
with open(cell_path, 'r', encoding='latin-1') as f:
    for ln in f:
        ln = ln.rstrip('\n')
        if not ln.strip():
            continue
        parts = ln.split(None, 1)
        if len(parts) < 2:
            continue
        try:
            j = int(parts[0])
        except ValueError:
            continue
        if j < 1 or j > 46:
            continue
        row_str = parts[1]
        if len(row_str) < 52:
            continue
        if len(sample_lines) < 3:
            sample_lines.append(f'  j={j}: |{row_str[:52]}|')
        for ch in row_str[:52]:
            char_count[ch] = char_count.get(ch, 0) + 1
            total_cells += 1
            if ch in ('5', '9'):
                total_water += 1

print(f"  total cells parsed: {total_cells}")
print(f"  water cells (5 or 9): {total_water}")
print(f"  character frequency:")
for ch, cnt in sorted(char_count.items()):
    pct = 100 * cnt / total_cells
    print(f"    '{ch}' (0x{ord(ch):02x}): {cnt:5d} ({pct:.1f}%)")
print(f"\n  sample lines:")
for s in sample_lines:
    print(s)

# check if there are other water markers besides 5/9
water_chars = set(char_count.keys()) - {'0', ' ', 'C', 'c', 'x', '-', '.'}
print(f"\n  potential water chars (not 0/space/C/x/-/.): {water_chars}")

print("\n" + "=" * 70)
print("  VERIFICATION 2: aser.inp precip/evap data")
print("=" * 70)
aser_path = os.path.join(EFDC_DIR, 'aser.inp')
with open(aser_path, 'r', encoding='latin-1') as f:
    lines = f.readlines()

# find data header
hdr_idx = None
for k, ln in enumerate(lines):
    parts = ln.split()
    if len(parts) >= 4:
        try:
            int(parts[0])
            if '86400' in ln:
                hdr_idx = k
                break
        except ValueError:
            continue

print(f"  header line {hdr_idx}: {lines[hdr_idx].rstrip()}")
hdr = lines[hdr_idx].split()
n_recs = int(hdr[0])
print(f"  n_recs: {n_recs}")

# parse first 5 and last 5 records
print(f"\n  first 5 records (time, slp_mb, t2, rh, precip_m/d, evap_m/d, swr, tcc):")
data_count = 0
for ln in lines[hdr_idx + 1:]:
    parts = ln.split()
    if len(parts) < 8:
        continue
    try:
        t = float(parts[0])
    except ValueError:
        continue
    if data_count < 5 or data_count >= n_recs - 5:
        print(f"    [{data_count:4d}] t={parts[0]:>8s} slp={parts[1]:>8s} t2={parts[2]:>6s} "
              f"rh={parts[3]:>5s} P={parts[4]:>8s} E={parts[5]:>8s} swr={parts[6]:>8s} tcc={parts[7]:>5s}")
    data_count += 1
    if data_count >= n_recs:
        break

# compute precip/evap stats
precip_arr = []
evap_arr = []
data_count = 0
for ln in lines[hdr_idx + 1:]:
    parts = ln.split()
    if len(parts) < 8:
        continue
    try:
        float(parts[0])
    except ValueError:
        continue
    if data_count >= n_recs:
        break
    precip_arr.append(float(parts[4]))
    evap_arr.append(float(parts[5]))
    data_count += 1

precip_arr = np.array(precip_arr)
evap_arr = np.array(evap_arr)
print(f"\n  precip stats: min={precip_arr.min():.4f}, max={precip_arr.max():.4f}, "
      f"mean={precip_arr.mean():.4f} m/d, nonzero={np.sum(precip_arr > 0)}/{len(precip_arr)} days")
print(f"  evap  stats: min={evap_arr.min():.4f}, max={evap_arr.max():.4f}, "
      f"mean={evap_arr.mean():.4f} m/d, nonzero={np.sum(evap_arr > 0)}/{len(evap_arr)} days")
print(f"  annual precip: {precip_arr.sum() * 365 / len(precip_arr):.0f} mm/yr (Luoma ~900 mm/yr)")
print(f"  annual evap:   {evap_arr.sum() * 365 / len(evap_arr):.0f} mm/yr (Luoma ~1000 mm/yr)")
