#!/usr/bin/env bash
# Build, check, and deploy the site in one command.
#
#   tools/deploy.sh              # build -> check_build -> deploy --prune
#   tools/deploy.sh --dry-run    # same, but deploy only lists what would change
#
# Extra arguments are passed to deploy.py. FTP credentials come from .env at
# the repo root and are exported only into this process; nothing is printed.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
    echo "error: no .env at $(pwd) (needs FTP_HOST, FTP_USER, FTP_PASS)" >&2
    exit 1
fi

PY=.venv/bin/python

"$PY" build.py
"$PY" tools/check_build.py

set -a
. ./.env
set +a

exec "$PY" tools/deploy.py --prune "$@"
