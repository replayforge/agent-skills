#!/usr/bin/env python3
"""Dispatch every stage that is ready, as background agent sessions.

Reads the live stage board (../stage-status/stage_status.py), picks stages in
`pending dispatch` / `verify pending dispatch` that have a prompt file, applies
the concurrency rules, and launches one background session per stage with the
prompt file's content. Prints what it launched and what it held back, and why.

Prompt files live next to the briefs:
    stage-<N>-<slug>-prompt.md          executor prompt  → session named s<N>
    stage-<N>-<slug>-verify-prompt.md   verifier prompt  → session named s<N>v
The first line may declare the stage kind, used by the concurrency rules:
    <!-- stage-run: kind=docs -->      docs | research | crate | merge   (default docs)

Usage:
  python3 stage_run.py [--repo PATH] [--dry-run] [--only N[,N…]]
"""
import importlib.util
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
_spec = importlib.util.spec_from_file_location(
    "stage_status", os.path.join(HERE, "..", "stage-status", "stage_status.py"))
ss = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ss)

RUN_DEFAULTS = {
    # {name} = session name, {prompt} = full prompt text. Runs with cwd = repo root.
    "launcher": ["claude", "--bg", "-n", "{name}", "--permission-mode", "bypassPermissions", "{prompt}"],
    "max_parallel": 3,   # all stages running at once
    "max_crate": 1,      # stages that build shipping code: they share build caches and merge surfaces
    "max_merge": 1,      # merge stages move the integration branch
    # Appended to every prompt: a background session has nobody to answer it.
    "background_note": (
        "\n\n---\nYou are running as a background session with no human watching. "
        "Do not wait for answers: if you hit a decision that belongs to the user or "
        "the orchestrator, write it into your report as an open question and stop. "
        "Commit only your own files; do not push."
    ),
}
KIND = re.compile(r"<!--\s*stage-run:\s*kind=(\w+)\s*-->")


def kind_of(text):
    m = KIND.search(text.splitlines()[0] if text else "")
    return m.group(1) if m else "docs"


def read_on(repo, ref, path):
    return ss.git(repo, "show", f"{ref}:{path}")


def main():
    args = sys.argv[1:]
    repo = args[args.index("--repo") + 1] if "--repo" in args else os.getcwd()
    repo = ss.git(repo, "rev-parse", "--show-toplevel") or repo
    dry = "--dry-run" in args
    only = None
    if "--only" in args:
        only = {int(x) for x in args[args.index("--only") + 1].split(",")}

    cfg = ss.load_config(repo)
    run = {**RUN_DEFAULTS, **cfg.get("run", {})}
    main_ref = cfg["main_branch"]
    rows = ss.board(repo, cfg)

    # Count what is already running, by kind (from that stage's own prompt file).
    running = {"total": 0, "crate": 0, "merge": 0}
    for r in rows:
        if r["state"] in ("running", "verifying"):
            key = "verify-prompt" if r["state"] == "verifying" else "prompt"
            p = r["files"].get(key)
            # No prompt file (e.g. dispatched by hand): we cannot tell its kind, so count
            # it as crate — the conservative choice; it only ever holds a launch back.
            k = kind_of(read_on(repo, main_ref, p)) if p else "crate"
            running["total"] += 1
            if k in ("crate", "merge"):
                running[k] += 1

    before = dict(running)
    launched, held = [], []
    for r in rows:
        n = r["stage"]
        if only and n not in only:
            continue
        if r["state"] == "pending dispatch":
            key, name = "prompt", cfg["executor_branch"].format(n=n)
        elif r["state"] == "verify pending dispatch":
            key, name = "verify-prompt", cfg["verifier_branch"].format(n=n)
        else:
            continue
        path = r["files"].get(key)
        if not path:
            held.append((n, name, f"no {key} file — orchestrator has to write one"))
            continue
        if name in r.get("sessions", {}):
            held.append((n, name, "a session with this name is already live"))
            continue
        text = read_on(repo, main_ref, path)
        k = kind_of(text)
        if running["total"] >= run["max_parallel"]:
            held.append((n, name, f"max_parallel={run['max_parallel']} reached"))
            continue
        if k in ("crate", "merge") and running[k] >= run[f"max_{k}"]:
            held.append((n, name, f"another {k} stage is running (max_{k}={run[f'max_{k}']})"))
            continue

        cmd = [a.replace("{name}", name).replace("{prompt}", text + run["background_note"])
               for a in run["launcher"]]
        if dry:
            launched.append((n, name, k, "(dry run)"))
        else:
            res = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
            out = (res.stdout.strip() or res.stderr.strip()).splitlines()
            status = out[-1] if out else ""
            if res.returncode != 0:
                held.append((n, name, f"launcher failed (exit {res.returncode}): {status}"))
                continue
            launched.append((n, name, k, status))
        running["total"] += 1
        if k in ("crate", "merge"):
            running[k] += 1

    print(f"repo {repo}  main {main_ref}  already running: {before}")
    for n, name, k, status in launched:
        print(f"  ▶ launched  {n:>4}  {name:<8} kind={k:<8} {status}")
    for n, name, why in held:
        print(f"  ⏸ held      {n:>4}  {name:<8} {why}")
    if not launched and not held:
        print("  (nothing ready to dispatch)")
    if any(k == "merge" for _, _, k, _ in launched):
        print("⚠ A merge stage is running: do not commit to the integration branch until it finishes.")
    if launched and not dry:
        print("Watch: `claude agents`  ·  attach: `claude attach <id>`  ·  logs: `claude logs <id>`")


if __name__ == "__main__":
    main()
