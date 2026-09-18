// Each guard takes half the apples plus one; one apple survives the last gate.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let gates = inst.size("num_gates");

    // 0..100 is the bound the reference declares for the puzzle.
    let apples = cp.ints(gates + 1, 0, 100);
    cp.eq(vec![t(apples[gates])], 1);
    for i in 1..=gates {
        // before == 2 * (after + 1)
        cp.eq(vec![t(apples[i - 1]), c(-2, apples[i])], 2);
    }

    let mut m = Model::new();
    m.put("apples", apples);
    m
}
