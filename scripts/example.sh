#!/usr/bin/env bash
#
# Example shell script for cloud-automation-lab.
# Can be used as a standalone script or called from a workflow step.
#

set -euo pipefail

echo "========================================"
echo "  cloud-automation-lab - Example Script"
echo "========================================"

echo ""
echo "Environment (safe variables only):"
echo "  User: ${USER:-unknown}"
echo "  Shell: ${SHELL:-unknown}"
echo "  PWD: $(pwd)"
echo ""

echo "System:"
echo "  OS: $(uname -srm)"
echo "  Hostname: $(hostname 2>/dev/null || echo 'unknown')"
echo "  Date: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

echo "Disk space:"
df -h / | tail -1
echo ""

echo "Script completed successfully."