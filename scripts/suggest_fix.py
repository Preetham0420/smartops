import re
from pathlib import Path
import difflib

RCA_TXT    = Path(r"C:\Users\preet\Projects\nani\smartops\data\parsed\gha_latest_rca.txt")
SUG_TXT    = Path(r"C:\Users\preet\Projects\nani\smartops\data\parsed\suggestion.txt")
PATCH_DIFF = Path(r"C:\Users\preet\Projects\nani\smartops\data\parsed\patch.diff")

# Demo repo requirements file:
REQ_PATH   = Path(r"C:\Users\preet\Projects\nani\smartops-demo\requirements.txt")

def parse_rca(rca: str):
    m = re.search(r"requirement\s+([A-Za-z0-9_\-]+)\s*==\s*([0-9][^\s]*)", rca, flags=re.IGNORECASE)
    if m:
        pkg, ver = m.group(1), m.group(2)
        return {"type": "bad_pin", "pkg": pkg, "ver": ver}
    m2 = re.search(r"ModuleNotFoundError:\s+No module named ['\"]([^'\"]+)['\"]", rca)
    if m2:
        return {"type": "missing_pkg", "pkg": m2.group(1)}
    return {"type": "unknown"}

def build_suggestion(info):
    if info["type"] == "bad_pin":
        pkg = info["pkg"]
        pinned = f"{pkg}==1.26.4" if pkg.lower()=="numpy" else f"{pkg}>=1.0.0"
        explanation = (
            f"The CI failed during dependency resolution because **{pkg}=={info['ver']}** "
            f"does not exist for this Python version. Pin {pkg} to a known good version."
        )
        commands = f"Update requirements.txt:\n- {pkg}=={info['ver']}\n+ {pinned}"
        return explanation, commands, (pkg, info["ver"], pinned)
    if info["type"] == "missing_pkg":
        pkg = info["pkg"]
        explanation = f"Tests import **{pkg}**, but it is not installed. Add it to requirements.txt."
        commands = f"Append to requirements.txt:\n+ {pkg}"
        return explanation, commands, (pkg, None, pkg)
    return ("SmartOps could not confidently classify the error. Needs manual review.",
            "Inspect the RCA block and full log.", None)

def normalize_newlines(text: str) -> str:
    # Normalize to LF, ensure file ends with newline
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    if not t.endswith("\n"):
        t += "\n"
    return t

def smart_edit_requirements(edit, req_path: Path) -> str | None:
    if not edit or not req_path.exists():
        return None
    pkg, old, new = edit
    before = normalize_newlines(req_path.read_text(encoding="utf-8", errors="replace"))
    after  = before

    # 1) Try exact pin replace (tolerant spacing, case-insensitive)
    if old:
        pattern = rf"(?im)^\s*{re.escape(pkg)}\s*==\s*{re.escape(old)}\s*$"
        after2  = re.sub(pattern, new, after)
        if after2 != after:
            after = after2
        else:
            # 2) Try replacing any line that pins the same package (unknown old)
            pattern_any_pin = rf"(?im)^\s*{re.escape(pkg)}\s*==\s*[0-9][^\s]*\s*$"
            after2 = re.sub(pattern_any_pin, new, after)
            if after2 != after:
                after = after2
            else:
                # 3) Append new pin if package not present as a line
                if not re.search(rf"(?im)^\s*{re.escape(pkg)}(\s*==|\s*>=|\s*$)", after):
                    after += f"{new}\n"
                else:
                    # If package is present without version, replace that line
                    pattern_name_only = rf"(?im)^\s*{re.escape(pkg)}\s*$"
                    after = re.sub(pattern_name_only, new, after)
    else:
        # missing package case: append if not present
        if not re.search(rf"(?im)^\s*{re.escape(pkg)}(\s*==|\s*>=|\s*$)", after):
            after += f"{new}\n"

    # Build unified diff
    before_lines = before.splitlines(keepends=True)
    after_lines  = normalize_newlines(after).splitlines(keepends=True)
    diff = "\n".join(difflib.unified_diff(
        before_lines, after_lines,
        fromfile=str(req_path), tofile=str(req_path),
        lineterm=""
    ))
    return diff if diff.strip() else None

def main():
    rca = RCA_TXT.read_text(encoding="utf-8", errors="replace") if RCA_TXT.exists() else ""
    info = parse_rca(rca)
    explanation, commands, edit = build_suggestion(info)

    SUG_TXT.parent.mkdir(parents=True, exist_ok=True)
    SUG_TXT.write_text(f"Explanation:\n{explanation}\n\nSuggested fix:\n{commands}\n", encoding="utf-8")

    diff = smart_edit_requirements(edit, REQ_PATH)
    if diff:
        PATCH_DIFF.write_text(diff, encoding="utf-8")
        print(f"Wrote: {SUG_TXT}")
        print(f"Wrote: {PATCH_DIFF}")
    else:
        print(f"Wrote: {SUG_TXT}")
        print("No patch produced — check that requirements.txt exists and contains the package line.")

if __name__ == "__main__":
    main()
