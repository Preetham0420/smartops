import subprocess, sys
from pathlib import Path

BASE = Path(r"C:\Users\preet\Projects\nani\smartops")
RAW  = BASE / r"data\raw\gha_latest.log"
RCA  = BASE / r"data\parsed\gha_latest_rca.txt"
SUG  = BASE / r"data\parsed\suggestion.txt"
DIF  = BASE / r"data\parsed\patch.diff"
REP  = BASE / r"data\parsed\report.md"

def run(cmd):
    print(f"$ {' '.join(cmd)}")
    r = subprocess.run(cmd, shell=False)
    if r.returncode != 0:
        sys.exit(r.returncode)

def main():
    if not RAW.exists():
        print(f"[x] Log not found: {RAW}")
        sys.exit(2)

    # 1) RCA
    run([sys.executable, str(BASE / r"scripts\run_rca.py")])
    if not RCA.exists():
        print("[x] RCA not created")
        sys.exit(3)

    # 2) Suggestion (+ optional patch)
    run([sys.executable, str(BASE / r"scripts\suggest_fix.py")])
    if not SUG.exists():
        print("[x] Suggestion not created")
        sys.exit(4)

    # 3) Report
    run([sys.executable, str(BASE / r"scripts\make_report.py")])
    if not REP.exists():
        print("[x] Report not created")
        sys.exit(5)

    print("\n[✓] Pipeline done.")
    print(f"RCA:     {RCA}")
    print(f"Sugg:    {SUG}")
    print(f"Patch:   {DIF if DIF.exists() else '(none)'}")
    print(f"Report:  {REP}")

if __name__ == "__main__":
    main()
