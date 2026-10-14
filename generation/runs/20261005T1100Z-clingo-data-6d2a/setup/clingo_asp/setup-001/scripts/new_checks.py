"""Run only the two new readiness checks against whatever clingo_asp image is built."""
import importlib.util, json, sys, tempfile
from pathlib import Path

REPO = Path(r"C:\Users\kostis\code\DCP-Bench-Open")

if __name__ == "__main__":
    sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location("rt", REPO / "solvers/clingo_asp/readiness_test.py")
    rt = importlib.util.module_from_spec(spec); spec.loader.exec_module(rt)
    assert "_n(N)" in rt.UNDERSCORED and " n(N)" not in rt.UNDERSCORED, rt.UNDERSCORED
    from evaluation import evaluate
    with tempfile.TemporaryDirectory() as d:
        out = {}
        for name, src, ref, inst in [
            ("underscore_field", rt.UNDERSCORED, rt.UNDERSCORED_REFERENCE, [{"_N": 3}]),
            ("string_characters", rt.STRINGS, rt.STRINGS_REFERENCE,
             [{"alphabet": "ZYX", "words": ["XY", "Z", "YYZX"]}])]:
            p = Path(d) / f"{name}.lp"; p.write_text(src, encoding="utf-8")
            r = evaluate(p, "readiness", "clingo_asp", reference_source=ref, instances=inst, instance_count=2)
            out[name] = {"accepted": r["accepted"], "reason": r.get("reason"), "detail": str(r.get("detail"))[:200],
                         "image": r["image"]["id"][:19], "instances_checked": r.get("instances_checked")}
    print(json.dumps(out, indent=1))
