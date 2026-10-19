// Problem: divisible_by_1_through_9. Find a 10 digit number that uses each of the
// digits 0 to 9 exactly once and where the number formed by the first n digits of
// the number is divisible by n. Print the number (number).

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // Find a 10 digit number that uses each of the digits 0 to 9 exactly once.
    // The leading digit of a 10 digit number is not zero.
    let mut d: Vec<IntVar> = Vec::new();
    for i in 0..10 {
        let lo: i64 = if i == 0 { 1 } else { 0 };
        d.push(IntVar::new(lo..=9));
    }
    all_different(s, &d)?;

    // The number is the digits read from left to right.
    let mut e = LinExp::default();
    let mut place: i64 = 1_000_000_000;
    for x in &d {
        e += scaled(x, place);
        place /= 10;
    }
    let number = define(s, e)?;

    // The number formed by the first n digits of the number is divisible by n, for n = 1 to 9.
    // The prefix value itself is not held in a variable: its remainder modulo n is tracked
    // digit by digit, R_k = (10 * R_(k-1) + d_(k-1)) mod n, and R_n must be 0.
    for n in 1..=9i64 {
        let mut prev: Option<IntVar> = None;
        for k in 1..=(n as usize) {
            let t = match &prev {
                None => d[k - 1].clone(),
                Some(r) => {
                    let mut e = scaled(r, 10);
                    e += iv(&d[k - 1]);
                    define(s, e)?
                }
            };
            let r = IntVar::new(0..=(n - 1));
            mod_const(s, &t, n, &r)?;
            prev = Some(r);
        }
        if let Some(r) = &prev {
            post(s, iv(r), Comparator::Equal, 0)?;
        }
    }

    let mut out = Out::new();
    out.put("number", &number);
    Ok(out)
}
