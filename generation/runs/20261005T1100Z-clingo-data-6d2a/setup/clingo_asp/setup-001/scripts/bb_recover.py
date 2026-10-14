"""Inside the clingo image: do the new character facts let ASP recover building_blocks words?"""
import importlib.util, json, sys
import clingo

PROGRAM = """
letter(L,C) :- alphabet_char(L,C).
word_letter(W,P,L) :- words_str_char(W,P,C), letter(L,C).
word_len(W,N) :- words_str(W,_), N = #count { P : words_str_char(W,P,_) }.
#show word_letter/3.
#show word_len/2.
"""

if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("runner_new", "/s/run_new.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    ok = True
    for i, inst in enumerate(json.load(open("/s/bb.json"))):
        control = clingo.Control()
        control.add("base", [], runner.facts(inst) + "\n" + PROGRAM)
        control.ground([("base", [])])
        atoms = []
        control.solve(on_model=lambda m: atoms.extend(m.symbols(shown=True)))
        letters, lengths = {}, {}
        for a in atoms:
            args = [x.number for x in a.arguments]
            if a.name == "word_letter":
                letters[(args[0], args[1])] = args[2]
            else:
                lengths[args[0]] = args[1]
        words = ["".join(inst["alphabet"][letters[(w, p)]] for p in range(lengths[w])) for w in sorted(lengths)]
        same = words == inst["words_str"]
        ok &= same
        print(i, same, words[:4], "...", len(words), "words")
    print("ALL_RECOVERED" if ok else "MISMATCH")
