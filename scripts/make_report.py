from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\preet\Projects\nani\smartops")
RCA  = BASE / r"data\parsed\gha_latest_rca.txt"
SUG  = BASE / r"data\parsed\suggestion.txt"
DIF  = BASE / r"data\parsed\patch.diff"
OUT  = BASE / r"data\parsed\report.md"

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""

def main():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rca = read(RCA).strip()
    sug = read(SUG).strip()
    diff = read(DIF).strip()

    md = []
    md.append(f"# SmartOps Report  \n_Generated: {ts}_")
    md.append("\n## RCA (Root Cause)\n")
    md.append("```text")
    md.append(rca or "— (RCA file missing)")
    md.append("```")

    md.append("\n## Suggested Fix\n")
    md.append("```text")
    md.append(sug or "— (suggestion file missing)")
    md.append("```")

    md.append("\n## Patch (Unified Diff)\n")
    md.append("```diff")
    md.append(diff or "— (no patch generated)")
    md.append("```")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote report: {OUT}")

if __name__ == "__main__":
    main()
