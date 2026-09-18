// Split 1..n into two halves with equal sums and equal sums of squares.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let n = inst.size("n");
    let half = n / 2;
    let top = n as i32;

    let a = cp.ints(half, 1, top);
    let b = cp.ints(half, 1, top);

    let mut every: Vec<Var> = a.clone();
    every.extend(b.iter().copied());
    cp.all_different(terms(&every));

    // equal sums
    let mut balance = terms(&a);
    balance.extend(b.iter().map(|&v| c(-1, v)));
    cp.eq(balance, 0);

    // equal sums of squares, each square introduced by a multiplication
    let mut square_balance: Vec<Term> = Vec::new();
    for &v in &a {
        let s = cp.int(1, top * top);
        cp.times(v, v, s);
        square_balance.push(t(s));
    }
    for &v in &b {
        let s = cp.int(1, top * top);
        cp.times(v, v, s);
        square_balance.push(c(-1, s));
    }
    cp.eq(square_balance, 0);

    let mut m = Model::new();
    m.put("A", a);
    m.put("B", b);
    m
}
