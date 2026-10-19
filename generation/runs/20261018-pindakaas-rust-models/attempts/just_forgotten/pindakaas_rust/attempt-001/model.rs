// Problem just_forgotten: Joe's account number x is a list of n integers that holds
// all the digits from 0 to n-1 in some order. For each set of digits, exactly
// num_correct_digits of the digits are in their correct position (equal to x at the
// same index). Output x.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let sets = inst.matrix("sets");
    let k = inst.int("num_correct_digits");
    let n = sets[0].len();

    // the account number has all the digits from 0 to n-1 in some order
    let x: Vec<IntVar> = (0..n).map(|_| IntVar::new(0..=(n as i64 - 1))).collect();
    all_different(s, &x)?;

    // in each set just a specific number of the digits were in their correct position
    for set in &sets {
        let mut e = LinExp::default();
        for i in 0..n {
            let b = x[i].equals(s, set[i])?;
            e += bx(b);
        }
        post(s, e, Comparator::Equal, k)?;
    }

    let mut out = Out::new();
    out.put("x", &x);
    Ok(out)
}
