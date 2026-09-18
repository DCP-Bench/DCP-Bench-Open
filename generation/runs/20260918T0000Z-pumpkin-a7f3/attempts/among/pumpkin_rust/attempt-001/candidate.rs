// Exactly m of the n variables take a value from v.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let n = inst.size("n");
    let m_count = inst.int("m");
    let v = inst.ints("v");

    // 0..7 is the domain the problem statement fixes, not an instance field.
    let x = cp.ints(n, 0, 7);
    let mut hits: Vec<Lit> = Vec::new();
    for i in 0..n {
        for &value in &v {
            hits.push(cp.is(x[i], value));
        }
    }
    cp.exactly(&hits, m_count);

    let mut m = Model::new();
    m.put("x", x);
    m
}
