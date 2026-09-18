// Reconstruct a 0/1 matrix from its row and column sums.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let row_sums = inst.ints("row_sums");
    let col_sums = inst.ints("col_sums");
    let r = row_sums.len();
    let c = col_sums.len();

    let matrix = cp.grid(r, c, 0, 1);
    for i in 0..r {
        cp.eq(terms(&matrix[i]), row_sums[i]);
    }
    for j in 0..c {
        let column: Vec<Var> = (0..r).map(|i| matrix[i][j]).collect();
        cp.eq(terms(&column), col_sums[j]);
    }

    let mut m = Model::new();
    m.put("matrix", matrix);
    m
}
