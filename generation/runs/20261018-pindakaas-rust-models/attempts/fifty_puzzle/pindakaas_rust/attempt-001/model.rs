// Fifty puzzle (side show with dummies): choose which dummies to knock over with
// baseballs so that the numbers on the dummies knocked over sum to exactly the
// target sum. Output: dummies, one Boolean per dummy (true = knocked over).

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let vals = inst.ints("values");
    let target = inst.int("target_sum");

    // Each dummy is knocked over or not.
    let bs: Vec<Lit> = (0..vals.len()).map(|_| s.new_lit()).collect();

    // The numbers on the dummies knocked over add up to exactly the target sum,
    // neither more nor less.
    let mut e = LinExp::default();
    for (b, v) in bs.iter().zip(vals.iter()) {
        e += b.clone() * *v;
    }
    post(s, e, Comparator::Equal, target)?;

    let mut out = Out::new();
    out.put("dummies", &bs);
    Ok(out)
}
