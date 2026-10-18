// csplib 011: 1997/98 ACC basketball schedule, a double round robin over 18 dates for 9 teams.
// Teams are indexed in the order of the description: Clemson 0, Duke 1, FSU 2, GT 3, UMD 4,
// UNC 5, NCSt 6, UVA 7, Wake 8. Dates are 0-based here: date k of the description is index k-1.
// config[d][i] is the opponent of team i on date d (i itself on a bye);
// where[d][i] is 0 for home, 1 for a bye, 2 for away.

const CLEM: usize = 0;
const DUKE: usize = 1;
const FSU: usize = 2;
const GT: usize = 3;
const UMD: usize = 4;
const UNC: usize = 5;
const NCST: usize = 6;
const UVA: usize = 7;
const WAKE: usize = 8;

// Literal true iff x == v.
fn eq_b(m: &mut Model, x: View<i64>, v: usize) -> View<bool> {
    m.linear(x).eq(v as i64).reify()
}

fn sum_b(xs: &[View<bool>]) -> IntLinearExp {
    xs.iter().copied().sum::<IntLinearExp>()
}

// Literal true iff a and b are both true.
fn and_b(m: &mut Model, a: View<bool>, b: View<bool>) -> View<bool> {
    m.linear(sum_b(&[a, b])).eq(2).reify()
}

