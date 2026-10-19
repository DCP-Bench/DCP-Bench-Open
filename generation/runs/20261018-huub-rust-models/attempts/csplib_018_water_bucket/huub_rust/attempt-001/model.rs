// Water bucket (csplib 018): three buckets with capacities, start with the
// first one full, and reach the state where the first two buckets hold half
// of the water each. Each transfer pours from one bucket into another until
// the source is empty or the target is full. Minimise the number of transfers.
// The sequence lists the state before the first transfer, then the state
// after each transfer, and PADDING_VALUE rows after the goal state.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let caps = inst.ints("capacities");
    let init = inst.ints("initial_state");
    let goal = inst.ints("goal_state");
    let steps = inst.size("MAX_STEPS");
    let pad = inst.int("PADDING_VALUE");
    let nb = caps.len();

    // The number of transfers, at most one less than the number of rows.
    let cost = m.new_int_decision(0..=(steps as i64 - 1));

    // state[t][j]: content of bucket j after t transfers.
    // Row 0 is the initial state, fixed by its domain.
    let mut state: Vec<Vec<View<i64>>> = Vec::new();
    let row0: Vec<View<i64>> = (0..nb).map(|j| m.new_int_decision(init[j]..=init[j])).collect();
    state.push(row0);
    for _ in 1..steps {
        let row: Vec<View<i64>> = (0..nb).map(|j| m.new_int_decision(0..=caps[j])).collect();
        state.push(row);
    }

    // Transfers: step k produces state k+1. Either a pour between two buckets
    // happens, or the step is a stay. Stays are exactly the steps from cost on.
    // A pour moves f = min(content of source, room in target) units.
    // The goal is reached at the end of the sequence; stays keep it there.
    for k in 0..steps - 1 {
        // The description says a transfer pours between buckets.
        // Exactly one option holds in each step.
        let mut options: Vec<View<bool>> = Vec::new();
        for i in 0..nb {
            for j in 0..nb {
                if i == j {
                    continue;
                }
                let p = m.new_bool_decision();
                options.push(p);
                // Room left in bucket j, and the amount poured.
                let room = m.new_int_decision(0..=caps[j]);
                m.linear(room + state[k][j]).eq(caps[j]).post()?;
                let f = m.new_int_decision(0..=caps[i]);
                m.minimum(vec![state[k][i], room]).result(f).post()?;
                // The pour moves f units from bucket i to bucket j.
                m.linear(state[k + 1][i] - state[k][i] + f).eq(0).implied_by(p).post()?;
                m.linear(state[k + 1][j] - state[k][j] - f).eq(0).implied_by(p).post()?;
                for l in 0..nb {
                    if l != i && l != j {
                        m.linear(state[k + 1][l] - state[k][l]).eq(0).implied_by(p).post()?;
                    }
                }
            }
        }
        // A stay leaves all buckets unchanged. It happens exactly from step cost on.
        let st = m.new_bool_decision();
        options.push(st);
        for j in 0..nb {
            m.linear(state[k + 1][j] - state[k][j]).eq(0).implied_by(st).post()?;
        }
        m.linear(cost).le(k as i64).reified_by(st).post()?;
        m.linear(options.iter().copied().sum::<IntLinearExp>()).eq(1).post()?;
    }

    // The goal state is the state at the end of the sequence.
    for j in 0..nb {
        m.linear(state[steps - 1][j]).eq(goal[j]).post()?;
    }

    // Output rows. Row t holds the state after t transfers while t <= cost,
    // and PADDING_VALUE rows after the goal state.
    let mut rows: Vec<Vec<View<i64>>> = Vec::new();
    rows.push(state[0].clone());
    for t in 1..steps {
        let live = m.new_bool_decision();
        m.linear(cost).ge(t as i64).reified_by(live).post()?;
        let dead = m.new_bool_decision();
        m.linear(cost).le(t as i64 - 1).reified_by(dead).post()?;
        let mut row: Vec<View<i64>> = Vec::new();
        for j in 0..nb {
            let o = m.new_int_decision(pad..=caps[j]);
            m.linear(o - state[t][j]).eq(0).implied_by(live).post()?;
            m.linear(o).eq(pad).implied_by(dead).post()?;
            row.push(o);
        }
        rows.push(row);
    }

    let mut out = Out::new();
    out.put("cost", cost).put("sequence", rows);
    out.minimise(cost);
    Ok(out)
}
