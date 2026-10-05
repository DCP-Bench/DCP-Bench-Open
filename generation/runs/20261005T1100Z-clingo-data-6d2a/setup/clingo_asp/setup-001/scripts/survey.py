"""Survey retained clingo_asp models: string fields, underscore fields, *_char usage."""
import glob, json, re, sys
from pathlib import Path

sys.path.insert(0, ".")
from evaluation.reference import embedded_instance


def strings_in(v):
    if isinstance(v, str):
        return True
    if isinstance(v, list):
        return any(strings_in(x) for x in v)
    return False


if __name__ == "__main__":
    rows = []
    for model in sorted(glob.glob("generated_models/*/clingo_asp/*/model.lp")):
        problem = Path(model).parts[1]
        d = Path("dataset") / problem
        refs = list(d.glob("*.cpmpy.py")) or list(d.glob("*.py"))
        insts = []
        if refs:
            try:
                insts.append(embedded_instance(refs[0].read_text(encoding="utf-8")))
            except Exception as e:
                insts.append({})
        j = d / f"{problem}.json"
        if j.exists():
            insts += json.load(open(j, encoding="utf-8"))
        declared_str, meta_str, under, nonascii = set(), set(), set(), set()
        for inst in insts:
            for k, v in inst.items():
                if k.startswith("_"):
                    under.add(k)
                if strings_in(v):
                    (meta_str if k in ("name", "note") else declared_str).add(k)
                    if any(ord(c) > 127 for c in json.dumps(v, ensure_ascii=False)):
                        nonascii.add(k)
        src = Path(model).read_text(encoding="utf-8")
        chars = sorted(set(re.findall(r"\b[a-z_][A-Za-z0-9_]*_char\b", src)))
        rows.append((model, sorted(declared_str), sorted(meta_str), sorted(under), sorted(nonascii), chars))
    for r in rows:
        if r[1] or r[3] or r[4] or r[5]:
            print(r)
    print("total", len(rows), "with name/note strings", sum(1 for r in rows if r[2]))
