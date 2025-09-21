import pathlib, subprocess, sys, threading, queue, time
import streamlit as st

BASE = pathlib.Path(r"C:\Users\preet\Projects\nani\smartops")
RCA  = BASE / r"data\parsed\gha_latest_rca.txt"
SUG  = BASE / r"data\parsed\suggestion.txt"
DIF  = BASE / r"data\parsed\patch.diff"
REP  = BASE / r"data\parsed\report.md"
RUN_PS = BASE / r"scripts\run_sandbox.ps1"

st.set_page_config(page_title="SmartOps — CI RCA", layout="wide")
st.title("SmartOps")
st.caption("DevOps automation: fetch logs → RCA → suggest fix → sandbox (MVP)")

col1, col2 = st.columns([3,2])

with col1:
    st.subheader("RCA (Root Cause)")
    rca = RCA.read_text(encoding="utf-8", errors="replace") if RCA.exists() else "— (RCA not found)"
    st.code(rca, language="text")

    st.subheader("Patch (Unified Diff)")
    diff = DIF.read_text(encoding="utf-8", errors="replace") if DIF.exists() else "— (no patch generated)"
    st.code(diff, language="diff")

with col2:
    st.subheader("Suggested Fix")
    sug = SUG.read_text(encoding="utf-8", errors="replace") if SUG.exists() else "— (suggestion not found)"
    st.code(sug, language="text")

    st.subheader("Actions")

    def stream_sandbox():
        if not RUN_PS.exists():
            return "Sandbox script not found."

        # Run PowerShell with policy bypass, capture stdout in real-time
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(RUN_PS)]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        out_box = st.empty()
        lines = []
        for line in proc.stdout:
            lines.append(line.rstrip("\n"))
            # Keep the output snappy without over-refreshing
            if len(lines) % 5 == 0:
                out_box.code("\n".join(lines[-400:]), language="bash")
        proc.wait()
        out_box.code("\n".join(lines[-400:]), language="bash")
        return f"Exit code: {proc.returncode}"

    if st.button("Try in Sandbox"):
        with st.spinner("Running sandbox… this can take a few minutes the first time"):
            rc = stream_sandbox()
        st.success(rc)

st.divider()
st.subheader("Full Report (Markdown)")
rep = REP.read_text(encoding="utf-8", errors="replace") if REP.exists() else "— (report not found)"
st.code(rep, language="markdown")
