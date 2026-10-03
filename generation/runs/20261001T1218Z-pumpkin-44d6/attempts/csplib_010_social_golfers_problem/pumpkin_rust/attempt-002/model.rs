// Social golfers: every week the golfers play in groups of a fixed size, and no
// two golfers are in the same group in more than one week.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n_weeks = inst.size("n_weeks");
    let n_groups = inst.size("n_groups");
    let group_size = inst.int("group_size");
    let n_golfers = n_groups * group_size as usize;

    // in_group[g][w][gr] is true exactly when golfer g plays in group gr in week w.
    // The model is written over these Booleans, because Pumpkin has no count
    // constraint and Boolean clauses and sums propagate well.
    let in_group: Vec<Vec<Vec<Lit>>> = (0..n_golfers)
        .map(|_| {
            (0..n_weeks)
                .map(|_| (0..n_groups).map(|_| solver.new_literal()).collect())
                .collect()
        })
        .collect();

    // Each golfer plays in exactly one group every week: at least one, and no two.
    let at_least_one = solver.new_constraint_tag();
    let at_most_one = solver.new_constraint_tag();
    for g in 0..n_golfers {
        for w in 0..n_weeks {
            solver
                .add_constraint(pumpkin_solver::clause(in_group[g][w].clone(), at_least_one))
                .post();
            for a in 0..n_groups {
                for b in (a + 1)..n_groups {
                    solver
                        .add_constraint(pumpkin_solver::clause(
                            vec![!in_group[g][w][a], !in_group[g][w][b]], at_most_one))
                        .post();
                }
            }
        }
    }

    // assign[g][w] is the group number (0-indexed) of golfer g in week w, the sum of
    // gr * in_group[g][w][gr]. Group 0 has weight 0, which Pumpkin cannot take, so it
    // is left out of the sum.
    let assign: Vec<Vec<Var>> = (0..n_golfers)
        .map(|_| {
            (0..n_weeks)
                .map(|_| solver.new_bounded_integer(0, n_groups as i32 - 1))
                .collect()
        })
        .collect();
    let numbering = solver.new_constraint_tag();
    if n_groups > 1 {
        for g in 0..n_golfers {
            for w in 0..n_weeks {
                let weights: Vec<i32> = (1..n_groups as i32).collect();
                let lits: Vec<Lit> = (1..n_groups).map(|gr| in_group[g][w][gr]).collect();
                solver
                    .add_constraint(pumpkin_solver::boolean_equals(
                        weights, lits, assign[g][w], numbering))
                    .post();
            }
        }
    }

    // Each group has exactly group_size players in every week.
    let sized = solver.new_constraint_tag();
    let players = solver.new_bounded_integer(group_size, group_size);
    for w in 0..n_weeks {
        for gr in 0..n_groups {
            let members: Vec<Lit> = (0..n_golfers).map(|g| in_group[g][w][gr]).collect();
            solver
                .add_constraint(pumpkin_solver::boolean_equals(
                    vec![1; n_golfers], members, players, sized))
                .post();
        }
    }

    // meet[g1][g2][w] is true exactly when golfers g1 and g2 share a group in week w
    // (the same literal serves both orders of the pair). Both directions are
    // stated: sharing a group forces it true, and it being true forces the two to
    // be in the same group.
    let none_zero = solver.new_constraint_tag();
    let blank = Vec::<Lit>::new();
    let mut meet: Vec<Vec<Vec<Lit>>> = vec![vec![blank.clone(); n_golfers]; n_golfers];
    for g1 in 0..n_golfers {
        for g2 in (g1 + 1)..n_golfers {
            let mut per_week: Vec<Lit> = Vec::new();
            for w in 0..n_weeks {
                let flag = solver.new_literal();
                for gr in 0..n_groups {
                    let x1 = in_group[g1][w][gr];
                    let x2 = in_group[g2][w][gr];
                    solver
                        .add_constraint(pumpkin_solver::clause(vec![!x1, !x2, flag], none_zero))
                        .post();
                    solver
                        .add_constraint(pumpkin_solver::clause(vec![!flag, !x1, x2], none_zero))
                        .post();
                    solver
                        .add_constraint(pumpkin_solver::clause(vec![!flag, x1, !x2], none_zero))
                        .post();
                }
                per_week.push(flag);
            }
            meet[g1][g2] = per_week.clone();
            meet[g2][g1] = per_week;
        }
    }

    // Each pair of golfers meets at most once: over the weeks, the number of weeks
    // in which they share a group is at most 1.
    let once = solver.new_constraint_tag();
    for g1 in 0..n_golfers {
        for g2 in (g1 + 1)..n_golfers {
            solver
                .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                    vec![1; n_weeks], meet[g1][g2].clone(), 1, once))
                .post();
        }
    }

    // Implied constraint, added to help propagation: in each week a golfer shares a
    // group with exactly group_size - 1 other golfers.
    let partners_tag = solver.new_constraint_tag();
    let partners = solver.new_bounded_integer(group_size - 1, group_size - 1);
    for g1 in 0..n_golfers {
        for w in 0..n_weeks {
            let others: Vec<Lit> = (0..n_golfers).filter(|&g2| g2 != g1).map(|g2| meet[g1][g2][w]).collect();
            solver
                .add_constraint(pumpkin_solver::boolean_equals(
                    vec![1; others.len()], others, partners, partners_tag))
                .post();
        }
    }

    let mut m = Model::new();
    m.put("assign", assign);
    m
}
