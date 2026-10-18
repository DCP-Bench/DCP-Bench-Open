// Sports tournament scheduling (CSPLib 026): n teams play over n-1 weeks.
// Each week has n/2 periods and two slots per period: the first team in a slot
// plays at home, the second plays away. Outputs home[w][p] and away[w][p]
// (teams numbered 1..n, weeks and periods 0-based in the arrays).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n_teams");
    let weeks = (n - 1) as usize;
    let periods = (n / 2) as usize;
    let nu = n as usize;

    // Every team plays once a week: the n slots of each week hold every team exactly once.
    let mut rows: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..weeks {
        let row = m.new_int_decisions(nu, 1..=n);
        m.unique(row.clone()).post()?;
        rows.push(row);
    }

    let mut home: Vec<Vec<View<i64>>> = Vec::new();
    let mut away: Vec<Vec<View<i64>>> = Vec::new();
    for row in &rows {
        home.push((0..periods).map(|p| row[2 * p]).collect());
        away.push((0..periods).map(|p| row[2 * p + 1]).collect());
    }

    // Every team plays every other team exactly once.
    // Each match (week, period) gets a code home * (n+1) + away; the code of an
    // ordered pair (i, j) is counted over all matches, and the two orders of a
    // pair together occur exactly once.
    let base = n + 1;
    let mut codes: Vec<View<i64>> = Vec::new();
    for w in 0..weeks {
        for p in 0..periods {
            let x = m.new_int_decision((base + 1)..=(n * base + n));
            m.linear(home[w][p] * base + away[w][p]).eq(x).post()?;
            codes.push(x);
        }
    }
    for i in 1..=n {
        for j in (i + 1)..=n {
            let pair_count: IntLinearExp = codes
                .iter()
                .map(|x| x.eq(i * base + j))
                .chain(codes.iter().map(|x| x.eq(j * base + i)))
                .sum();
            m.linear(pair_count).eq(1).post()?;
        }
    }

    // Every team plays at most twice in the same period over the tournament.
    for t in 1..=n {
        for p in 0..periods {
            let xs: Vec<View<i64>> = (0..weeks)
                .flat_map(|w| [home[w][p], away[w][p]])
                .collect();
            m.linear(count_eq(&xs, t)).le(2).post()?;
        }
    }

    let mut out = Out::new();
    out.put("home", home).put("away", away);
    Ok(out)
}
