// Aircraft landing: aircraft land on one runway in a fixed order, each within its
// time window and separated from the previous ones; choose the landing times that
// minimise the penalty for landing before or after each aircraft's target time.

// `sum(coeffs[k] * vars[k])` as terms for a linear constraint. A zero
// coefficient would break Pumpkin, so those entries are dropped; if nothing is
// left the sum is the constant 0, written over a variable fixed at 0 because
// Pumpkin cannot post an empty linear constraint.
fn weighted(solver: &mut Solver, coeffs: &[i32], vars: &[Var]) -> Vec<Term> {
    let mut terms: Vec<Term> = coeffs
        .iter()
        .zip(vars)
        .filter(|(&c, _)| c != 0)
        .map(|(&c, &v)| v.scaled(c))
        .collect();
    if terms.is_empty() {
        terms.push(solver.new_bounded_integer(0, 0).scaled(1));
    }
    terms
}

fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let earliest = inst.ints("earliest_landing");
    let latest = inst.ints("latest_landing");
    let target = inst.ints("target_landing");
    let penalty_after = inst.ints("penalty_after"); // per time unit landing after the target
    let penalty_before = inst.ints("penalty_before"); // per time unit landing before the target
    let separation = inst.matrix("separation_time"); // separation[i][j]: gap needed between i and j
    let n = earliest.len();

    // landing_times[i] is when aircraft i lands. The time window constraints
    // earliest[i] <= landing_times[i] <= latest[i] are the bounds of its domain.
    let landing_times: Vec<Var> = (0..n)
        .map(|i| solver.new_bounded_integer(earliest[i], latest[i]))
        .collect();

    // earliness[i] and lateness[i] are how far aircraft i lands before and after
    // its target time. Their upper bounds come from the time window: an aircraft
    // cannot land earlier than its earliest time or later than its latest time.
    // Capping them at those values removes only assignments where an aircraft
    // is counted both early and late, which are never cheaper and so never
    // change the landing times or the minimum penalty.
    let earliness: Vec<Var> = (0..n)
        .map(|i| solver.new_bounded_integer(0, (target[i] - earliest[i]).max(0)))
        .collect();
    let lateness: Vec<Var> = (0..n)
        .map(|i| solver.new_bounded_integer(0, (latest[i] - target[i]).max(0)))
        .collect();

    // Landing time minus target time equals lateness minus earliness:
    // landing_times[i] - lateness[i] + earliness[i] == target[i].
    let deviation = solver.new_constraint_tag();
    for i in 0..n {
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![
                    landing_times[i].scaled(1),
                    lateness[i].scaled(-1),
                    earliness[i].scaled(1),
                ],
                target[i],
                deviation,
            ))
            .post();
    }

    // The landing order is fixed (i lands before j for i < j) and consecutive
    // landings keep their separation time: landing_times[j] - landing_times[i]
    // >= separation[i][j], posted as landing_times[i] - landing_times[j] <= -separation[i][j].
    let gap = solver.new_constraint_tag();
    for i in 0..n {
        for j in (i + 1)..n {
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(
                    vec![landing_times[i].scaled(1), landing_times[j].scaled(-1)],
                    -separation[i][j],
                    gap,
                ))
                .post();
        }
    }

    // total_penalty = sum(penalty_before * earliness + penalty_after * lateness).
    // Its bounds are the cheapest and dearest values the penalties allow.
    let mut coeffs: Vec<i32> = penalty_before.clone();
    coeffs.extend(penalty_after.iter());
    let mut vars: Vec<Var> = earliness.clone();
    vars.extend(lateness.iter());
    let mut lowest = 0;
    let mut highest = 0;
    for i in 0..n {
        let early = penalty_before[i] * (target[i] - earliest[i]).max(0);
        let late = penalty_after[i] * (latest[i] - target[i]).max(0);
        lowest += early.min(0) + late.min(0);
        highest += early.max(0) + late.max(0);
    }
    let total_penalty = solver.new_bounded_integer(lowest, highest);
    let mut terms = weighted(solver, &coeffs, &vars);
    terms.push(total_penalty.scaled(-1));
    let objective = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(terms, 0, objective))
        .post();

    let mut m = Model::new();
    m.put("landing_times", landing_times);
    m.put("total_penalty", total_penalty);
    m.minimise(total_penalty);
    m
}
