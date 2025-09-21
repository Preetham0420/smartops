$ErrorActionPreference = "Stop"

$base       = "C:\Users\preet\Projects\nani\smartops"
$work       = Join-Path $base "sandbox\work"
$dockerfile = Join-Path $base "sandbox\Dockerfile"

# 1) Prepare a fresh workdir (copies demo + applies suggested edit)
py -3 (Join-Path $base "scripts\prep_sandbox.py")

# 2) Build the base image
docker build -t smartops-sandbox -f $dockerfile $work

# 3) Run with /app mounted; force pytest to ignore repo configs (-c /dev/null)
docker run --rm `
  --mount type=bind,source="$work",target=/app `
  smartops-sandbox bash -lc "
    set -euo pipefail
    echo '--- Python ---'
    python -V
    echo '--- Install ---'
    if [ -f requirements.txt ]; then python -m pip install -r requirements.txt; else echo 'requirements.txt not found'; fi
    echo '--- Tests ---'
    if command -v pytest >/dev/null 2>&1; then pytest -q -c /dev/null || true; else echo 'pytest not found'; fi
"
