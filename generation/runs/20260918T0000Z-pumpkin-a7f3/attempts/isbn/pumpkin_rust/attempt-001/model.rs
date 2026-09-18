// Fill the unknown digits of an ISBN-13 so the check digit is right.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let given = inst.ints("isbn_init");
    let n = given.len();

    let isbn = cp.ints(n, 0, 9);
    for i in 0..n {
        // -1 marks a digit that is not known.
        if given[i] != -1 {
            cp.eq(vec![t(isbn[i])], given[i]);
        }
    }
    // Every ISBN-13 starts 978 or 979.
    cp.eq(vec![t(isbn[0])], 9);
    cp.eq(vec![t(isbn[1])], 7);
    let eight = cp.is(isbn[2], 8);
    let nine = cp.is(isbn[2], 9);
    cp.any(vec![eight, nine]);

    // Weights alternate 1, 3 over the first twelve digits.
    let alternating: Vec<i32> = (0..n - 1).map(|i| if i % 2 == 0 { 1 } else { 3 }).collect();
    let body: Vec<Var> = isbn[..n - 1].to_vec();
    let weighted_sum = cp.sum(weighted(&alternating, &body));

    // check == (10 - weighted_sum % 10) % 10, which is exactly
    // (check + weighted_sum) % 10 == 0. Pumpkin has no modulo, so the remainder
    // is introduced explicitly.
    let ceiling = cp.upper_bound(weighted_sum);
    let quotient = cp.int(0, ceiling / 10);
    let remainder = cp.int(0, 9);
    cp.eq(vec![t(weighted_sum), c(-10, quotient), c(-1, remainder)], 0);
    let combined = cp.sum(vec![t(isbn[n - 1]), t(remainder)]);
    let none = cp.is(combined, 0);
    let ten = cp.is(combined, 10);
    cp.any(vec![none, ten]);

    let mut m = Model::new();
    m.put("isbn", isbn);
    m
}
