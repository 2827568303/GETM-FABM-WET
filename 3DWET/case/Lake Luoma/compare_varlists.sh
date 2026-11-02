#!/bin/bash
# Extract variable list from both logs and compare
TL="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake/run.log"
LL="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma/run.log"

# Find the line number of "Processing output category"
TL_START=$(grep -n "Processing output category" "$TL" | head -1 | cut -d: -f1)
LL_START=$(grep -n "Processing output category" "$LL" | head -1 | cut -d: -f1)

echo "Theoretical Lake: Processing output starts at line $TL_START"
echo "Lake Luoma: Processing output starts at line $LL_START"

# Extract variable lists (lines starting with "   -")
echo ""
echo "=== Variable count ==="
echo "Theoretical Lake: $(sed -n "${TL_START},\$p" "$TL" | grep '^   - ' | wc -l)"
echo "Lake Luoma: $(sed -n "${LL_START},\$p" "$LL" | grep '^   - ' | wc -l)"

# Compare the lists
echo ""
echo "=== Diff (Theoretical Lake vs Lake Luoma) ==="
diff <(sed -n "${TL_START},\$p" "$TL" | grep '^   - ' | sort) <(sed -n "${LL_START},\$p" "$LL" | grep '^   - ' | sort)
