#!/usr/bin/env bash
# Shared acceptance lock for dispatched fox-fix-projex-bug workers and their coordinator.
#
#   accept-lock.sh acquire <lock-dir> <owner> [max-wait-seconds]   (default 2700 = 45 min)
#   accept-lock.sh release <lock-dir> <owner>
#   accept-lock.sh held    <lock-dir> <owner>
#   accept-lock.sh status  <lock-dir>
#
# acquire exits 0 only once the lock is held; on timeout it exits 3 and the caller
# must stop without touching the acceptance workspace. held exits 0 only when
# <owner> holds the lock (5 otherwise); chain it before every command that touches
# the acceptance workspace. release refuses (exit 4) a lock held by another owner.
# The owner file holds the owner on line 1 and the acquisition time on line 2.
set -euo pipefail

usage() { sed -n '2,13p' "$0" >&2; exit 2; }

cmd=${1:-}
lock=${2:-}
[ -n "$cmd" ] && [ -n "$lock" ] || usage

case "$cmd" in
  acquire)
    owner=${3:-}
    [ -n "$owner" ] || usage
    max=${4:-2700}
    interval=30
    waited=0
    until mkdir "$lock" 2>/dev/null; do
      if [ "$waited" -ge "$max" ]; then
        echo "timeout after ${waited}s; lock held by: $(head -n 2 "$lock/owner" 2>/dev/null | tr '\n' ' ')" >&2
        exit 3
      fi
      sleep "$interval"
      waited=$((waited + interval))
    done
    printf '%s\n%s\n' "$owner" "$(date '+%Y-%m-%d %H:%M:%S %z')" >"$lock/owner"
    echo "acquired after ${waited}s"
    ;;
  release)
    owner=${3:-}
    [ -n "$owner" ] || usage
    if [ ! -d "$lock" ]; then
      echo "not held"
      exit 0
    fi
    current=$(head -n 1 "$lock/owner" 2>/dev/null || true)
    if [ "$current" != "$owner" ]; then
      echo "refusing to release: lock held by '$current', not '$owner'" >&2
      exit 4
    fi
    rm -f "$lock/owner"
    rmdir "$lock"
    echo "released"
    ;;
  held)
    owner=${3:-}
    [ -n "$owner" ] || usage
    current=$(head -n 1 "$lock/owner" 2>/dev/null || true)
    if [ "$current" != "$owner" ]; then
      echo "not held by '$owner'; current owner: '${current:-none}'" >&2
      exit 5
    fi
    ;;
  status)
    if [ -d "$lock" ]; then
      echo "held by: $(head -n 2 "$lock/owner" 2>/dev/null | tr '\n' ' ')"
    else
      echo "free"
    fi
    ;;
  *) usage ;;
esac
