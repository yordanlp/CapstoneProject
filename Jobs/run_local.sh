#!/usr/bin/env bash
# Runs redis, the model services and the worker natively (see setup_local.sh).
# DEVICE can be auto (default), cuda, mps or cpu.
set -euo pipefail
cd "$(dirname "$0")"
JOBS_DIR=$(pwd)

export DEVICE=${DEVICE:-auto}
export SHARED_FOLDER="$JOBS_DIR/Shared"
# Run ops that aren't implemented on mps on the cpu instead of failing
export PYTORCH_ENABLE_MPS_FALLBACK=1

export REDIS_ROUTE=localhost ALIS_ROUTE=localhost STYLEGAN2_ROUTE=localhost SUPERRESOLUTION_ROUTE=localhost

mkdir -p .logs
pids=()
cleanup() { kill "${pids[@]}" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

if command -v redis-server >/dev/null; then
    redis-server --port 6379 > .logs/redis.log 2>&1 &
    pids+=($!)
else
    docker run --rm --name pixellift-redis -p 6379:6379 redis > .logs/redis.log 2>&1 &
    pids+=($!)
    trap 'cleanup; docker stop pixellift-redis >/dev/null 2>&1 || true' EXIT INT TERM
fi

for svc in Stylegan2 Superresolution; do  # Alis disabled: checkpoint no longer available
    (cd "$svc" && exec .venv/bin/python api.py) > ".logs/$svc.log" 2>&1 &
    pids+=($!)
done

# Give redis and the APIs a moment before the worker subscribes
sleep 3
(cd Worker && exec .venv/bin/python worker.py) > .logs/Worker.log 2>&1 &
pids+=($!)

echo "Services running with DEVICE=$DEVICE. Logs in $JOBS_DIR/.logs (Ctrl+C to stop)."
wait
