// Climbing stairs: a stair of n steps, climbed with moves of m1 to m2 steps at a time.
// steps[i] is the number of steps taken at move i (1-based in the description, 0-based here):
// it is between m1 and m2, or 0 when no steps are taken at that move, i.e. after the top is reached.
// The output has one entry per move, so its length is n.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.int("n");
    let m1 = inst.int("m1");
    let m2 = inst.int("m2");
    let len = inst.size("n");

    // Each move takes between m1 and m2 steps, or 0 when no steps are taken at that move.
    let steps: Vec<IntVar> = (0..len).map(|_| IntVar::new(0..=m2)).collect();
    let mut zero: Vec<Lit> = Vec::with_capacity(len);
    for x in &steps {
        let z = reify_eq(s, iv(x), 0)?;
        post_if(s, &[!z], iv(x), Comparator::GreaterEq, m1)?;
        zero.push(z);
    }

    // The moves climb the stair of n steps: the steps taken sum to n.
    let mut total = LinExp::default();
    for x in &steps {
        total += iv(x);
    }
    post(s, total, Comparator::Equal, n)?;

    // 0 is used only after reaching the top: once a move is 0, every later move is 0.
    for i in 0..len.saturating_sub(1) {
        s.add_clause([!zero[i], zero[i + 1]])?;
    }

    let mut out = Out::new();
    out.put("steps", &steps);
    Ok(out)
}
