#!/usr/bin/env python3
"""寫文件當下的三項機械檢查（engineering-doc-writing）。有可疑處 exit 1。

  CLAIM  講現況的句子（既有／已有／現有／目前／原本／existing／currently…）
         同一行沒有證據：file:line、commit SHA、【強度】標記、或反引號裡的指令。
         由來：任務書寫「SIGINT 既有測試照跑」並當成驗收條款，那個測試不存在。
  ROW    表格列超過 --row-limit 字元（預設 600）。狀態列疊歷史就是從這裡開始的。
         由來：階段表 140 列、249 K 字元，一列平均 1～2 千字，總線只讀得到片段。
  MARK   一行有 4 個以上的強調標記（⚠🔴⛔⭐🔑🟡⏳🔒），或整份平均每行超過 1.0 個。
         由來：同一張表每行約 2 個標記，讀的人分不出哪條還有效。門檻依實測定：
         一般任務書每行 0.4～0.8 個，出問題的階段表 1.96。

只檢查「形狀」：CLAIM 綠不代表那個事實是對的，只代表旁邊附了可以重跑的出處。
確定不是現況主張的行加 `<!-- doc-ok -->`。程式碼框內不檢查。

用法：
    python3 check_doc_write.py <檔案>... [--row-limit N]
    python3 check_doc_write.py --self-test
"""
import re
import sys

STATE = re.compile(r'既有|已有|現有|目前|原本|現行|existing|currently|already', re.I)
EVIDENCE = re.compile(
    r'[\w./-]+\.\w+:\d+'                      # file:line
    r'|(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])'   # SHA
    r'|【[^】]+】'                             # 強度標記
    r'|`(?:git|command grep|grep|rg|wc|ls|find|awk|sed|cat|python3|node|cargo|jq)\b[^`]*`')
MARKS = '⚠🔴⛔⭐🔑🟡⏳🔒'
SKIP = '<!-- doc-ok -->'


def scan(lines, row_limit=600):
    hits, fence, marks, nonempty = [], False, 0, 0
    for no, line in enumerate(lines, 1):
        s = line.rstrip('\n')
        if s.lstrip().startswith('```'):
            fence = not fence
            continue
        if fence or SKIP in s:
            continue
        if s.strip():
            nonempty += 1
        n = sum(s.count(m) for m in MARKS)
        marks += n
        if STATE.search(s) and not EVIDENCE.search(s):
            hits.append(('CLAIM', no, s))
        if s.lstrip().startswith('|') and len(s) > row_limit:
            hits.append(('ROW', no, f'{len(s)} 字元 > {row_limit}'))
        if n >= 4:
            hits.append(('MARK', no, f'{n} 個標記'))
    if nonempty and marks / nonempty > 1.0:
        hits.append(('MARK', 0, f'整份 {marks}/{nonempty} = {marks / nonempty:.2f} 個標記／行 > 1.0'))
    return hits


def self_test():
    bad = ['SIGINT 既有測試照跑', '目前只建 terminate', 'the existing test covers it',
           '| x | ' + 'a' * 700 + ' |', '⚠ 🔴 ⛔ ⭐ 注意']
    good = ['既有測試 `git grep -n sigint s141 -- tests` ⇒ 0 筆', '目前在 `shutdown.rs:53` 建立',
            '現行 base `cd28145`', '既有 3 行【單鍵】', '<!-- doc-ok --> 目前狀態欄', '普通的一行',
            '```', '目前 這行在程式碼框裡', '```']
    for s in bad:
        assert scan([s]), f'應該抓到：{s}'
    assert not [h for h in scan(good) if h[1]], scan(good)
    assert scan(['⚠⚠ a', '⚠ b'])[-1][0] == 'MARK'        # 整份密度 1.5
    assert not scan(['⚠ a', 'b'])                         # 0.5：一般任務書的密度，不報
    print('self-test OK')


def main(argv):
    if argv == ['--self-test']:
        return self_test()
    limit = 600
    if '--row-limit' in argv:
        i = argv.index('--row-limit'); limit = int(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    total = 0
    for path in argv:
        with open(path, encoding='utf-8') as f:
            for kind, no, s in scan(f.readlines(), limit):
                total += 1
                print(f'{path}:{no}: {kind} {s[:120]}')
    print(f'可疑 {total} 處' if total else 'OK')
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
