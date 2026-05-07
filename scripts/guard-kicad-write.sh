#!/usr/bin/env bash
# Pre-write safety check for KiCad project files.
# Run BEFORE any agent-driven edit to .kicad_sch / .kicad_pcb / .kicad_sym.
#
# Exits 0 if safe to write, non-zero with a message otherwise.
#
# Usage:
#   scripts/guard-kicad-write.sh           # check only
#   scripts/guard-kicad-write.sh --strict  # also fail if kicad-mcp-pro is running
#
# See .agents/kicad-workflow.md for the full workflow.

set -euo pipefail

strict=0
[[ "${1:-}" == "--strict" ]] && strict=1

fail() {
    echo "GUARD FAIL: $1" >&2
    echo "  See .agents/kicad-workflow.md for the rationale." >&2
    exit 1
}

# 1. KiCad GUI must be closed. It silently auto-saves and reverts agent edits.
if pgrep -i kicad >/dev/null; then
    pids=$(pgrep -i kicad | tr '\n' ' ')
    fail "KiCad GUI is running (pids: ${pids}). Close it before editing project files."
fi

# 2. kicad-mcp-pro caches schematic in memory. If it's running and we direct-edit,
#    its next write call clobbers our changes. In strict mode, refuse.
#    In default mode, warn — the agent should be in Mode A (read-only MCP) anyway.
if pgrep -fl kicad-mcp-pro >/dev/null 2>&1; then
    if [[ $strict -eq 1 ]]; then
        fail "kicad-mcp-pro is running. Stop it first or stay in read-only MCP mode (Mode A)."
    else
        echo "GUARD WARN: kicad-mcp-pro is running. Do NOT call any MCP write tools this session." >&2
        echo "  (See .agents/kicad-workflow.md — pick one mode per session.)" >&2
    fi
fi

echo "guard ok: safe to direct-edit KiCad files"
