// ISBN-13 validation and check digit calculation: the 13 digits of an ISBN-13, where -1 marks
// an unknown digit. Find the unknown digits so that the number is a valid ISBN-13.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let init = inst.ints("isbn_init");
    let n = init.len();

    // Each digit is 0..9; a given digit is fixed to its value.
    let mut d: Vec<IntVar> = Vec::new();
    for i in 0..n {
        let x = IntVar::new(0..=9);
        if init[i] != -1 {
            post(s, iv(&x), Comparator::Equal, init[i])?;
        }
        d.push(x);
    }

    // An ISBN-13 must start with 978 or 979.
    post(s, iv(&d[0]), Comparator::Equal, 9)?;
    post(s, iv(&d[1]), Comparator::Equal, 7)?;
    // The third digit is 8 or 9, so it is not 0..=7.
    let below_eight = reify_le(s, iv(&d[2]), 7)?;
    s.add_clause([!below_eight])?;

    // Multiply the digits alternately by 1 and 3 (starting with 1) and sum the products.
    // The check digit is (10 - sum % 10) % 10, so the weighted sum of all 13 digits is
    // a multiple of 10: sum = 10 * q.
    let mut sum = LinExp::default();
    for i in 0..n {
        let w: i64 = if i % 2 == 0 { 1 } else { 3 };
        sum += scaled(&d[i], w);
    }
    let q = IntVar::new(0..=22);
    sum += scaled(&q, -10);
    post(s, sum, Comparator::Equal, 0)?;

    let mut out = Out::new();
    out.put("isbn", &d);
    Ok(out)
}
