// Langford's problem: the two copies of i sit i places apart.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let k = inst.size("k");
    let length = 2 * k;

    let position = cp.ints(length, 0, length as i32 - 1);
    let sol = cp.ints(length, 1, k as i32);
    cp.all_different(terms(&position));

    let cells = terms(&sol);
    for i in 1..=k {
        // the second copy of i is i + 1 places after the first
        cp.eq(
            vec![t(position[i + k - 1]), c(-1, position[i - 1])],
            i as i32 + 1,
        );
        let value = cp.constant(i as i32);
        cp.element(position[i - 1], cells.clone(), value);
        cp.element(position[k + i - 1], cells.clone(), value);
    }

    let mut m = Model::new();
    m.put("sol", sol);
    m
}
