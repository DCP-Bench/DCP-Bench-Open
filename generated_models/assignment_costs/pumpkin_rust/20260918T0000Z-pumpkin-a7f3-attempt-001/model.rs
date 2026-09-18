// Assign every task to a distinct person at least total cost.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let cost = inst.matrix("cost");
    let rows = cost.len();
    let cols = cost[0].len();

    let x = cp.bool_grid(rows, cols);
    for i in 0..rows {
        cp.exactly(&x[i], 1);
    }
    for j in 0..cols {
        let column: Vec<Lit> = (0..rows).map(|i| x[i][j]).collect();
        cp.at_most(&column, 1);
    }

    let ceiling: i32 = cost.iter().flatten().sum();
    let total = cp.int(0, ceiling);
    let mut spend: Vec<Term> = Vec::new();
    for i in 0..rows {
        spend.extend(weighted(&cost[i], &x[i]));
    }
    cp.sum_eq(spend, total);

    let mut m = Model::new();
    m.put("x", x);
    m.minimise(total);
    m
}
