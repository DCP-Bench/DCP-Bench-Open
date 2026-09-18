// Recover individual bale weights from every pairwise total.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let n = inst.size("n");
    let weights = inst.ints("weights");

    // 0..50 is the bound the reference declares for the puzzle.
    let bales = cp.ints(n, 0, 50);
    let cells = terms(&bales);
    for &w in &weights {
        let i = cp.int(0, n as i32 - 1);
        let j = cp.int(0, n as i32 - 1);
        cp.lt(vec![t(i), c(-1, j)], 0);
        let left = cp.int(0, 50);
        let right = cp.int(0, 50);
        cp.element(i, cells.clone(), left);
        cp.element(j, cells.clone(), right);
        cp.eq(vec![t(left), t(right)], w);
    }

    let mut m = Model::new();
    m.put("bales", bales);
    m
}
