// Problem: divisible_by_1_through_9. Find a 10 digit number that uses each of the
// digits 0 to 9 exactly once and where the number formed by the first n digits of the
// number is divisible by n. Print the number (number).
// Digits are read left to right: d[0] is the leading digit, d[k] the digit at position k+1.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // The number has 10 digits, so the leading digit is not 0. Each digit is 0..=9.
    let d: Vec<IntVar> = (0..10).map(|i| IntVar::new(if i == 0 { 1 } else { 0 }..=9)).collect();

    // Each of the digits 0 to 9 is used exactly once.
    all_different(s, &d)?;

    // The number formed by the first n digits of the number is divisible by n, for n = 2..10.
    // prefix is the number formed by the first n digits; q is a wide quotient with prefix = n * q.
    // (The n = 1 case is always true: every digit is divisible by 1.)
    for n in 2..=10usize {
        let mut prefix = LinExp::default();
        let mut place = 1i64;
        for k in (0..n).rev() {
            prefix += scaled(&d[k], place);
            place *= 10;
        }
        // place is now 10^n, so the prefix is at most 10^n - 1.
        let q = wide_int(s, 0, (place - 1) / n as i64)?;
        post_wide(s, prefix - q.exp() * n as i64, Comparator::Equal, 0)?;
    }

    // The number is the ten digits read left to right. It is held in bits because its
    // value reaches 10^10, which a plain integer variable cannot represent as an output.
    let number = wide_int(s, 0, 9_999_999_999)?;
    let mut value = LinExp::default();
    let mut place = 1i64;
    for k in (0..10).rev() {
        value += scaled(&d[k], place);
        place *= 10;
    }
    post_wide(s, number.exp() - value, Comparator::Equal, 0)?;

    let mut out = Out::new();
    out.put("number", &number);
    Ok(out)
}
