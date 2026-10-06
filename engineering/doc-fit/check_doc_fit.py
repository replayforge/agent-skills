#!/usr/bin/env python3
"""Fail if a rewrite lost or changed any load-bearing token of the original.

A context-filling rewrite may ADD explanation; it must not drop or alter
facts. Load-bearing tokens, extracted from both versions:
  - IDs:      DEC-077, stage-121, s136v, R-83, Q-5, `code spans`
  - numbers:  15, 1:1, 256 MB, 2026-10-06 ...
  - quotes:   text inside 「」 or “” (people's own words)
Every token of the original must still appear in the rewrite (multiset:
appearing fewer times also fails, so a duplicated fact cannot be silently
merged into one).

usage: check_doc_fit.py <original> <rewrite>     exit 0 ok / 1 lost tokens
       check_doc_fit.py --self-test
"""
import re, sys
from collections import Counter

PAT = re.compile(
    r"`[^`\n]+`"                      # code spans
    r"|「[^」\n]+」|“[^”\n]+”"          # quoted words
    r"|\b[A-Z]{1,4}-\d+[a-z]?\b"       # DEC-077, R-83, Q-5
    r"|\bstage-\d+\b|\bs\d+v?\b"       # stage-121, s136v
    r"|\d+(?:[.:/-]\d+)*"              # numbers, dates, ratios
)

def tokens(text):
    return Counter(PAT.findall(text))

def lost(orig, new):
    a, b = tokens(orig), tokens(new)
    return {t: a[t] - b[t] for t in a if a[t] > b[t]}

def self_test():
    o = "DEC-077 Q-5：15 秒後「請找主管」，`checkBetStopped`。"
    ok = "背景說明……DEC-077 的 Q-5 規定：15 秒後顯示「請找主管」，用 `checkBetStopped` 查。"
    assert lost(o, ok) == {}, lost(o, ok)
    for bad in [o.replace("15", "30"), o.replace("「請找主管」", "請找主管"),
                o.replace("Q-5", "Q-6"), o.replace("`checkBetStopped`", "查詢")]:
        assert lost(o, bad), bad
    assert lost("A 15、B 15", "A 15、B 也一樣")  # merged duplicate fact
    print("self-test OK")

if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test(); sys.exit(0)
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    d = lost(open(sys.argv[1], encoding="utf-8").read(),
             open(sys.argv[2], encoding="utf-8").read())
    for t, n in sorted(d.items()):
        print(f"LOST x{n}: {t}")
    print("OK: every original token survives" if not d else f"{len(d)} token(s) lost or changed")
    sys.exit(1 if d else 0)
