#!/usr/bin/env bash
# /task-continue：對目前目錄底下「沒做完」的背景 session 各送一句 continue（預設），
# 用在 API rate limit 或 daemon 重啟後 session 停在半路的時候。
# 用法：continue.sh [--dry-run] [訊息]
set -euo pipefail
dry=0
[[ "${1:-}" == "--dry-run" ]] && { dry=1; shift; }
msg="${1:-continue}"

# 跳過：done（已結束）、busy／running（還在跑 —— 對它 --resume 會開出一份複本）。
# ponytail: 狀態用排除法，claude 新增的狀態會被當成「要續跑」；先 --dry-run 看清單。
claude agents --json --all --cwd "$PWD" | python3 -c '
import json, sys
for a in json.load(sys.stdin):
    st = a.get("state") or a.get("status") or ""
    if a.get("kind") == "background" and st not in ("done", "busy", "running"):
        print(a["sessionId"], a["id"], a.get("name") or "-", st or "-", a["cwd"])
' | while read -r sid id name st cwd; do
  if (( dry )); then
    echo "  would continue  $id  $name  ($st)"
    continue
  fi
  echo "  continue  $id  $name  ($st)"
  (cd "$cwd" && claude --bg --resume "$sid" --permission-mode bypassPermissions "$msg") </dev/null
done
