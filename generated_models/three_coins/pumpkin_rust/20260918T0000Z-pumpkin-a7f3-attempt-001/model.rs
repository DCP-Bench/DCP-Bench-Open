// Flip one coin per move so that all coins end up alike.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let init = inst.ints("init");
    let num_moves = inst.size("num_moves");
    let n = init.len();

    let steps = cp.bool_grid(num_moves + 1, n);
    for j in 0..n {
        cp.eq(vec![t(steps[0][j])], init[j]);
    }
    // Exactly one coin differs between consecutive rows.
    for row in 1..=num_moves {
        let same: Vec<Lit> = (0..n)
            .map(|j| {
                let flag = cp.bool();
                cp.iff_eq(flag, vec![t(steps[row][j]), c(-1, steps[row - 1][j])], 0);
                flag
            })
            .collect();
        cp.exactly(&same, n as i32 - 1);
    }
    // The last row is all heads or all tails.
    let last = cp.sum(terms(&steps[num_moves]));
    let none = cp.is(last, 0);
    let every = cp.is(last, n as i32);
    cp.any(vec![none, every]);

    let mut m = Model::new();
    m.put("steps", steps);
    m
}