// The rival of each team, if it has one (FSU has none).
fn rival(i: usize) -> Option<usize> {
    match i {
        CLEM => Some(GT),
        DUKE => Some(UNC),
        GT => Some(CLEM),
        UMD => Some(UVA),
        UNC => Some(DUKE),
        NCST => Some(WAKE),
        UVA => Some(UMD),
        WAKE => Some(NCST),
        _ => None,
    }
}

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n_teams");
    let days = inst.size("n_days");
    assert!(n == 9 && days == 18, "the description fixes 9 teams and 18 dates");

    // Decision variables: opponent and venue of each team on each date.
    let mut opp: Vec<Vec<View<i64>>> = Vec::with_capacity(days);
    let mut wh: Vec<Vec<View<i64>>> = Vec::with_capacity(days);
    for _ in 0..days {
        let mut orow = Vec::with_capacity(n);
        let mut wrow = Vec::with_capacity(n);
        for _ in 0..n {
            orow.push(m.new_int_decision(0..=(n as i64 - 1)));
            wrow.push(m.new_int_decision(0..=2));
        }
        opp.push(orow);
        wh.push(wrow);
    }

    // Literals: eqo[d][i][j] = team i plays j on date d (j == i is a bye),
    // hm / aw / by = team i is at home / away / on a bye on date d.
    let mut eqo: Vec<Vec<Vec<View<bool>>>> = Vec::with_capacity(days);
    let mut hm: Vec<Vec<View<bool>>> = Vec::with_capacity(days);
    let mut aw: Vec<Vec<View<bool>>> = Vec::with_capacity(days);
    let mut by: Vec<Vec<View<bool>>> = Vec::with_capacity(days);
    for d in 0..days {
        let mut erow = Vec::with_capacity(n);
        let mut hrow = Vec::with_capacity(n);
        let mut arow = Vec::with_capacity(n);
        let mut brow = Vec::with_capacity(n);
        for i in 0..n {
            let mut evec = Vec::with_capacity(n);
            for j in 0..n {
                evec.push(eq_b(m, opp[d][i], j));
            }
            erow.push(evec);
            hrow.push(eq_b(m, wh[d][i], 0));
            arow.push(eq_b(m, wh[d][i], 2));
            brow.push(eq_b(m, wh[d][i], 1));
        }
        eqo.push(erow);
        hm.push(hrow);
        aw.push(arow);
        by.push(brow);
    }

    // Each team meets each opponent, one game per date, and the two sides agree on the game.
    // The venue of a game is opposite for the two teams, and a bye is the team's own index.
    for d in 0..days {
        for i in 0..n {
            for j in 0..n {
                if j == i {
                    continue;
                }
                let g = eqo[d][i][j];
                m.linear(opp[d][j]).eq(i as i64).implied_by(g).post()?;
                m.linear(wh[d][i] + wh[d][j]).eq(2).implied_by(g).post()?;
            }
            m.linear(wh[d][i]).eq(1).reified_by(eqo[d][i][i]).post()?;
        }
    }

    // Double round-robin: each team plays each other once at home, once away.
    for i in 0..n {
        for j in 0..n {
            if j == i {
                continue;
            }
            let games: Vec<View<bool>> = (0..days).map(|d| eqo[d][i][j]).collect();
            m.linear(sum_b(&games)).eq(2).post()?;
            let mut homes = Vec::with_capacity(days);
            for d in 0..days {
                homes.push(and_b(m, eqo[d][i][j], hm[d][i]));
            }
            m.linear(sum_b(&homes)).eq(1).post()?;
        }
    }

    // 1. Mirroring. The dates are grouped into pairs (r1, r2), such that each team will get
    // to play against the same team in dates r1 and r2. Pairs in 0-based dates:
    // (1,8), (2,9), (3,12), (4,13), (5,14), (6,15), (7,16), (10,17), (11,18) in 1-based dates.
    const MIRROR: [(usize, usize); 9] = [
        (0, 7),
        (1, 8),
        (2, 11),
        (3, 12),
        (4, 13),
        (5, 14),
        (6, 15),
        (9, 16),
        (10, 17),
    ];
    for &(r1, r2) in MIRROR.iter() {
        for i in 0..n {
            m.linear(opp[r1][i] - opp[r2][i]).le(0).post()?;
            m.linear(opp[r1][i] - opp[r2][i]).ge(0).post()?;
        }
    }

    // 2. No Two Final Aways. No team can play away on both last dates.
    for i in 0..n {
        m.linear(sum_b(&[aw[days - 2][i], aw[days - 1][i]])).le(1).post()?;
    }

    // 3. Home/Away/Bye Pattern Constraints. No team may have more than two away matches in a row.
    // No team may have more than two home matches in a row. No team may have more than three
    // away matches or byes in a row (no home match in four dates). No team may have more than
    // four home matches or byes in a row (at least one away match in five dates).
    for i in 0..n {
        for d in 0..=(days - 3) {
            m.linear(sum_b(&[aw[d][i], aw[d + 1][i], aw[d + 2][i]])).le(2).post()?;
            m.linear(sum_b(&[hm[d][i], hm[d + 1][i], hm[d + 2][i]])).le(2).post()?;
        }
        for d in 0..=(days - 4) {
            m.linear(sum_b(&[hm[d][i], hm[d + 1][i], hm[d + 2][i], hm[d + 3][i]])).ge(1).post()?;
        }
        for d in 0..=(days - 5) {
            let w: Vec<View<bool>> = (d..d + 5).map(|k| aw[k][i]).collect();
            m.linear(sum_b(&w)).ge(1).post()?;
        }
    }

    // The weekends are the second and all subsequent even dates: 0-based 1, 3, ..., 17.
    let weekends: Vec<usize> = (1..days).step_by(2).collect();

    // 4. Weekend Pattern. Of the weekends, each team plays four at home, four away, and one bye.
    for i in 0..n {
        let h: Vec<View<bool>> = weekends.iter().map(|&d| hm[d][i]).collect();
        let a: Vec<View<bool>> = weekends.iter().map(|&d| aw[d][i]).collect();
        let b: Vec<View<bool>> = weekends.iter().map(|&d| by[d][i]).collect();
        m.linear(sum_b(&h)).eq(4).post()?;
        m.linear(sum_b(&a)).eq(4).post()?;
        m.linear(sum_b(&b)).eq(1).post()?;
    }

    // 5. First Weekends. Each team must have home matches or byes at least on two of the first
    // five weekends. A weekend that is not away is a home match or a bye.
    for i in 0..n {
        let early: Vec<View<bool>> = weekends[..5].iter().map(|&d| aw[d][i]).collect();
        m.linear(sum_b(&early)).le(3).post()?;
    }

    // 6. Rival Matches. Every team except FSU has a traditional rival. In the last date, every
    // team except FSU plays against its rival, unless it plays against FSU or has a bye.
    for i in 0..n {
        if let Some(r) = rival(i) {
            m.proposition(
                BoolFormula::Atom(eqo[days - 1][i][r])
                    | BoolFormula::Atom(eqo[days - 1][i][FSU])
                    | BoolFormula::Atom(eqo[days - 1][i][i]),
            )
            .post()?;
        }
    }

    // 7. Constrained Matches. The following pairings must occur at least once in dates 11 to 18:
    // Wake-UNC, Wake-Duke, GT-UNC, and GT-Duke.
    for &(i, j) in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)].iter() {
        let meets: Vec<View<bool>> = (10..days).map(|d| eqo[d][i][j]).collect();
        m.linear(sum_b(&meets)).ge(1).post()?;
    }

    // 8. Opponent Sequence Constraints. No team plays in two consecutive dates away against UNC
    // and Duke. No team plays in three consecutive dates against UNC, Duke and Wake
    // (independent of home/away).
    for i in 0..n {
        for d in 0..(days - 1) {
            for &(x, y) in [(UNC, DUKE), (DUKE, UNC)].iter() {
                if x == i || y == i {
                    continue;
                }
                let first = and_b(m, aw[d][i], eqo[d][i][x]);
                let second = and_b(m, aw[d + 1][i], eqo[d + 1][i][y]);
                m.linear(sum_b(&[first, second])).le(1).post()?;
            }
        }
        const ORDERS: [[usize; 3]; 6] = [
            [UNC, DUKE, WAKE],
            [UNC, WAKE, DUKE],
            [DUKE, UNC, WAKE],
            [DUKE, WAKE, UNC],
            [WAKE, UNC, DUKE],
            [WAKE, DUKE, UNC],
        ];
        for d in 0..(days - 2) {
            for order in ORDERS.iter() {
                if order.contains(&i) {
                    continue;
                }
                let seq = [
                    eqo[d][i][order[0]],
                    eqo[d + 1][i][order[1]],
                    eqo[d + 2][i][order[2]],
                ];
                m.linear(sum_b(&seq)).le(2).post()?;
            }
        }
    }

    // 9. Other Constraints. UNC plays its rival Duke in the last date, and in date 11.
    // UNC plays Clem in the second date.
    m.linear(opp[days - 1][UNC]).eq(DUKE as i64).post()?;
    m.linear(opp[10][UNC]).eq(DUKE as i64).post()?;
    m.linear(opp[1][UNC]).eq(CLEM as i64).post()?;
    // Duke has a bye in date 16.
    m.linear(wh[15][DUKE]).eq(1).post()?;
    // Wake does not play home in date 17.
    m.linear(wh[16][WAKE]).ne(0).post()?;
    // Wake has a bye in the first date.
    m.linear(wh[0][WAKE]).eq(1).post()?;
    // Clem, Duke, UMD and Wake do not play away in the last date.
    for &t in [CLEM, DUKE, UMD, WAKE].iter() {
        m.linear(wh[days - 1][t]).ne(2).post()?;
    }
    // Clem, FSU, GT and Wake do not play away in the first date.
    for &t in [CLEM, FSU, GT, WAKE].iter() {
        m.linear(wh[0][t]).ne(2).post()?;
    }
    // Neither FSU nor NCSt have a bye in the last date.
    for &t in [FSU, NCST].iter() {
        m.linear(wh[days - 1][t]).ne(1).post()?;
    }
    // UNC does not have a bye in the first date.
    m.linear(wh[0][UNC]).ne(1).post()?;

    let mut out = Out::new();
    out.put("config", opp).put("where", wh);
    Ok(out)
}
