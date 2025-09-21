import re, shutil
from pathlib import Path

BASE   = Path(r"C:\Users\preet\Projects\nani\smartops")
DEMO   = Path(r"C:\Users\preet\Projects\nani\smartops-demo")
WORK   = BASE / r"sandbox\work"
SUGTXT = BASE / r"data\parsed\suggestion.txt"

def ensure_clean_dir(p: Path):
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)

def normalize(text: str) -> str:
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    if not t.endswith("\n"):
        t += "\n"
    # strip UTF-8 BOM if present
    return t.lstrip("\ufeff")

def parse_pin_from_suggestion(text: str):
    for line in text.splitlines():
        m = re.match(r"\+\s*([A-Za-z0-9_\-]+(?:==|>=)[^\s]+)\s*$", line.strip())
        if m:
            return m.group(1)
    return None

def apply_req_patch(req_path: Path, new_line: str):
    lines = []
    if req_path.exists():
        lines = normalize(req_path.read_text(encoding="utf-8", errors="replace")).splitlines()

    # ensure pytest present
    has_pytest = any(re.match(r"^\s*pytest(\s*(==|>=).*)?$", ln, re.I) for ln in lines)
    if not has_pytest:
        lines.append("pytest")

    # if we have a suggested pin, remove all existing pins for that pkg and add one clean line
    if new_line:
        pkg = new_line.split("==")[0].split(">=")[0]
        lines = [ln for ln in lines if not re.match(rf"^\s*{re.escape(pkg)}\s*(==|>=)\s*.+$", ln, re.I)]
        lines.append(new_line)

    # write back normalized
    content = "\n".join([ln for ln in lines if ln.strip()]) + "\n"
    req_path.write_text(content, encoding="utf-8")

def main():
    ensure_clean_dir(WORK)
    # copy demo repo into WORK (excluding .git)
    for item in DEMO.iterdir():
        if item.name == ".git":
            continue
        dest = WORK / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    # apply suggestion into WORK/requirements.txt
    sug = SUGTXT.read_text(encoding="utf-8", errors="replace") if SUGTXT.exists() else ""
    new_line = parse_pin_from_suggestion(sug)
    req = WORK / "requirements.txt"
    apply_req_patch(req, new_line)

    print(f"[✓] Prepared sandbox at: {WORK}")
    print(f"     requirements.txt exists: {req.exists()}")

if __name__ == "__main__":
    main()
