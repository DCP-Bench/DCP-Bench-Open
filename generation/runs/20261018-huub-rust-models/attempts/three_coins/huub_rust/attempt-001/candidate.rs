// Problem three_coins: three coins lie on a table in the order tails, heads,
// tails. In precisely three moves make them face either all heads or all tails.
// Each move consists of choosing one coin and flipping it over. Output steps:
// a list of lists of booleans, True meaning tails, one row per state, starting
// from the initial state.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let init = inst.ints("init");
    let moves = inst.size("num_moves");
    let coins = init.len();

    // state[t][i]: 1 if coin i shows tails after t moves, 0 if heads.
    let mut state: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..=moves {
        let mut row = Vec::new();
        for _ in 0..coins {
            row.push(m.new_int_decision(0..=1));
        }
        state.push(row);
    }

    // The initial state is the coins as the instance gives them, 1 = tails.
    for (i, &c) in init.iter().enumerate() {
        m.linear(IntLinearExp::from(state[0][i])).eq(i64::from(c == 1)).post()?;
    }

    // Each move chooses one coin and flips it over: exactly one coin differs
    // between consecutive states.
    for t in 0..moves {
        let mut diffs = Vec::new();
        for i in 0..coins {
            let d = m
                .linear(IntLinearExp::from(state[t][i]) - IntLinearExp::from(state[t + 1][i]))
                .ne(0)
                .reify();
            diffs.push(d);
        }
        m.linear(diffs.iter().copied().sum::<IntLinearExp>()).eq(1).post()?;
    }

    // Make them all face either all heads or all tails: the final state has
    // every coin showing the same face.
    let last = &state[moves];
    for i in 1..coins {
        m.linear(IntLinearExp::from(last[0]) - IntLinearExp::from(last[i])).eq(0).post()?;
    }

    // Report each state as booleans, True meaning tails.
    let mut steps: Vec<Vec<View<bool>>> = Vec::new();
    for row in &state {
        let mut out_row = Vec::new();
        for &x in row {
            out_row.push(m.linear(IntLinearExp::from(x)).eq(1).reify());
        }
        steps.push(out_row);
    }

    let mut out = Out::new();
    out.put("steps", steps);
    Ok(out)
}
