#!/usr/bin/env python3
"""檢查「⛔」後面有沒有否定詞 —— 漏寫「不」會讓禁令變成指令。

由來：總線寫任務書時「⛔ 不整份讀大檔」被寫成「⛔ 整份讀大檔」，同一個 session
又犯了三次（2026-10-06 stage-121／132v／135），每次都是提交前人工抓到。

規則：`⛔` 後面（略過空白、`*`、`` ` ``）的前 8 個字內要有否定／停止類字
（容許「⛔ 任何人都不得」「⛔ 報告不得含」）；「⛔ 表」是指涉「⛔ 不在範圍」表，放行；
例外：
- 表格列以 `| ⛔` 開頭（「不在範圍」表的「不做」欄，表頭已帶否定）；
- 該行含 `<!-- neg-ok -->`（確定不是禁令時手動豁免）。

用法：
    python3 scripts/check_forbid_negation.py <檔案>...   # 有可疑處 exit 1
    python3 scripts/check_forbid_negation.py --self-test
"""
import re
import sys

NEG = set('不未沒停無別勿禁非零')
NEG_EN = re.compile(r"(?i)\b(not|no|never|don't|stop|none)\b")
WINDOW = 8
PAT = re.compile(r'⛔[\s*`]*([^\n]{0,%d})' % WINDOW)


def scan(lines):
    """回傳 [(行號, 行內容)]：⛔ 後 WINDOW 字內沒有否定詞的行。"""
    hits = []
    for no, line in enumerate(lines, 1):
        if '<!-- neg-ok -->' in line or line.lstrip().startswith('| ⛔'):
            continue
        if any(not (NEG & set(m.group(1)) or NEG_EN.search(m.group(1))
                    or m.group(1).startswith('表'))
               for m in PAT.finditer(line)):
            hits.append((no, line.rstrip('\n')))
    return hits


def self_test():
    bad = ['- ⛔ 整份讀附錄', '（⛔ `syncInfo`）', '**⛔ 只寫編號**', '結尾⛔',
           '（⛔ 重跑到綠）', '（⛔ `--force`）', '- ⛔ read the whole file']
    good = ['- ⛔ 不整份讀附錄', '⛔ **不**連測試服', '目標檔在就⛔ 停下來',
            '| ⛔ 改 `modules/` | 理由 |', '⛔ 改完再說 <!-- neg-ok -->', '沒有符號的行',
            '⛔ 任何人都不得跑', '逐條走 ⛔ 表', '- ⛔ do not read it', '⛔ never push']
    ok = all(scan([b]) for b in bad) and not any(scan([g]) for g in good)
    print('self-test', 'OK' if ok else 'FAIL')
    return 0 if ok else 1


def main(argv):
    if argv == ['--self-test']:
        return self_test()
    if not argv:
        print(__doc__)
        return 2
    total = 0
    for path in argv:
        with open(path, encoding='utf-8') as f:
            for no, line in scan(f):
                total += 1
                print(f'{path}:{no}: {line.strip()[:120]}')
    print(f'可疑 {total} 處（⛔ 後面沒有否定詞）' if total else 'OK：每個 ⛔ 後面都有否定詞')
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
