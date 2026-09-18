// Fewest raw rolls cut, using the given patterns to meet every order.
//
// The instance also carries `roll_width` and the `widths` themselves. The
// reference uses neither in a constraint, only `len(widths)`: the patterns in
// `num_rolls_width` already encode what fits on a roll, so re-deriving them
// here would be a different problem from the one the reference states.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let orders = inst.ints("orders");
    let num_patterns = inst.size("num_patterns");
    let per_pattern = inst.matrix("num_rolls_width");
    let widths = inst.len("widths");

    // 0..100 uses of each pattern is the bound the reference declares.
    let used = cp.ints(num_patterns, 0, 100);
    for i in 0..widths {
        let yields: Vec<i32> = (0..num_patterns).map(|j| per_pattern[j][i]).collect();
        cp.ge(weighted(&yields, &used), orders[i]);
    }

    let rolls = cp.sum(terms(&used));

    let mut m = Model::new();
    m.put("patterns_used", used);
    m.put("min_rolls_cut", rolls);
    m.minimise(rolls);
    m
}
