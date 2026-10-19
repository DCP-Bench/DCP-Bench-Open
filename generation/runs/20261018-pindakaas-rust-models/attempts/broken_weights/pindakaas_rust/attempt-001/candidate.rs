// Broken weights: a measuring weight of m pounds broke into n pieces. Each piece
// weighs a whole number of pounds, and the pieces together weigh the total m.
// The pieces can weigh every whole number from 1 to m on a balance: a piece
// goes on the object's side (+1), on the other side (-1), or off the scale (0).

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let m = inst.int("m");
    let n = inst.size("n");

    // The pieces are whole pounds, each at least 1 and at most m.
    let w: Vec<IntVar> = (0..n).map(|_| IntVar::new(1..=m)).collect();

    // The pieces together weigh the whole weight m.
    let mut total = LinExp::default();
    for x in &w {
        total += iv(x);
    }
    post(s, total, Comparator::Equal, m)?;

    // The pieces could be used to weigh every integral weight between 1 and the total weight.
    for v in 1..=m {
        // Each piece contributes a signed weight a = c * w_i with c in {-1, 0, 1}.
        let mut sum = LinExp::default();
        for x in &w {
            let p = s.new_lit(); // piece on the object's side
            let q = s.new_lit(); // piece on the other side
            s.add_clause([!p, !q])?;
            let a = IntVar::new(-m..=m);
            post_if(s, &[p], iv(&a) - iv(x), Comparator::Equal, 0)?;
            post_if(s, &[q], iv(&a) + iv(x), Comparator::Equal, 0)?;
            post_if(s, &[!p, !q], iv(&a), Comparator::Equal, 0)?;
            sum += iv(&a);
        }
        // The signed pieces balance the weight v.
        post(s, sum, Comparator::Equal, v)?;
    }

    let mut out = Out::new();
    out.put("weights", &w);
    Ok(out)
}
