#!/bin/bash
# Run GETM-FABM-WET model for Theoretical Lake test case.
# Usage: bash scripts/run_model.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"
CASE_DIR="${PROJECT_ROOT}/case"

# Reuse the GETM executable built for the 3DWET case (same source tree).
GETM_ROOT="$( dirname "${PROJECT_ROOT}" )/3DWET"
INSTALL_DIR="${GETM_ROOT}/install"
LOG_FILE="${CASE_DIR}/run.log"
EXE="${INSTALL_DIR}/bin/getm_cartesian"

# OpenMP configuration
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-8}
export OMP_SCHEDULE=dynamic

echo "==========================================" | tee "${LOG_FILE}"
echo "  GETM-FABM-WET Model Run (Theoretical Lake)" | tee -a "${LOG_FILE}"
echo "==========================================" | tee -a "${LOG_FILE}"
echo "" | tee -a "${LOG_FILE}"
echo "Start time:    $(date)" | tee -a "${LOG_FILE}"
echo "Case dir:      ${CASE_DIR}" | tee -a "${LOG_FILE}"
echo "Executable:    ${EXE}" | tee -a "${LOG_FILE}"
echo "OMP_NUM_THREADS: ${OMP_NUM_THREADS}" | tee -a "${LOG_FILE}"
echo "OMP_SCHEDULE:  ${OMP_SCHEDULE}" | tee -a "${LOG_FILE}"
echo "" | tee -a "${LOG_FILE}"

if [ ! -x "${EXE}" ]; then
    echo "ERROR: executable not found: ${EXE}" | tee -a "${LOG_FILE}"
    exit 1
fi

cd "${CASE_DIR}"
"${EXE}" 2>&1 | tee -a "${LOG_FILE}"
exit_code=${PIPESTATUS[0]}

echo "" | tee -a "${LOG_FILE}"
echo "End time:      $(date)" | tee -a "${LOG_FILE}"
echo "Exit code:     ${exit_code}" | tee -a "${LOG_FILE}"

exit ${exit_code}
