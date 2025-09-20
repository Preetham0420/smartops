from pathlib import Path

RAW_LOG = Path(r"C:\Users\preet\Projects\nani\smartops\data\raw\gha_latest.log")
OUT_TXT = Path(r"C:\Users\preet\Projects\nani\smartops\data\parsed\gha_latest_rca.txt")

PATTERNS = [
    "ModuleNotFoundError", "ImportError", "AssertionError", "ERROR",
    "E   ", "Traceback", "Failed", "error:", "npm ERR!", "fatal:"
]

def find_anchor(lines):
    anchor = -1
    for i, line in enumerate(lines):
        if any(pat in line for pat in PATTERNS):
            anchor = i
    return anchor

def extract_block(lines, anchor, before=15, after=25):
    start = max(0, anchor - before) if anchor >= 0 else max(0, len(lines) - (before + after))
    end = min(len(lines), (anchor + after)) if anchor >= 0 else len(lines)
    return lines[start:end]

def main():
    if not RAW_LOG.exists():
        raise SystemExit(f"Log not found: {RAW_LOG}")

    text = RAW_LOG.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    anchor = find_anchor(lines)
    block = extract_block(lines, anchor)

    OUT_TXT.parent.mkdir(parents=True, exist_ok=True)
    OUT_TXT.write_text("\n".join(block), encoding="utf-8")

    print(f"RCA written to: {OUT_TXT} (lines: {len(block)})")

if __name__ == "__main__":
    main()
