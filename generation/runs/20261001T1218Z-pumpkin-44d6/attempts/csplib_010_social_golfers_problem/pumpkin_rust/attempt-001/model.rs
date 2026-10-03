// Social golfers: every week the golfers play in groups of a fixed size, and no
// two golfers are in the same group in more than one week.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n_weeks = inst.size("n_weeks");
    let n_groups = inst.size("n_groups");
    let group_size = inst.int("group_size");
    let n_golfers = n_groups * group_size as usize;

    // assign[g][w] is the group (0-indexed) that golfer g plays in during week w.
    let assign: Vec<Vec<Var>> = (0..n_golfers)
        .map(|_| {
            (0..n_weeks)
                .map(|_| solver.new_bounded_integer(0, n_groups as i32 - 1))
                .collect()
        })
        .collect();

    // in_group[g][w][gr] is true exactly when golfer g is in group gr in week w.
    // Pumpkin has no count constraint, so the group sizes and the meetings below
    // are written over these literals.
    let channel = solver.new_constraint_tag();
    let mut in_group: Vec<Vec<Vec<Lit>>> = Vec::new();
    for g in 0..n_golfers {
        let mut per_week: Vec<Vec<Lit>> = Vec::new();
        for w in 0..n_weeks {
            let mut per_group: Vec<Lit> = Vec::new();
            for gr in 0..n_groups {
                let flag = solver.new_literal();
                solver
                    .add_constraint(pumpkin_solver::equals(
                        vec![assign[g][w].scaled(1)], gr as i32, channel))
                    .reify(flag);
                per_group.push(flag);
            }
            per_week.push(per_group);
        }
        in_group.push(per_week);
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

    // Each pair of golfers meets at most once: over the weeks, the number of weeks
    // in which they share a group is at most 1. meet[w] is forced true when the
    // two golfers are in the same group in week w; it may also be true otherwise,
    // which can only tighten the limit and never allows a repeated meeting.
    let shares = solver.new_constraint_tag();
    let once = solver.new_constraint_tag();
    for g1 in 0..n_golfers {
        for g2 in (g1 + 1)..n_golfers {
            let mut meet: Vec<Lit> = Vec::new();
            for w in 0..n_weeks {
                let flag = solver.new_literal();
                for gr in 0..n_groups {
                    solver
                        .add_constraint(pumpkin_solver::clause(
                            vec![!in_group[g1][w][gr], !in_group[g2][w][gr], flag], shares))
                        .post();
                }
                meet.push(flag);
            }
            solver
                .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                    vec![1; n_weeks], meet, 1, once))
                .post();
        }
    }

    let mut m = Model::new();
    m.put("assign", assign);
    m
}
