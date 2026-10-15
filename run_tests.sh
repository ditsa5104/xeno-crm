#!/usr/bin/env bash
# Runs the suite inside the crm container (README.md's documented
# `docker compose exec crm pytest`) and saves the full console output as a
# timestamped markdown report, alongside the DEBUG trace pytest.ini writes
# to crm/test-results/pytest.log.
set -uo pipefail

cd "$(dirname "$0")"

RESULTS_DIR="crm/test-results"
TIMESTAMP="$(date +"%Y-%m-%d_%H-%M-%S")"
REPORT_FILE="$RESULTS_DIR/test-run-$TIMESTAMP.md"

mkdir -p "$RESULTS_DIR"

STATUS_FILE="$(mktemp)"
trap 'rm -f "$STATUS_FILE"' EXIT

{
  echo "# Test run - $TIMESTAMP"
  echo
  echo '```'
  docker compose exec -T crm pytest "$@" 2>&1
  echo "$?" > "$STATUS_FILE"
  echo '```'
} | tee "$REPORT_FILE"

PYTEST_EXIT="$(cat "$STATUS_FILE")"
echo "Report written to $REPORT_FILE"
exit "$PYTEST_EXIT"
