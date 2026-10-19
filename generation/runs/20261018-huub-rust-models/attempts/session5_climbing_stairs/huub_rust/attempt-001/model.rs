// Climbing stairs: climb a stair of n steps, taking between m1 and m2 steps per move.
// Output steps[i] is the number of steps taken at move i: a value in m1..=m2,
// or 0 when no steps are taken, i.e. after the top is reached.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let m1 = inst.int("m1");
    let m2 = inst.int("m2");
    let len = inst.size("n");

    let mut steps: Vec<View<i64>> = Vec::new();
    for _ in 0..len {
        steps.push(m.new_int_decision(0..=m2));
    }
    let mut moved: Vec<View<bool>> = Vec::new();
    for _ in 0..len {
        moved.push(m.new_bool_decision());
    }

    // A move takes between m1 and m2 steps, or none (0 steps).
    for i in 0..len {
        m.linear(steps[i]).ge(1).reified_by(moved[i]).post()?;
        m.linear(steps[i]).ge(m1).implied_by(moved[i]).post()?;
        m.linear(steps[i]).le(m2).implied_by(moved[i]).post()?;
    }

    // Once a move takes no steps, every later move takes no steps.
    for i in 0..len.saturating_sub(1) {
        m.linear(steps[i]).ge(1).implied_by(moved[i + 1]).post()?;
    }

    // The moves together reach the top exactly.
    m.linear(steps.iter().copied().sum::<IntLinearExp>()).eq(n).post()?;

    let mut out = Out::new();
    out.put("steps", steps);
    Ok(out)
}
