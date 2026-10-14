// ACC basketball scheduling (CSPLib 011): a double round-robin timetable for the
// nine teams of the 1997/98 Atlantic Coast Conference over 18 dates, with
// mirroring, home/away/bye pattern, weekend, rival and opponent-sequence rules.
// config[d][i] == j: team i plays team j on date d (j == i is a bye).
// where[d][i]: 0 home, 1 bye, 2 away.
//
// n_teams and n_days come from the instance. The named teams, the mirroring
// scheme and the special rules (items 1-9) are the problem's own constants for
// these nine teams and 18 dates, mirrored from the reference.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n_teams = inst.size("n_teams");
    let n_days = inst.size("n_days");
    let last = n_days - 1;

    // Teams, in the reference's order.
    let (clem, duke, fsu, gt, umd, unc, ncst, uva, wake) = (0, 1, 2, 3, 4, 5, 6, 7, 8);
    let rivals = [gt, unc, fsu, clem, uva, duke, wake, umd, ncst];
    let (home, bye, away) = (0, 1, 2);
    let weekends: Vec<usize> = (0..n_days).filter(|d| d % 2 == 1).collect();

    let config: Vec<Vec<Var>> = (0..n_days)
        .map(|_| (0..n_teams).map(|_| solver.new_bounded_integer(0, n_teams as i32 - 1)).collect())
        .collect();
    let place: Vec<Vec<Var>> = (0..n_days)
        .map(|_| (0..n_teams).map(|_| solver.new_bounded_integer(0, 2)).collect())
        .collect();

    // vs[d][i][j]: team i meets team j on date d (vs[d][i][i] is a bye).
    let channel = solver.new_constraint_tag();
    let vs: Vec<Vec<Vec<Lit>>> = (0..n_days)
        .map(|d| {
            (0..n_teams)
                .map(|i| {
                    (0..n_teams)
                        .map(|j| {
                            let l = solver.new_literal();
                            solver
                                .add_constraint(pumpkin_solver::equals(vec![config[d][i]], j as i32, channel))
                                .reify(l);
                            l
                        })
                        .collect()
                })
                .collect()
        })
        .collect();
    // is_home / is_bye / is_away[d][i]: where[d][i] takes that value.
    let mut flags = |value: i32| -> Vec<Vec<Lit>> {
        (0..n_days)
            .map(|d| {
                (0..n_teams)
                    .map(|i| {
                        let l = solver.new_literal();
                        solver.add_constraint(pumpkin_solver::equals(vec![place[d][i]], value, channel)).reify(l);
                        l
                    })
                    .collect()
            })
            .collect()
    };
    let is_home = flags(home);
    let is_bye = flags(bye);
    let is_away = flags(away);

    // A team cannot have different opponents on the same date.
    let tag = solver.new_constraint_tag();
    for d in 0..n_days {
        solver.add_constraint(pumpkin_solver::all_different(config[d].clone(), tag)).post();
    }

    // If team i plays team j, then team j plays team i.
    let mutual = solver.new_constraint_tag();
    for d in 0..n_days {
        for i in 0..n_teams {
            for j in 0..n_teams {
                if i != j {
                    solver.add_constraint(pumpkin_solver::clause(vec![!vs[d][i][j], vs[d][j][i]], mutual)).post();
                }
            }
        }
    }

    // A team has a bye exactly when it is its own opponent; when two teams meet,
    // one plays at home and the other away.
    let home_away = solver.new_constraint_tag();
    for d in 0..n_days {
        for i in 0..n_teams {
            solver
                .add_constraint(pumpkin_solver::clause(vec![!is_bye[d][i], vs[d][i][i]], home_away))
                .post();
            solver
                .add_constraint(pumpkin_solver::clause(vec![is_bye[d][i], !vs[d][i][i]], home_away))
                .post();
            for j in 0..n_teams {
                if i == j {
                    continue;
                }
                let meet = vs[d][i][j];
                // i at home with j as opponent <-> j away; i away <-> j at home.
                for (mine, theirs) in [(is_home[d][i], is_away[d][j]), (is_away[d][i], is_home[d][j])] {
                    solver.add_constraint(pumpkin_solver::clause(vec![!meet, !mine, theirs], home_away)).post();
                    solver.add_constraint(pumpkin_solver::clause(vec![!meet, !theirs, mine], home_away)).post();
                }
            }
        }
    }

    // Double round-robin: each team plays each other team exactly once at home.
    // home_vs is the conjunction "i meets j on date d and i is at home".
    let round_robin = solver.new_constraint_tag();
    let one = solver.new_bounded_integer(1, 1);
    for i in 0..n_teams {
        for j in 0..n_teams {
            if i == j {
                continue;
            }
            let hosted: Vec<Lit> = (0..n_days)
                .map(|d| {
                    let both = solver.new_literal();
                    solver.add_constraint(pumpkin_solver::clause(vec![!both, vs[d][i][j]], round_robin)).post();
                    solver.add_constraint(pumpkin_solver::clause(vec![!both, is_home[d][i]], round_robin)).post();
                    solver
                        .add_constraint(pumpkin_solver::clause(vec![!vs[d][i][j], !is_home[d][i], both], round_robin))
                        .post();
                    both
                })
                .collect();
            solver
                .add_constraint(pumpkin_solver::boolean_equals(vec![1; n_days], hosted, one, round_robin))
                .post();
        }
    }

    // 1. Mirroring: dates are paired (1,8), (2,9), (3,12), (4,13), (5,14), (6,15),
    // (7,16), (10,17), (11,18); paired dates have the same opponents with home
    // and away swapped (where + mirrored where == 2).
    let scheme = [7usize, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10];
    let mirror = solver.new_constraint_tag();
    for d in 0..n_days {
        for i in 0..n_teams {
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![config[d][i].scaled(1), config[scheme[d]][i].scaled(-1)],
                    0,
                    mirror,
                ))
                .post();
            solver
                .add_constraint(pumpkin_solver::equals(vec![place[d][i], place[scheme[d]][i]], 2, mirror))
                .post();
        }
    }

    // At most k of these literals are true.
    let at_most = |solver: &mut Solver, lits: Vec<Lit>, k: i32, tag| {
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(vec![1; lits.len()], lits, k, tag))
            .post();
    };

    // 2. No team plays away on both last dates.
    let tag = solver.new_constraint_tag();
    for t in 0..n_teams {
        at_most(solver, vec![is_away[last - 1][t], is_away[last][t]], 1, tag);
    }

    // 3. Home/away/bye patterns: at most two home matches in a row, at most two
    // away matches in a row, at most three away-or-bye dates in a row (i.e. not
    // home), at most four home-or-bye dates in a row (i.e. not away).
    let pattern = solver.new_constraint_tag();
    for t in 0..n_teams {
        for d in 0..n_days - 2 {
            at_most(solver, (d..d + 3).map(|e| is_home[e][t]).collect(), 2, pattern);
            at_most(solver, (d..d + 3).map(|e| is_away[e][t]).collect(), 2, pattern);
        }
        for d in 0..n_days - 3 {
            at_most(solver, (d..d + 4).map(|e| !is_home[e][t]).collect(), 3, pattern);
        }
        for d in 0..n_days - 4 {
            at_most(solver, (d..d + 5).map(|e| !is_away[e][t]).collect(), 4, pattern);
        }
    }

    // 4. Weekend pattern: of the weekends each team plays four at home, four
    // away, and has one bye.
    let weekend = solver.new_constraint_tag();
    let four = solver.new_bounded_integer(4, 4);
    for t in 0..n_teams {
        for (flag, target) in [(&is_home, four), (&is_away, four), (&is_bye, one)] {
            let lits: Vec<Lit> = weekends.iter().map(|&d| flag[d][t]).collect();
            solver
                .add_constraint(pumpkin_solver::boolean_equals(vec![1; lits.len()], lits, target, weekend))
                .post();
        }
    }

    // 5. First weekends: each team is at home or has a bye on at least two of the
    // first five weekends, i.e. plays away on at most three of them.
    let tag = solver.new_constraint_tag();
    for t in 0..n_teams {
        at_most(solver, weekends[..5].iter().map(|&d| is_away[d][t]).collect(), 3, tag);
    }

    // 6. Rival matches: on the last date every team except FSU plays its rival,
    // unless it plays FSU or has a bye.
    let tag = solver.new_constraint_tag();
    for t in 0..n_teams {
        if t != fsu {
            solver
                .add_constraint(pumpkin_solver::clause(
                    vec![vs[last][t][rivals[t]], vs[last][t][fsu], is_bye[last][t]],
                    tag,
                ))
                .post();
        }
    }

    // 7. Constrained matches: Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each occur
    // at least once in dates 11 to 18.
    let tag = solver.new_constraint_tag();
    for (a, b) in [(wake, unc), (wake, duke), (gt, unc), (gt, duke)] {
        solver
            .add_constraint(pumpkin_solver::clause((10..n_days).map(|d| vs[d][a][b]).collect::<Vec<Lit>>(), tag))
            .post();
    }

    // 8. Opponent sequences: no team plays away against UNC and then away against
    // Duke on consecutive dates (or Duke then UNC); no team plays UNC, Duke and
    // Wake on three consecutive dates in any order.
    let sequence = solver.new_constraint_tag();
    for t in 0..n_teams {
        if t != duke && t != unc {
            for d in 0..n_days - 1 {
                for (x, y) in [(unc, duke), (duke, unc)] {
                    solver
                        .add_constraint(pumpkin_solver::clause(
                            vec![!vs[d][t][x], !is_away[d][t], !vs[d + 1][t][y], !is_away[d + 1][t]],
                            sequence,
                        ))
                        .post();
                }
            }
        }
        if t != unc && t != duke && t != wake {
            for d in 0..n_days - 2 {
                for [x, y, z] in [
                    [unc, duke, wake],
                    [unc, wake, duke],
                    [duke, unc, wake],
                    [duke, wake, unc],
                    [wake, unc, duke],
                    [wake, duke, unc],
                ] {
                    solver
                        .add_constraint(pumpkin_solver::clause(
                            vec![!vs[d][t][x], !vs[d + 1][t][y], !vs[d + 2][t][z]],
                            sequence,
                        ))
                        .post();
                }
            }
        }
    }

    // 9. Other constraints.
    let other = solver.new_constraint_tag();
    let mut fact = |solver: &mut Solver, l: Lit| {
        solver.add_constraint(pumpkin_solver::clause(vec![l], other)).post();
    };
    // UNC plays its rival Duke in date 11 and in the last date.
    fact(solver, vs[10][unc][duke]);
    fact(solver, vs[last][unc][duke]);
    // UNC plays Clem in the second date.
    fact(solver, vs[1][unc][clem]);
    // Duke has a bye in date 16.
    fact(solver, is_bye[15][duke]);
    // Wake does not play home in date 17.
    fact(solver, !is_home[16][wake]);
    // Wake has a bye in the first date.
    fact(solver, is_bye[0][wake]);
    // Clem, Duke, UMD and Wake do not play away in the last date.
    for t in [clem, duke, umd, wake] {
        fact(solver, !is_away[last][t]);
    }
    // Clem, FSU, GT and Wake do not play away in the first date.
    for t in [clem, fsu, gt, wake] {
        fact(solver, !is_away[0][t]);
    }
    // Neither FSU nor NCSt has a bye in the last date.
    for t in [fsu, ncst] {
        fact(solver, !is_bye[last][t]);
    }
    // UNC does not have a bye in the first date.
    fact(solver, !is_bye[0][unc]);

    let mut m = Model::new();
    m.put("config", config);
    m.put("where", place);
    m
}
