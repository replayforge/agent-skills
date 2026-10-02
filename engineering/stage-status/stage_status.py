#!/usr/bin/env python3
"""Live stage board: which stages are running, waiting to be dispatched,
waiting on the orchestrator, or waiting to be merged. Read-only.

Derived from git and the filesystem every time it runs, so it cannot go
stale the way a hand-maintained status table does.

Conventions it assumes (override in <repo>/.stage-status.json):
  - stage documents live in one directory:   stage-<N>-<slug>.md
        brief           stage-<N>-<slug>.md
        report          stage-<N>-<slug>-result.md
        verify brief    stage-<N>-<slug>-verify.md
        verdict         stage-<N>-<slug>-verify-result.md
  - every dispatched session works on its own branch + worktree:
        executor  s<N>      verifier  s<N>v
  - the orchestrator records verdicts in a register table whose rows start
    with "| <N> |" and carry a verdict marker (✅/🔴/⏸ + **ACCEPT/REJECT/BLOCKED**).
    Stages the orchestrator accepted itself have no verdict file, only this row.

Usage:
  python3 stage_status.py [--repo PATH] [--all] [--json]
"""
import json
import os
import re
import subprocess
import sys
import time

DEFAULTS = {
    "tasks_dir": "docs/tasks",
    "main_branch": None,                 # None ⇒ the branch checked out in --repo
    "executor_branch": "s{n}",
    "verifier_branch": "s{n}v",
    "register": "docs/tasks/README.md",  # set to null if there is no register
    "verdict_marker": r"(✅|🔴|⏸)\s*\*\*[^|`]{0,10}`?(ACCEPT|REJECT|BLOCKED)",
    # Stages numbered below this with no branch predate the worktree convention;
    # their state cannot be derived, so they are hidden unless --all.
    "hide_branchless_below": 0,
    "stale_minutes": 60,
}
FILE = re.compile(r"^stage-(\d+)-.+?(-verify-result|-verify|-result)?(-[A-Z])?\.md$")
SKIP_DIRS = {".git", "target", "node_modules", "dist", "build", ".venv"}
OPEN = ("pending dispatch", "running", "verify pending dispatch", "verifying",
        "done, awaiting acceptance")


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo, "-c", "core.quotepath=false", *args],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def load_config(repo):
    cfg = dict(DEFAULTS)
    path = os.path.join(repo, ".stage-status.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            cfg.update(json.load(f))
    if not cfg["main_branch"]:
        cfg["main_branch"] = git(repo, "rev-parse", "--abbrev-ref", "HEAD") or "HEAD"
    return cfg


def files_on(repo, ref, tasks_dir):
    """{stage: {kind: path}} for the stage documents present on `ref`."""
    out = {}
    for p in git(repo, "ls-tree", "-r", "--name-only", ref, "--", tasks_dir).splitlines():
        m = FILE.match(os.path.basename(p))
        if m:
            kind = (m.group(2) or "-brief").lstrip("-")
            out.setdefault(int(m.group(1)), {})[kind] = p
    return out


def verdict(repo, ref, path):
    """Verdicts are written at the top; only the head is read so that prose
    like "must not REJECT" further down cannot match."""
    head = "\n".join(git(repo, "show", f"{ref}:{path}").splitlines()[:40])
    for k in ("REJECT", "BLOCKED", "ACCEPT"):
        if k in head:
            return k
    return ""


def registered(repo, cfg):
    """Stages whose verdict the orchestrator already recorded in the register."""
    if not cfg["register"]:
        return set()
    try:
        text = open(os.path.join(repo, cfg["register"]), encoding="utf-8").read()
    except OSError:
        return set()
    marker = re.compile(cfg["verdict_marker"])
    out = set()
    for line in text.splitlines():
        m = re.match(r"^\| *(\d+) *\|", line)
        if m and marker.search(line):
            out.add(int(m.group(1)))
    return out


def worktrees(repo):
    """{branch: path}, skipping worktrees whose directory was deleted
    (git marks them prunable) — otherwise they would read as "running"."""
    out, path = {}, None
    for line in git(repo, "worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            path = line[9:]
        elif line.startswith("branch ") and path and os.path.isdir(path):
            out[line.rsplit("/", 1)[-1]] = path
    return out


def activity(repo, path):
    """(uncommitted file count, minutes since the newest file change)."""
    dirty = len([l for l in git(path, "status", "--porcelain").splitlines() if l.strip()])
    newest = 0.0
    # ponytail: walks the whole tree; build dirs are skipped. Fine for doc-sized trees.
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            try:
                newest = max(newest, os.path.getmtime(os.path.join(root, f)))
            except OSError:
                pass
    return dirty, (int((time.time() - newest) / 60) if newest else None)


def merged(repo, branch, main):
    return subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", branch, main],
                          capture_output=True).returncode == 0


def board(repo, cfg, show_all=False):
    main = cfg["main_branch"]
    branches = set(git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines())
    wts = worktrees(repo)
    reg = registered(repo, cfg)
    main_files = files_on(repo, main, cfg["tasks_dir"])
    ex = re.compile("^" + re.escape(cfg["executor_branch"]).replace(r"\{n\}", r"(\d+)") + "$")
    vf = re.compile("^" + re.escape(cfg["verifier_branch"]).replace(r"\{n\}", r"(\d+)") + "$")
    nums = set(main_files)
    for b in branches:
        m = ex.match(b) or vf.match(b)
        if m:
            nums.add(int(m.group(1)))

    rows = []
    for n in sorted(nums):
        e, v = cfg["executor_branch"].format(n=n), cfg["verifier_branch"].format(n=n)
        # Main first; a document only on a branch means "done but not merged yet".
        found = dict(main_files.get(n, {}))
        src = {k: main for k in found}
        for b in (e, v):
            if b in branches:
                for k, p in files_on(repo, b, cfg["tasks_dir"]).get(n, {}).items():
                    if k not in found:
                        found[k], src[k] = p, b
        vd = verdict(repo, src["verify-result"], found["verify-result"]) if "verify-result" in found else ""
        unmerged = [b for b in (e, v) if b in branches and not merged(repo, b, main)]

        # Latest state wins.
        if v in wts and "verify-result" not in found:
            state = "verifying"
        elif n in reg:
            state = "recorded, awaiting merge" if unmerged else "closed"
        elif "verify-result" in found:
            state = f"verdict {vd}, awaiting record"
        elif "verify" in found:
            state = "verify pending dispatch"
        elif "result" in found:
            state = "done, awaiting acceptance"
        elif e in wts:
            state = "running"
        elif "brief" in found:
            state = "pending dispatch"
        else:
            state = "branch only"

        has_branch = e in branches or v in branches
        if not show_all and (state == "closed" or
                             (not has_branch and n < cfg["hide_branchless_below"])):
            continue

        act = None
        for b in (v, e):  # the verifier's tree is the newer one
            if b in wts:
                dirty, mins = activity(repo, wts[b])
                act = {"worktree": b, "uncommitted": dirty, "minutes_since_change": mins}
                break
        rows.append({"stage": n, "state": state, "unmerged": unmerged, "activity": act})
    return rows


def main():
    args = sys.argv[1:]
    repo = os.getcwd()
    if "--repo" in args:
        repo = args[args.index("--repo") + 1]
    repo = git(repo, "rev-parse", "--show-toplevel") or repo
    cfg = load_config(repo)
    rows = board(repo, cfg, show_all="--all" in args)

    if "--json" in args:
        print(json.dumps({"repo": repo, "main_branch": cfg["main_branch"],
                          "stale_minutes": cfg["stale_minutes"], "stages": rows},
                         ensure_ascii=False, indent=1))
        return
    if not rows:
        print("(no open stages)")
        return
    print(f"repo {repo}  main {cfg['main_branch']}")
    print(f"{'#':>4}  {'state':<28} {'unmerged':<14} activity")
    print("-" * 78)
    for r in rows:
        a = r["activity"]
        act = ""
        if a:
            mins = a["minutes_since_change"]
            act = f"{a['worktree']}: {a['uncommitted']} uncommitted, " + (
                f"changed {mins} min ago" if mins is not None else "empty")
            if r["state"] in ("running", "verifying") and mins is not None and mins > cfg["stale_minutes"]:
                act += "  ⚠ possibly stalled"
        print(f"{r['stage']:>4}  {r['state']:<28} {','.join(r['unmerged']) or '-':<14} {act}")
    print("\n⚠ 'pending dispatch' may also mean a session is open but has not created its worktree yet.")
    print("⚠ A fresh worktree's change time is its creation time: recent ≠ progress.")


if __name__ == "__main__":
    main()
