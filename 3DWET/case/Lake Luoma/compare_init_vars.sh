#!/bin/bash
# Compare only initialization-phase variable lists
TL="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake/run.log"
LL="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma/run.log"

# Extract from "Processing output category" to "finalize_register_all_variables" (or EOF)
TL_START=$(grep -n "Processing output category" "$TL" | head -1 | cut -d: -f1)
TL_END=$(grep -n "finalize_register_all_variables" "$TL" | head -1 | cut -d: -f1)

LL_START=$(grep -n "Processing output category" "$LL" | head -1 | cut -d: -f1)
LL_END=$(wc -l < "$LL")

echo "Theoretical Lake: lines $TL_START to $TL_END"
echo "Lake Luoma: lines $LL_START to $LL_END"

echo ""
echo "=== Variable count (init phase only) ==="
echo "Theoretical Lake: $(sed -n "${TL_START},${TL_END}p" "$TL" | grep '^   - ' | wc -l)"
echo "Lake Luoma: $(sed -n "${LL_START},${LL_END}p" "$LL" | grep '^   - ' | wc -l)"

echo ""
echo "=== Diff (init phase only) ==="
diff <(sed -n "${TL_START},${TL_END}p" "$TL" | grep '^   - ' | sort) <(sed -n "${LL_START},${LL_END}p" "$LL" | grep '^   - ' | sort)
