// Appointment scheduling: assign 4 people to 4 interview slots from their free-busy schedules.
// m[i][j] is true when person i is free in slot j. x[i][j] is true when person i is assigned to slot j.
// Schedule every person into exactly one slot.
// Every slot takes exactly one person.
// A person is assigned only to a slot they are free in.
fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let free = inst.matrix("m");
    let n = free.len();

    let x: Vec<Vec<View<bool>>> = (0..n)
        .map(|_| (0..n).map(|_| m.new_bool_decision()).collect())
        .collect();

    // Schedule every person into exactly one slot.
    for i in 0..n {
        m.linear(x[i].iter().copied().sum::<IntLinearExp>()).eq(1).post()?;
    }

    // Every slot takes exactly one person.
    for j in 0..n {
        m.linear((0..n).map(|i| x[i][j]).sum::<IntLinearExp>()).eq(1).post()?;
    }

    // A person is assigned only to a slot they are free in.
    for i in 0..n {
        for j in 0..n {
            if free[i][j] == 0 {
                m.proposition(BoolFormula::Atom(!x[i][j])).post()?;
            }
        }
    }

    let mut out = Out::new();
    out.put("x", x);
    Ok(out)
}
