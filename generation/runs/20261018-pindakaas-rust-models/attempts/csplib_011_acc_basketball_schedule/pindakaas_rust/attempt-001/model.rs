// CSPLib 011: 1997/98 Atlantic Coast Conference basketball timetable. A double round-robin
// schedule for 9 teams over 18 dates, with the mirroring scheme, home/away/bye pattern
// constraints, weekend pattern, first-weekend, rival, constrained-match, opponent-sequence
// and other constraints of the description.
// Teams (0-based): 0 Clemson, 1 Duke, 2 FSU, 3 GT, 4 UMD, 5 UNC, 6 NCSt, 7 UVA, 8 Wake.
// Dates are 0-based here: date k of the description is day k-1. Weekends are the even
// dates of the description (odd day indices 1, 3, ..., 17).
// Outputs: where[d][i] is 0 home, 1 bye, 2 away; config[d][i] is the opponent of team i
// on day d, and i itself on a bye.

const FSU: usize = 2;

fn sum_lits(ls: &[Lit]) -> LinExp {
    let mut e = LinExp::default();
    for &l in ls {
        e += LinExp::from(l);
    }
    e
}

// A literal equal to the disjunction of `ls`.
fn or_lit(s: &mut Cadical, ls: &[Lit]) -> Res<Lit> {
    let p = s.new_lit();
    for &l in ls {
        s.add_clause([!l, p])?;
    }
    let mut c = vec![!p];
    c.extend_from_slice(ls);
    s.add_clause(c)?;
    Ok(p)
}

// Games team i hosts on day d (the literals h[d][i][j] for j != i).
fn home(h: &[Vec<Vec<Lit>>], d: usize, i: usize) -> Vec<Lit> {
    (0..h[d].len()).filter(|&j| j != i).map(|j| h[d][i][j]).collect()
}

// Games team i plays away on day d (the literals h[d][j][i] for j != i).
fn away(h: &[Vec<Vec<Lit>>], d: usize, i: usize) -> Vec<Lit> {
    (0..h[d].len()).filter(|&j| j != i).map(|j| h[d][j][i]).collect()
}

// Every game team i plays on day d, at home or away.
fn played(h: &[Vec<Vec<Lit>>], d: usize, i: usize) -> Vec<Lit> {
    let mut v = home(h, d, i);
    v.extend(away(h, d, i));
    v
}

// The games between i and j on day d, either venue.
fn pair(h: &[Vec<Vec<Lit>>], d: usize, i: usize, j: usize) -> Vec<Lit> {
    vec![h[d][i][j], h[d][j][i]]
}

