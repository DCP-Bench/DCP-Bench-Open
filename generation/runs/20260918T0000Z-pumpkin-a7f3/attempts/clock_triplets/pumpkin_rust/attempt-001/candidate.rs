// Rearrange 1..12 on a clock face so no three adjacent numbers exceed 21.
// The clock is the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, cp: &mut Cp) -> Model {
    let n = 12;
    let x = cp.ints(n, 1, n as i32);
    cp.all_different(terms(&x));

    // 21 is the smallest bound the highest triplet can have, which the problem
    // statement fixes; the reference bounds its triplet variable by it.
    for i in 0..n {
        let a = x[i];
        let b = x[(i + n - 1) % n];
        let cc = x[(i + n - 2) % n];
        cp.le(vec![t(a), t(b), t(cc)], 21);
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
