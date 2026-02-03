#!/usr/bin/env python3
"""Quick local secrets scanner: high-entropy strings and common key patterns.
This is a lightweight helper, not a replacement for detect-secrets.
"""
import re
import sys
import os
import math

KEY_PATTERNS = [
    r"(?:AKIA|A3T|ASIA)[A-Z0-9]{16}",  # AWS access key id patterns (approx)
    r"[a-zA-Z0-9_-]{20,}",
    r"-----BEGIN PRIVATE KEY-----",
    r"-----BEGIN RSA PRIVATE KEY-----",
    r"-----BEGIN OPENSSH PRIVATE KEY-----",
]

ENTROPY_THRESHOLD = 3.5


def shannon_entropy(data: str) -> float:
    if not data:
        return 0.0
    prob = [float(data.count(c)) / len(data) for c in set(data)]
    entropy = -sum(p * math.log(p, 2) for p in prob)
    return entropy


def scan_file(path: str):
    try:
        with open(path, "r", errors="ignore") as f:
            data = f.read()
    except Exception:
        return []

    findings = []
    # Pattern matches
    for pat in KEY_PATTERNS:
        for m in re.finditer(pat, data):
            snippet = data[m.start() : m.end()]
            findings.append(("pattern", pat, snippet))

    # High entropy token candidates
    tokens = re.findall(r"[A-Za-z0-9+/=]{20,}", data)
    for t in tokens:
        e = shannon_entropy(t)
        if e >= ENTROPY_THRESHOLD:
            findings.append(("entropy", round(e, 2), t[:80]))

    return findings


def walk_and_scan(root: str = "."):
    results = {}
    for dirpath, dirs, files in os.walk(root):
        # skip venvs, .git
        if ".git" in dirpath.split(os.sep) or "venv" in dirpath.split(os.sep) or "node_modules" in dirpath.split(os.sep):
            continue
        for fn in files:
            fp = os.path.join(dirpath, fn)
            findings = scan_file(fp)
            if findings:
                results[fp] = findings
    return results


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    res = walk_and_scan(root)
    if not res:
        print("No likely secrets found (use detect-secrets for more thorough scan).")
        sys.exit(0)
    for path, items in res.items():
        print(f"== {path} ==")
        for it in items:
            print(" -", it)
    sys.exit(0)
