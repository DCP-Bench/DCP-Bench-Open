// The Pythagorean triplet whose three numbers add up to 1000.
// The target is the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, cp: &mut Cp) -> Model {
    let x = cp.ints(3, 1, 500);
    let (a, b, c_side) = (x[0], x[1], x[2]);
    cp.eq(terms(&x), 1000);

    // a*a + b*b == c*c, each square introduced by a multiplication
    let a2 = cp.int(1, 500 * 500);
    let b2 = cp.int(1, 500 * 500);
    let c2 = cp.int(1, 500 * 500);
    cp.times(a, a, a2);
    cp.times(b, b, b2);
    cp.times(c_side, c_side, c2);
    cp.eq(vec![t(a2), t(b2), c(-1, c2)], 0);

    let mut m = Model::new();
    m.put("a", a);
    m.put("b", b);
    m.put("c", c_side);
    m
}
