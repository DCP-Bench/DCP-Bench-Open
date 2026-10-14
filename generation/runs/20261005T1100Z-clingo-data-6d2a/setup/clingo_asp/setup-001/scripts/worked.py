import importlib.util, clingo
if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("r", "/s/run_new.py"); r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
    prog = r.facts({"alphabet": "ABEKNOXY", "words": ["BAKE", "ONYX"]}) + """
letter(L,C) :- alphabet_char(L,C).
word_letter(W,P,L) :- words_char(W,P,C), letter(L,C).
word_length(W,N) :- words(W,_), N = #count { P : words_char(W,P,_) }.
last_letter(W,L) :- words_char(W,P,C), not words_char(W,P+1,_), letter(L,C).
#show word_letter/3. #show word_length/2. #show last_letter/2.
"""
    c = clingo.Control(); c.add("base", [], prog); c.ground([("base", [])])
    c.solve(on_model=lambda m: print(sorted(str(s) for s in m.symbols(shown=True))))
    print(r.predicate("_SHIP"), r.predicate("_x"), r.predicate("N"), r.predicate("MAX_STEPS"), r.predicate("__Ab"))
    for bad in [{"a": "xy", "a_char": 1}, {"_": 1}]:
        try: r.facts(bad); print("accepted", bad)
        except ValueError as e: print("refused:", e)
