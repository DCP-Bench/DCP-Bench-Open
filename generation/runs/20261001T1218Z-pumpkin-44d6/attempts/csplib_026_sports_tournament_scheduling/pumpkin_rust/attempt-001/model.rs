// Sports tournament scheduling (CSPLib 26): n_teams teams play over n_teams-1
// weeks, each week split into n_teams/2 periods with one match per period.
// Every team plays once a week, every two teams meet, and no team plays more
// than twice in the same period.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n_teams = inst.size("n_teams");
    let n_weeks = n_teams - 1;
    let n_periods = n_teams / 2;

    // is_home[w][p][t] (is_away[w][p][t]) is true when team t + 1 is the home
    // (away) team of the match in week w, period p. The model is written over
    // these Booleans because Pumpkin has no count constraint and sums of
    // literals propagate well.
    let slot_lits = |solver: &mut Solver| -> Vec<Vec<Vec<Lit>>> {
        (0..n_weeks)
            .map(|_| {
                (0..n_periods)
                    .map(|_| (0..n_teams).map(|_| solver.new_literal()).collect())
                    .collect()
            })
            .collect()
    };
    let is_home = slot_lits(solver);
    let is_away = slot_lits(solver);

    // Every match has exactly one home team and exactly one away team.
    let one_team = solver.new_constraint_tag();
    let one = solver.new_bounded_integer(1, 1);
    for w in 0..n_weeks {
        for p in 0..n_periods {
            for side in [&is_home, &is_away] {
                solver
                    .add_constraint(pumpkin_solver::boolean_equals(
                        vec![1; n_teams], side[w][p].clone(), one, one_team))
                    .post();
            }
        }
    }

    // home[w][p] and away[w][p] are the team numbers (1..n_teams).
    let numbering = solver.new_constraint_tag();
    let weights: Vec<i32> = (1..=n_teams as i32).collect();
    let number = |solver: &mut Solver, side: &Vec<Vec<Vec<Lit>>>| -> Vec<Vec<Var>> {
        (0..n_weeks)
            .map(|w| {
                (0..n_periods)
                    .map(|p| {
                        let v = solver.new_bounded_integer(1, n_teams as i32);
                        solver
                            .add_constraint(pumpkin_solver::boolean_equals(
                                weights.clone(), side[w][p].clone(), v, numbering))
                            .post();
                        v
                    })
                    .collect()
            })
            .collect()
    };
    let home = number(solver, &is_home);
    let away = number(solver, &is_away);

    // Every team plays exactly once a week (the reference's AllDifferent over the
    // week's home and away teams, which use up all n_teams teams). This also
    // keeps a team from playing itself.
    let weekly = solver.new_constraint_tag();
    let n_slots = 2 * n_periods;
    for w in 0..n_weeks {
        for t in 0..n_teams {
            let mut appearances: Vec<Lit> = Vec::new();
            for p in 0..n_periods {
                appearances.push(is_home[w][p][t]);
                appearances.push(is_away[w][p][t]);
            }
            solver
                .add_constraint(pumpkin_solver::boolean_equals(
                    vec![1; n_slots], appearances, one, weekly))
                .post();
        }
    }

    // Every two teams play each other. meets[w][p][pair] is true when the match
    // in week w, period p is between the two teams of the pair; it requires both
    // teams to play in that match, and for each pair some match must be theirs.
    let pairs: Vec<(usize, usize)> = (0..n_teams)
        .flat_map(|a| ((a + 1)..n_teams).map(move |b| (a, b)))
        .collect();
    let meeting = solver.new_constraint_tag();
    let mut meets: Vec<Vec<Vec<Lit>>> = Vec::new();
    for w in 0..n_weeks {
        let mut per_period = Vec::new();
        for p in 0..n_periods {
            let mut per_pair = Vec::new();
            for &(a, b) in &pairs {
                let lit = solver.new_literal();
                for t in [a, b] {
                    solver
                        .add_constraint(pumpkin_solver::clause(
                            vec![!lit, is_home[w][p][t], is_away[w][p][t]], meeting))
                        .post();
                }
                per_pair.push(lit);
            }
            per_period.push(per_pair);
        }
        meets.push(per_period);
    }
    for k in 0..pairs.len() {
        let somewhere: Vec<Lit> = (0..n_weeks)
            .flat_map(|w| (0..n_periods).map(move |p| (w, p)))
            .map(|(w, p)| meets[w][p][k])
            .collect();
        solver.add_constraint(pumpkin_solver::clause(somewhere, meeting)).post();
    }

    // Implied constraint, added to help the search: there are exactly as many
    // matches as pairs of teams, so each match is between exactly one pair.
    let implied = solver.new_constraint_tag();
    for w in 0..n_weeks {
        for p in 0..n_periods {
            solver
                .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                    vec![1; pairs.len()], meets[w][p].clone(), 1, implied))
                .post();
        }
    }

    // Every team plays at most twice in the same period over the tournament.
    let period_limit = solver.new_constraint_tag();
    for t in 0..n_teams {
        for p in 0..n_periods {
            let mut plays: Vec<Lit> = Vec::new();
            for w in 0..n_weeks {
                plays.push(is_home[w][p][t]);
                plays.push(is_away[w][p][t]);
            }
            solver
                .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                    vec![1; plays.len()], plays, 2, period_limit))
                .post();
        }
    }

    let mut m = Model::new();
    m.put("home", home);
    m.put("away", away);
    m
}
