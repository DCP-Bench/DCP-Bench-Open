// A permutation of 0..n-1 whose neighbouring differences permute 1..n-1.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let n = inst.size("n");
    let top = n as i32 - 1;

    let x = cp.ints(n, 0, top);
    let diffs = cp.ints(n - 1, 1, top);
    cp.all_different(terms(&x));
    cp.all_different(terms(&diffs));

    for i in 0..(n - 1) {
        let signed = cp.int(-top, top);
        cp.eq(vec![t(x[i + 1]), c(-1, x[i]), c(-1, signed)], 0);
        cp.abs(signed, diffs[i]);
    }

    let mut m = Model::new();
    m.put("x", x);
    m.put("diffs", diffs);
    m
}
