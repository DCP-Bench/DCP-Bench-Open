The skill says an IntVar in 0..1 converts implicitly to BoolView. It does not: `BoolView r = intvar;` and `BoolView r(intvar);` both fail to compile (no BoolView(IntVar*) constructor).
Fix: create `BoolView r = newBoolVar();` and link it with `bool2int(r, intvar)`.
