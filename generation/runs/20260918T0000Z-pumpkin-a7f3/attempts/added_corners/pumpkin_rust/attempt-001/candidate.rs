// Digits 1..8 around a square, each side cell the sum of its two corners.
// The layout is the puzzle itself, so the instance carries no fields.
fn build(_inst: &Instance, cp: &mut Cp) -> Model {
    let n = 8;
    let p = cp.ints(n, 1, n as i32);
    cp.all_different(terms(&p));

    // reading order: a b c / d e / f g h
    let (a, b, cc, d, e, f, g, h) = (p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7]);
    cp.eq(vec![t(b), c(-1, a), c(-1, cc)], 0);
    cp.eq(vec![t(d), c(-1, a), c(-1, f)], 0);
    cp.eq(vec![t(e), c(-1, cc), c(-1, h)], 0);
    cp.eq(vec![t(g), c(-1, f), c(-1, h)], 0);

    let mut m = Model::new();
    m.put("positions", p);
    m
}
