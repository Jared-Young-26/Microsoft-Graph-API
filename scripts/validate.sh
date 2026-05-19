#!/usr/bin/env bash

set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

RUN_FRONTEND=1
RUN_BACKEND=1

for arg in "$@"; do
  case "$arg" in
    --frontend-only)
      RUN_BACKEND=0
      ;;
    --backend-only)
      RUN_FRONTEND=0
      ;;
    *)
      echo "[validate] Unknown argument: $arg"
      echo "[validate] Supported arguments: --frontend-only | --backend-only"
      exit 2
      ;;
  esac
done

if [ "$RUN_FRONTEND" -eq 0 ] && [ "$RUN_BACKEND" -eq 0 ]; then
  echo "[validate] Nothing to run."
  exit 2
fi

FAIL_COUNT=0
SKIP_COUNT=0

run_step() {
  local label="$1"
  shift
  echo
  echo "[validate] RUN  $label"
  echo "[validate] CMD  $*"
  if "$@"; then
    echo "[validate] PASS $label"
  else
    echo "[validate] FAIL $label"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

run_frontend_suite() {
  echo
  echo "[validate] === Frontend validation ==="
  run_step "boot_contract.test.js" node admin_gui/boot_contract.test.js
  run_step "help_center.test.js" node admin_gui/help_center.test.js
  run_step "investigation_summary.test.js" node admin_gui/investigation_summary.test.js
  run_step "json_inspector.test.js" node admin_gui/json_inspector.test.js
  run_step "next_steps.test.js" node admin_gui/next_steps.test.js
  run_step "persistence_security.test.js" node admin_gui/persistence_security.test.js
  run_step "portal_schema.test.js" node admin_gui/portal_schema.test.js
  run_step "service_shells.test.js" node admin_gui/service_shells.test.js
  run_step "triage.test.js" node admin_gui/triage.test.js
  run_step "node --check app.js" node --check admin_gui/app.js
  run_step "node --check portal_schema.js" node --check admin_gui/portal_schema.js
  run_step "node --check service_shells.js" node --check admin_gui/service_shells.js
  run_step "node --check persistence_security.js" node --check admin_gui/persistence_security.js
}

check_backend_prereqs() {
  if ! command -v python3 >/dev/null 2>&1; then
    echo "[validate] SKIP backend validation: python3 not found."
    echo "[validate] HINT install Python 3 and project deps from requirements.txt."
    SKIP_COUNT=$((SKIP_COUNT + 1))
    return 1
  fi

  local missing_modules
  missing_modules="$(python3 - <<'PY'
import importlib.util

required = ("flask", "fastapi", "starlette")
missing = [name for name in required if importlib.util.find_spec(name) is None]
if missing:
    print(",".join(missing))
PY
)"

  if [ -n "$missing_modules" ]; then
    echo "[validate] SKIP backend validation: missing Python modules: $missing_modules"
    echo "[validate] HINT run: pip install -r requirements.txt"
    SKIP_COUNT=$((SKIP_COUNT + 1))
    return 1
  fi

  return 0
}

run_backend_suite() {
  echo
  echo "[validate] === Backend validation ==="
  if ! check_backend_prereqs; then
    return 0
  fi

  run_step \
    "python3 -m unittest backend hardening subset" \
    python3 -m unittest \
      admin_gui.backend.test_browser_allowlist \
      admin_gui.backend.test_operator_auth \
      admin_gui.backend.test_flask_app_cache_busting \
      admin_gui.backend.test_fastapi_app_cache_busting
}

if [ "$RUN_FRONTEND" -eq 1 ]; then
  run_frontend_suite
fi

if [ "$RUN_BACKEND" -eq 1 ]; then
  run_backend_suite
fi

echo
echo "[validate] === Summary ==="
echo "[validate] failures=$FAIL_COUNT skipped=$SKIP_COUNT"

if [ "$FAIL_COUNT" -gt 0 ]; then
  echo "[validate] RESULT FAIL"
  exit 1
fi

echo "[validate] RESULT PASS"
exit 0
