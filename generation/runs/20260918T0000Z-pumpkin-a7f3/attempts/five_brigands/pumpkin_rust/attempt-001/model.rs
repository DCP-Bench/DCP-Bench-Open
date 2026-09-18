// Five brigands share 200 doubloons, and a reweighted share also totals 200.
// The puzzle fixes every number, so the instance carries no fields of its own.
fn build(_inst: &Instance, cp: &mut Cp) -> Model {
    let x = cp.ints(5, 1, 200);
    cp.eq(terms(&x), 200);
    // 6 * (12A + 3B + C) + 3D + 2E == 6 * 200, cleared of fractions.
    cp.eq(
        vec![c(72, x[0]), c(18, x[1]), c(6, x[2]), c(3, x[3]), c(2, x[4])],
        1200,
    );

    let mut m = Model::new();
    for (name, v) in ["A", "B", "C", "D", "E"].iter().zip(&x) {
        m.put(name, *v);
    }
    m
}
