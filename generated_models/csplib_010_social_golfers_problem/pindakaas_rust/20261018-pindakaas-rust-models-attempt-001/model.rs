// Social golfers problem (CSPLib 010).
// The club has n_groups * group_size golfers. Each golfer plays once a week, in groups of
// group_size, for n_weeks weeks. No golfer plays in the same group as any other golfer
// on more than one occasion.
// assign[i][j] is the group (0-based) of golfer i in week j.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let g = inst.int("n_groups");
    let size = inst.int("group_size");
    let n = (g * size) as usize;
    let n_weeks = inst.int("n_weeks") as usize;
    let gu = g as usize;

    // assign[i][j]: the group of golfer i in week j
    let mut assign: Vec<Vec<IntVar>> = Vec::with_capacity(n);
    for _ in 0..n {
        let row: Vec<IntVar> = (0..n_weeks).map(|_| IntVar::new(0..=g - 1)).collect();
        assign.push(row);
    }

    // at[i][w][k]: golfer i is in group k in week w
    let mut at: Vec<Vec<Vec<Lit>>> = vec![vec![Vec::with_capacity(gu); n_weeks]; n];
    for i in 0..n {
        for w in 0..n_weeks {
            for k in 0..gu {
                let b = assign[i][w].equals(s, k as i64)?;
                let l = lit_of(s, b)?;
                at[i][w].push(l);
            }
        }
    }

    // Each week the golfers are divided into groups of group_size golfers
    for w in 0..n_weeks {
        for k in 0..gu {
            let mut e = LinExp::default();
            for i in 0..n {
                e += bx(BoolVal::Lit(at[i][w][k]));
            }
            post(s, e, Comparator::Equal, size)?;
        }
    }

    // No golfer plays in the same group as any other golfer on more than one occasion.
    // t is true in week w when golfers i and j share a group that week (sharing implies t).
    // At most one week may have t true for each pair.
    for i in 0..n {
        for j in (i + 1)..n {
            let mut e = LinExp::default();
            for w in 0..n_weeks {
                let t = s.new_lit();
                for k in 0..gu {
                    s.add_clause([!at[i][w][k], !at[j][w][k], t])?;
                }
                e += bx(BoolVal::Lit(t));
            }
            post(s, e, Comparator::LessEq, 1)?;
        }
    }

    let mut out = Out::new();
    out.put("assign", &assign);
    Ok(out)
}
