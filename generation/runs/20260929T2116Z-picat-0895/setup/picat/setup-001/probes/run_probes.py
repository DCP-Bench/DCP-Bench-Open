"""Run battery models (bat/*.pi) through the image; each file's first line is '% instance: {json}' and '% limit: N'."""
import json, subprocess, sys, tempfile, os, re
from pathlib import Path
B = Path(__file__).resolve().parent
names = sys.argv[1:] or sorted(p.stem for p in B.glob("*.pi"))
for name in names:
    src = (B / f"{name}.pi").read_text(encoding="utf-8")
    inst = json.loads(re.search(r"% instance: (.*)", src).group(1))
    limit = int(re.search(r"% limit: (\d+)", src).group(1))
    for backend in (("cp", "sat") if "import cp." in src else ("as-is",)):
        body = src if backend in ("cp", "as-is") else src.replace("import cp.", "import sat.")
        d = Path(tempfile.mkdtemp(prefix="bt_")); os.chmod(d, 0o755)
        (d / "model.pi").write_text(body, encoding="utf-8")
        (d / "request.json").write_text(json.dumps({"instance": inst, "solution_limit": limit, "execution_timeout": 30,
                                                    "compilation_timeout": 60, "legacy": False, "outputs": []}))
        cmd = ["docker", "run", "--rm", "--network=none", "--read-only", "--user=65534:65534",
               "--tmpfs", "/tmp:rw,exec,nosuid,size=536870912,mode=1777", "--mount", f"type=bind,source={d},target=/input,readonly",
               "--workdir=/tmp", "--env=HOME=/tmp", "dcp-eval/picat:v1"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        recs = [json.loads(l) for l in r.stdout.splitlines() if l.strip()]
        sols = [x["values"] for x in recs if x["type"] == "solution"]
        st = recs[-1] if recs else {}
        print(f"== {name} [{backend}] status={st.get('status')} n={len(sols)} detail={st.get('detail','')[:300]}")
        for s in sols[:4]: print("   ", json.dumps(s))
