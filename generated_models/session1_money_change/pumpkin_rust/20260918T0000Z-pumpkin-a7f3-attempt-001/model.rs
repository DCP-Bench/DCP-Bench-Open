// Make the exact amount from the available coins, using as few coins as possible.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let amount = inst.int("amount");
    let types = inst.ints("types_of_coins");
    let available = inst.ints("available_coins");
    let n = types.len();

    let most = *available.iter().max().unwrap_or(&0);
    let counts = cp.ints(n, 0, most);
    cp.eq(weighted(&types, &counts), amount);
    for i in 0..n {
        cp.le(vec![t(counts[i])], available[i]);
    }

    let used = cp.sum(terms(&counts));

    let mut m = Model::new();
    m.put("coin_counts", counts);
    m.minimise(used);
    m
}
