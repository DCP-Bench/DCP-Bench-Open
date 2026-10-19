// Pythagorean triplet: naturals a, b, c with a < b < c, a^2 + b^2 = c^2 and a + b + c = 1000.
// The instance carries no data, so the sum 1000 comes from the description.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // Bounds from the description: a < b < c and a + b + c = 1000 give a <= 332, b <= 499, c <= 998.
    let a = IntVar::new(1..=332);
    let b = IntVar::new(1..=499);
    let c = IntVar::new(1..=998);

    // a + b + c = 1000
    post(s, iv(&a) + iv(&b) + iv(&c), Comparator::Equal, 1000)?;

    // a < b < c
    post(s, iv(&a) - iv(&b), Comparator::LessEq, -1)?;
    post(s, iv(&b) - iv(&c), Comparator::LessEq, -1)?;

    // a^2 + b^2 = c^2. With c fixed by a + b + c = 1000, forbid each pair (a, b)
    // whose squares do not satisfy the equation.
    for i in 1..=332i64 {
        for j in (i + 1)..=499i64 {
            let k = 1000 - i - j;
            if i * i + j * j != k * k {
                let ai = a.equals(s, i)?;
                let bj = b.equals(s, j)?;
                s.add_clause([!ai, !bj])?;
            }
        }
    }

    let mut out = Out::new();
    out.put("a", &a).put("b", &b).put("c", &c);
    Ok(out)
}
