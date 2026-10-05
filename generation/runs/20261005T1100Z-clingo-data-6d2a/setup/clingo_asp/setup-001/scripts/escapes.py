import clingo, json
def run(prog):
    try:
        c = clingo.Control(["0"]); c.add("base", [], prog); c.ground([("base", [])])
        out = []
        c.solve(on_model=lambda m: out.append([repr(s.string) if s.type == clingo.SymbolType.String else str(s) for s in m.symbols(atoms=True)]))
        return out
    except Exception as e:
        return "ERR " + str(e)
if __name__ == "__main__":
    for text in ["plain", "é", "\t", "q\"b\\", "\n", "—", "a'b"]:
        print(repr(text), "dumps:", run("a(%s)." % json.dumps(text)), "raw-utf8:", run("a(%s)." % json.dumps(text, ensure_ascii=False)))