fn rival(i: usize) -> Option<usize> {
    match i {
        0 => Some(3),
        3 => Some(0),
        1 => Some(5),
        5 => Some(1),
        6 => Some(8),
        8 => Some(6),
        4 => Some(7),
        7 => Some(4),
        _ => None,
    }
}

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n_teams");
    let days = inst.size("n_days");
    // The rules name these nine teams and the fixed dates below.
    assert!(n == 9 && days == 18, "the ACC rules need 9 teams and 18 dates");

    // h[d][i][j]: team i hosts team j on day d. The diagonal is never a game.
    let mut h: Vec<Vec<Vec<Lit>>> = Vec::new();
    for _ in 0..days {
        let mut day: Vec<Vec<Lit>> = Vec::new();
        for _ in 0..n {
            let row: Vec<Lit> = (0..n).map(|_| s.new_lit()).collect();
            day.push(row);
        }
        h.push(day);
    }
    for d in 0..days {
        for i in 0..n {
            s.add_clause([!h[d][i][i]])?;
        }
    }

    // Double round robin: each team plays each other, once at home and once away.
    for i in 0..n {
        for j in 0..n {
            if i != j {
                let hs: Vec<Lit> = (0..days).map(|d| h[d][i][j]).collect();
                post(s, sum_lits(&hs), Comparator::Equal, 1)?;
            }
        }
    }

    // A team plays at most one game a day.
    for d in 0..days {
        for i in 0..n {
            post(s, sum_lits(&played(&h, d, i)), Comparator::LessEq, 1)?;
        }
    }

    // Mirroring. The dates are grouped into pairs (r1, r2), such that each team will get to
    // play against the same team in dates r1 and r2. Nemhauser and Trick use the scheme
    // {(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)}.
    const MIRROR: [(usize, usize); 9] =
        [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)];
    for (a, b) in MIRROR {
        let (r1, r2) = (a - 1, b - 1);
        for i in 0..n {
            for j in 0..n {
                if i != j {
                    let e = sum_lits(&pair(&h, r1, i, j)) - sum_lits(&pair(&h, r2, i, j));
                    post(s, e, Comparator::Equal, 0)?;
                }
            }
        }
    }

    // No Two Final Aways. No team can play away on both last dates.
    for i in 0..n {
        let mut aw = away(&h, days - 2, i);
        aw.extend(away(&h, days - 1, i));
        post(s, sum_lits(&aw), Comparator::LessEq, 1)?;
    }

    // Home/Away/Bye Pattern Constraints. No team may have more than two away matches in a
    // row. No team may have more than two home matches in a row. No team may have more than
    // three away matches or byes in a row (so every four days contain a home match). No team
    // may have more than four home matches or byes in a row (so every five days contain an
    // away match).
    for i in 0..n {
        for d in 0..=days - 3 {
            let aw: Vec<Lit> = (d..d + 3).flat_map(|k| away(&h, k, i)).collect();
            post(s, sum_lits(&aw), Comparator::LessEq, 2)?;
            let hm: Vec<Lit> = (d..d + 3).flat_map(|k| home(&h, k, i)).collect();
            post(s, sum_lits(&hm), Comparator::LessEq, 2)?;
        }
        for d in 0..=days - 4 {
            let hm: Vec<Lit> = (d..d + 4).flat_map(|k| home(&h, k, i)).collect();
            post(s, sum_lits(&hm), Comparator::GreaterEq, 1)?;
        }
        for d in 0..=days - 5 {
            let aw: Vec<Lit> = (d..d + 5).flat_map(|k| away(&h, k, i)).collect();
            post(s, sum_lits(&aw), Comparator::GreaterEq, 1)?;
        }
    }

    // Weekend Pattern. Of the weekends, each team plays four at home, four away, and one bye.
    let weekends: Vec<usize> = (1..days).step_by(2).collect();
    for i in 0..n {
        let hm: Vec<Lit> = weekends.iter().flat_map(|&d| home(&h, d, i)).collect();
        post(s, sum_lits(&hm), Comparator::Equal, 4)?;
        let aw: Vec<Lit> = weekends.iter().flat_map(|&d| away(&h, d, i)).collect();
        post(s, sum_lits(&aw), Comparator::Equal, 4)?;
    }

    // First Weekends. Each team must have home matches or byes at least on two of the first
    // five weekends, that is, away on at most three of them.
    for i in 0..n {
        let aw: Vec<Lit> = weekends[..5].iter().flat_map(|&d| away(&h, d, i)).collect();
        post(s, sum_lits(&aw), Comparator::LessEq, 3)?;
    }

    // Rival Matches. Every team except FSU has a traditional rival. In the last date, every
    // team except FSU plays against its rival, unless it plays against FSU or has a bye.
    for i in 0..n {
        if i == FSU {
            continue;
        }
        let r = rival(i).expect("every team but FSU has a rival");
        for j in 0..n {
            if j != i && j != r && j != FSU {
                for l in pair(&h, days - 1, i, j) {
                    s.add_clause([!l])?;
                }
            }
        }
    }

    // Constrained Matches. The following pairings must occur at least once in dates 11 to
    // 18: Wake-UNC, Wake-Duke, GT-UNC, and GT-Duke.
    for (a, b) in [(8, 5), (8, 1), (3, 5), (3, 1)] {
        let ls: Vec<Lit> = (10..days).flat_map(|d| pair(&h, d, a, b)).collect();
        s.add_clause(ls)?;
    }

    // Opponent Sequence Constraints. No team plays in two consecutive dates away against
    // UNC and Duke. No team plays in three consecutive dates against UNC, Duke and Wake
    // (independent of home/away).
    for i in 0..n {
        for d in 0..days - 1 {
            for (x, y) in [(5, 1), (1, 5)] {
                s.add_clause([!h[d][x][i], !h[d + 1][y][i]])?;
            }
        }
        const PERMS: [[usize; 3]; 6] =
            [[5, 1, 8], [5, 8, 1], [1, 5, 8], [1, 8, 5], [8, 5, 1], [8, 1, 5]];
        for d in 0..days - 2 {
            for p in PERMS {
                for &a in &pair(&h, d, i, p[0]) {
                    for &b in &pair(&h, d + 1, i, p[1]) {
                        for &c in &pair(&h, d + 2, i, p[2]) {
                            s.add_clause([!a, !b, !c])?;
                        }
                    }
                }
            }
        }
    }

    // Other Constraints. UNC plays its rival Duke in the last date, and in date 11. UNC plays
    // Clem in the second date.
    s.add_clause(pair(&h, days - 1, 5, 1))?;
    s.add_clause(pair(&h, 10, 5, 1))?;
    s.add_clause(pair(&h, 1, 5, 0))?;
    // Duke has a bye in date 16.
    for l in played(&h, 15, 1) {
        s.add_clause([!l])?;
    }
    // Wake does not play home in date 17.
    for l in home(&h, 16, 8) {
        s.add_clause([!l])?;
    }
    // Wake has a bye in the first date.
    for l in played(&h, 0, 8) {
        s.add_clause([!l])?;
    }
    // Clem, Duke, UMD and Wake do not play away in the last date.
    for i in [0, 1, 4, 8] {
        for l in away(&h, days - 1, i) {
            s.add_clause([!l])?;
        }
    }
    // Clem, FSU, GT and Wake do not play away in the first date.
    for i in [0, 2, 3, 8] {
        for l in away(&h, 0, i) {
            s.add_clause([!l])?;
        }
    }
    // Neither FSU nor NCSt have a bye in the last date.
    for i in [FSU, 6] {
        s.add_clause(played(&h, days - 1, i))?;
    }
    // UNC does not have a bye in the first date.
    s.add_clause(played(&h, 0, 5))?;

    // Outputs. where[d][i]: 0 home, 1 bye, 2 away. config[d][i]: the opponent, or i on a bye.
    let mut where_rows: Vec<Vec<IntVar>> = Vec::new();
    let mut config_rows: Vec<Vec<IntVar>> = Vec::new();
    for d in 0..days {
        let mut wr: Vec<IntVar> = Vec::new();
        let mut cr: Vec<IntVar> = Vec::new();
        for i in 0..n {
            let wv = IntVar::new(0..=2);
            let cv = IntVar::new(0..=(n as i64 - 1));
            let hm = or_lit(s, &home(&h, d, i))?;
            let aw = or_lit(s, &away(&h, d, i))?;
            let pl = or_lit(s, &played(&h, d, i))?;

            let b0 = wv.equals(s, 0)?;
            let e0 = lit_of(s, b0)?;
            let b1 = wv.equals(s, 1)?;
            let e1 = lit_of(s, b1)?;
            let b2 = wv.equals(s, 2)?;
            let e2 = lit_of(s, b2)?;
            s.add_clause([!e0, hm])?;
            s.add_clause([!hm, e0])?;
            s.add_clause([!e2, aw])?;
            s.add_clause([!aw, e2])?;
            s.add_clause([!e1, !pl])?;
            s.add_clause([e1, pl])?;

            for j in 0..n {
                if j != i {
                    let bj = cv.equals(s, j as i64)?;
                    let ej = lit_of(s, bj)?;
                    s.add_clause([!h[d][i][j], ej])?;
                    s.add_clause([!h[d][j][i], ej])?;
                }
            }
            let bi = cv.equals(s, i as i64)?;
            let ei = lit_of(s, bi)?;
            s.add_clause([pl, ei])?;

            wr.push(wv);
            cr.push(cv);
        }
        where_rows.push(wr);
        config_rows.push(cr);
    }

    let mut out = Out::new();
    out.put("config", config_rows).put("where", where_rows);
    Ok(out)
}
