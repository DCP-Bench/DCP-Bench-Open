// Problem: appointment_scheduling. Schedule 4 people into 4 interview slots based on
// their free-busy schedules. Output x[i][j] is true when person i is assigned to slot j.
// Instance field m[i][j] = 1 when person i is free in slot j, 0 when busy.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let m = inst.matrix("m");
    let people = m.len();
    let slots = m[0].len();

    // Boolean assignment variables x[i][j].
    let x: Vec<Vec<Lit>> = (0..people)
        .map(|_| (0..slots).map(|_| s.new_lit()).collect())
        .collect();

    // A person can only be assigned to a slot in which they are free.
    for i in 0..people {
        for j in 0..slots {
            if m[i][j] == 0 {
                s.add_clause([!x[i][j]])?;
            }
        }
    }

    // Each person is scheduled into exactly one slot.
    for i in 0..people {
        let mut e = LinExp::default();
        for j in 0..slots {
            e += LinExp::from(x[i][j]);
        }
        post(s, e, Comparator::Equal, 1)?;
    }

    // Each slot is taken by at most one person.
    for j in 0..slots {
        let mut e = LinExp::default();
        for i in 0..people {
            e += LinExp::from(x[i][j]);
        }
        post(s, e, Comparator::LessEq, 1)?;
    }

    let mut out = Out::new();
    out.put("x", &x);
    Ok(out)
}
