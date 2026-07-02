#!/bin/bash
# Run GETM-FABM-WET model with OpenMP multi-threading and log output.
# Usage: bash scripts/run_model.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"
CASE_DIR="${PROJECT_ROOT}/case"
INSTALL_DIR="${PROJECT_ROOT}/install"
LOG_FILE="${CASE_DIR}/run.log"
EXE="${INSTALL_DIR}/bin/getm_cartesian"

# OpenMP configuration
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-8}
export OMP_SCHEDULE=dynamic

echo "==========================================" | tee "${LOG_FILE}"
echo "  GETM-FABM-WET Model Run" | tee -a "${LOG_FILE}"
echo "==========================================" | tee -a "${LOG_FILE}"
echo "" | tee -a "${LOG_FILE}"
echo "Start time:    $(date)" | tee -a "${LOG_FILE}"
echo "Case dir:      ${CASE_DIR}" | tee -a "${LOG_FILE}"
echo "Executable:    ${EXE}" | tee -a "${LOG_FILE}"
echo "OMP_NUM_THREADS: ${OMP_NUM_THREADS}" | tee -a "${LOG_FILE}"
echo "OMP_SCHEDULE:  ${OMP_SCHEDULE}" | tee -a "${LOG_FILE}"
echo "" | tee -a "${LOG_FILE}"

cd "${CASE_DIR}"
"${EXE}" 2>&1 | tee -a "${LOG_FILE}"
exit_code=${PIPESTATUS[0]}

echo "" | tee -a "${LOG_FILE}"
echo "End time:      $(date)" | tee -a "${LOG_FILE}"
echo "Exit code:     ${exit_code}" | tee -a "${LOG_FILE}"

exit ${exit_code}
