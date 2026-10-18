// ISBN-13 validation and check digit calculation.
// Given 13 integers where -1 is an unknown digit, find the unknown digits so that the
// result is a valid ISBN-13. The output isbn is the complete list of 13 digits.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let init = inst.ints("isbn_init");

    // Each digit is 0..=9; a given digit is fixed to its value.
    let mut isbn: Vec<View<i64>> = Vec::new();
    for i in 0..init.len() {
        let d = m.new_int_decision(0..=9);
        if init[i] >= 0 {
            m.linear(d).eq(init[i]).post()?;
        }
        isbn.push(d);
    }

    // An ISBN-13 must start with 978 or 979.
    m.linear(isbn[0]).eq(9).post()?;
    m.linear(isbn[1]).eq(7).post()?;
    m.linear(isbn[2]).ge(8).post()?;
    m.linear(isbn[2]).le(9).post()?;

    // Multiply the first 12 digits alternately by 1 and 3 (starting with 1).
    // Sum the products. The check digit is (10 - (sum % 10)) % 10.
    // Together with the check digit (weight 1), the weighted sum of all 13 digits
    // is a multiple of 10: weighted_sum == 10 * q.
    let weighted: IntLinearExp = isbn
        .iter()
        .enumerate()
        .map(|(i, d)| if i % 2 == 0 { *d * 1 } else { *d * 3 })
        .sum();
    let q = m.new_int_decision(0..=22);
    m.linear(weighted - q * 10).eq(0).post()?;

    let mut out = Out::new();
    out.put("isbn", isbn);
    Ok(out)
}
