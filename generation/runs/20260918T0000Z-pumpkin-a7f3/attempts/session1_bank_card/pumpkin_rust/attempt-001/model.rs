// A four digit PIN abcd with cd = 3*ab and da = 2*bc, all digits distinct.
// The clues are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, cp: &mut Cp) -> Model {
    let digits = cp.ints(4, 0, 9);
    let (a, b, c_digit, d) = (digits[0], digits[1], digits[2], digits[3]);
    cp.all_different(terms(&digits));

    // 10c + d == 3 * (10a + b)
    cp.eq(vec![c(10, c_digit), t(d), c(-30, a), c(-3, b)], 0);
    // 10d + a == 2 * (10b + c)
    cp.eq(vec![c(10, d), t(a), c(-20, b), c(-2, c_digit)], 0);

    let mut m = Model::new();
    m.put("a", a);
    m.put("b", b);
    m.put("c", c_digit);
    m.put("d", d);
    m
}
