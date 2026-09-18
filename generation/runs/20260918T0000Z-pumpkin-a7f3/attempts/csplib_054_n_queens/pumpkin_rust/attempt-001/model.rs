// Place n queens so that no two share a row, column or diagonal.
// Columns are 1-indexed, as the reference declares them.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let n = inst.size("n");
    let queens = cp.ints(n, 1, n as i32);
    cp.all_different(terms(&queens));
    // The two diagonal all-differents, written as the pairwise disequalities
    // Pumpkin would decompose them into anyway.
    for i in 0..n {
        for j in (i + 1)..n {
            let d = (j - i) as i32;
            cp.ne(vec![t(queens[i]), c(-1, queens[j])], d);
            cp.ne(vec![t(queens[i]), c(-1, queens[j])], -d);
        }
    }

    let mut m = Model::new();
    m.put("queens", queens);
    m
}
