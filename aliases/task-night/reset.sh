#!/usr/bin/env bash
# /task-night：從本 repo 停住的背景 session 畫面輸出，找用量上限的「resets …」字樣。
# 找不到就印 none。⚠ 字樣取自畫面輸出，不是穩定介面：把整行給使用者看，不要只信解析出的時間。
set -euo pipefail
found=0
while read -r id; do
  line=$(claude logs "$id" 2>/dev/null | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' \
    | command grep -oiE '.{0,60}resets?( at)? [0-9]{1,2}(:[0-9]{2})? ?(am|pm)?[^│]{0,30}' | tail -1 || true)
  if [[ -n "$line" ]]; then echo "$id  $line"; found=1; fi
done < <(claude agents --json --all --cwd "$PWD" | python3 -c '
import json, sys
for a in json.load(sys.stdin):
    st = a.get("state") or a.get("status") or ""
    if a.get("kind") == "background" and st not in ("done", "busy", "running"):
        print(a["id"])
')
(( found )) || echo none
