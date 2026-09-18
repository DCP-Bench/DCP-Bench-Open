// Put each person in a free interview slot, one person per slot.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let free = inst.matrix("m");
    let n = free.len();

    let x = cp.bool_grid(n, n);
    let one = cp.constant(1);
    for i in 0..n {
        // the chosen slot must be one the person is free for
        cp.bool_sum_eq(&free[i], &x[i], one);
        cp.exactly(&x[i], 1);
        let column: Vec<Lit> = (0..n).map(|j| x[j][i]).collect();
        cp.exactly(&column, 1);
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
