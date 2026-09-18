// Fewest items from whole packs that still meet the target.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let packs = inst.ints("packs");
    let target = inst.int("target");
    let n = packs.len();

    // The reference allows up to twice the target of each pack size.
    let ceiling = target * 2;
    let counts = cp.ints(n, 0, ceiling);
    let total = cp.int(0, ceiling * n as i32);
    cp.sum_eq(weighted(&packs, &counts), total);
    cp.ge(vec![t(total)], target);

    let mut m = Model::new();
    m.put("counts", counts);
    m.minimise(total);
    m
}
