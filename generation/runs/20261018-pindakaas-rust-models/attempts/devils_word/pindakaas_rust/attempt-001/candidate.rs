// Devil's word: insert '+' or '-' before each integer of the array arr so that the
// signed sum equals total. Output result: the array with the chosen signs applied.

// Given an array of integers, insert '+' or '-' operators before each integer in the array so that summing them up will
// result in total.
// Print the array with the correct signs (result).

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let arr = inst.ints("arr");
    let total = inst.int("total");
    let n = arr.len();

    // Each position i has a sign literal (true = plus) and a signed value r_i in {-a_i, a_i}.
    // Each sign is a conditional equality, so no encoding narrows a variable on its own.
    let mut rs: Vec<IntVar> = Vec::with_capacity(n);
    for i in 0..n {
        let a = arr[i].abs();
        let plus = s.new_lit();
        let r = IntVar::new(-a..=a);
        post_if(s, &[plus], iv(&r), Comparator::Equal, a)?;
        post_if(s, &[!plus], iv(&r), Comparator::Equal, -a)?;
        rs.push(r);
    }

    // The signed values sum to total.
    // The sum of the signed values equals total.
    let mut sum = LinExp::default();
    for r in &rs {
        sum += iv(r);
    }
    post(s, sum, Comparator::Equal, total)?;

    let mut out = Out::new();
    out.put("result", &rs);
    Ok(out)
}
