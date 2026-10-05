"""Old vs new clingo_asp facts over every dataset instance: old lines kept in order, only *_char added."""
import glob, json, re, sys, types
from pathlib import Path

REPO = Path(r"C:\Users\kostis\code\DCP-Bench-Open")
HERE = Path(__file__).parent


def load(path, label):
    sys.modules.setdefault("runtime", types.SimpleNamespace(emit=None, finish=None))
    sys.modules.setdefault("clingo", types.ModuleType("clingo"))
    module = types.ModuleType(label)
    exec(compile(Path(path).read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


if __name__ == "__main__":
    sys.path.insert(0, str(REPO))
    from evaluation.reference import embedded_instance
    old = load(HERE / "run_old.py", "old")
    new = load(REPO / "solvers/clingo_asp/run.py", "new")
    total = changed_names = errors_same = 0
    stats = {"instances": 0, "with_char_facts": 0, "old_error_new_ok": [], "new_error_old_ok": [], "mismatch": []}
    for folder in sorted((REPO / "dataset").iterdir()):
        if not folder.is_dir():
            continue
        insts = []
        for ref in folder.glob("*.cpmpy.py"):
            try:
                insts.append(("example", embedded_instance(ref.read_text(encoding="utf-8"))))
            except Exception:
                pass
        for j in folder.glob("*.json"):
            try:
                data = json.loads(j.read_text(encoding="utf-8"))
            except Exception:
                continue
            if isinstance(data, list):
                insts += [(f"json:{i}", x) for i, x in enumerate(data) if isinstance(x, dict)]
        for label, inst in insts:
            stats["instances"] += 1
            try:
                a = old.facts(inst).split("\n")
            except Exception as e:
                a = e
            try:
                b = new.facts(inst).split("\n")
            except Exception as e:
                b = e
            where = f"{folder.name}/{label}"
            if isinstance(a, Exception) or isinstance(b, Exception):
                if isinstance(a, Exception) and not isinstance(b, Exception):
                    stats["old_error_new_ok"].append(where)
                elif isinstance(b, Exception) and not isinstance(a, Exception):
                    stats["new_error_old_ok"].append((where, str(b)))
                continue
            kept = [x for x in b if not re.match(r"^_*[a-z][A-Za-z0-9_]*_char\(", x) or x in a]
            extra = [x for x in b if x not in kept]
            if kept != a:
                stats["mismatch"].append(where)
            if extra:
                stats["with_char_facts"] += 1
    print(json.dumps(stats, indent=1))
