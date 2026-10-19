// Devil's word: given an array of integers, insert '+' or '-' operators before each
// integer in the array so that summing them up will result in total.
// Output result: the array with the correct signs.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let arr = inst.ints("arr");
    let total = inst.int("total");
    let n = arr.len();

    // insert '+' or '-' operators before each integer in the array
    // Each position i has a sign literal (true = plus). The signed value r_i is -a_i or a_i,
    // and each sign is a conditional equality through the safe post_if helper.
    let mut rs: Vec<IntVar> = Vec::with_capacity(n);
    for i in 0..n {
        let a = arr[i].abs();
        let plus = s.new_lit();
        let r = IntVar::new(-a..=a);
        post_if(s, &[plus], iv(&r), Comparator::Equal, a)?;
        post_if(s, &[!plus], iv(&r), Comparator::Equal, -a)?;
        rs.push(r);
    }

    // so that summing them up will result in total
    let mut sum = LinExp::default();
    for r in &rs {
        sum += iv(r);
    }
    post(s, sum, Comparator::Equal, total)?;

    let mut out = Out::new();
    out.put("result", &rs);
    Ok(out)
}
