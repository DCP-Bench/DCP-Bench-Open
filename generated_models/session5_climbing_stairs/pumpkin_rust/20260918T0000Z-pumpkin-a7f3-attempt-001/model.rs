// Climb n stairs in moves of m1..m2, padding the tail with zeros.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let n = inst.size("n");
    let m1 = inst.int("m1");
    let m2 = inst.int("m2");

    // Each move is 0, or between m1 and m2; a sparse domain says exactly that.
    let allowed: Vec<i32> = std::iter::once(0).chain(m1..=m2).collect();
    let steps: Vec<Var> = (0..n).map(|_| cp.sparse(&allowed)).collect();
    cp.eq(terms(&steps), n as i32);

    // Once a move is zero every later move is zero, so the zeros are a suffix.
    for i in 1..n {
        let stopped = cp.is(steps[i - 1], 0);
        cp.when_eq(stopped, vec![t(steps[i])], 0);
    }

    let mut m = Model::new();
    m.put("steps", steps);
    m
}
