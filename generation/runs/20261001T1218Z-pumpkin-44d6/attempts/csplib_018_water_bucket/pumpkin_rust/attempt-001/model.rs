// Water buckets (CSPLib 018): starting from the initial contents of three
// buckets, pour water from one bucket into another (until the source is empty or
// the target is full) to reach the goal contents with the fewest transfers. The
// sequence of states has a fixed length MAX_STEPS; after the goal is reached the
// remaining states are padding.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let capacities = inst.ints("capacities");
    let initial = inst.ints("initial_state");
    let goal = inst.ints("goal_state");
    let steps = inst.size("MAX_STEPS");
    let pad = inst.int("PADDING_VALUE");
    let buckets = capacities.len();
    // The water in play is the largest initial amount, as in the reference.
    let total_water = *initial.iter().max().unwrap();

    // Every state of three buckets holding the first bucket's capacity of water
    // (the reference enumerates states this way), and every pour between two of
    // them that moves a positive amount.
    let mut states: Vec<Vec<i32>> = Vec::new();
    for i in 0..=capacities[0] {
        for j in 0..=capacities[1] {
            let k = capacities[0] - i - j;
            if k >= 0 && k <= capacities[2] {
                states.push(vec![i, j, k]);
            }
        }
    }
    let mut pours: Vec<(Vec<i32>, Vec<i32>)> = Vec::new();
    for state in &states {
        for from in 0..buckets {
            for to in 0..buckets {
                if from == to {
                    continue;
                }
                let amount = state[from].min(capacities[to] - state[to]);
                if amount > 0 {
                    let mut next = state.clone();
                    next[from] -= amount;
                    next[to] += amount;
                    if !pours.contains(&(state.clone(), next.clone())) {
                        pours.push((state.clone(), next));
                    }
                }
            }
        }
    }

    // seq[t][b]: the water in bucket b after t transfers, or the padding value.
    let seq: Vec<Vec<Var>> = (0..steps)
        .map(|_| (0..buckets).map(|_| solver.new_bounded_integer(pad, total_water)).collect())
        .collect();

    // The sequence starts with the initial state.
    let start = solver.new_constraint_tag();
    for b in 0..buckets {
        solver.add_constraint(pumpkin_solver::equals(vec![seq[0][b]], initial[b], start)).post();
    }

    // padded[t]: state t is padding (its first entry is the padding value).
    let padding = solver.new_constraint_tag();
    let padded: Vec<Lit> = (0..steps)
        .map(|t| {
            let p = solver.new_literal();
            solver.add_constraint(pumpkin_solver::equals(vec![seq[t][0]], pad, padding)).reify(p);
            p
        })
        .collect();

    // A state that is not padding conserves the water and keeps every bucket
    // within 0 and its capacity.
    let real_state = solver.new_constraint_tag();
    for t in 0..steps {
        solver
            .add_constraint(pumpkin_solver::equals(seq[t].clone(), total_water, real_state))
            .implied_by(!padded[t]);
        for b in 0..buckets {
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(vec![seq[t][b].scaled(-1)], 0, real_state))
                .implied_by(!padded[t]);
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(vec![seq[t][b]], capacities[b], real_state))
                .implied_by(!padded[t]);
        }
    }

    // at_goal[t]: state t is the goal state.
    let goal_tag = solver.new_constraint_tag();
    let at_goal: Vec<Lit> = (0..steps)
        .map(|t| {
            let g = solver.new_literal();
            let parts: Vec<Lit> = (0..buckets)
                .map(|b| {
                    let e = solver.new_literal();
                    solver.add_constraint(pumpkin_solver::equals(vec![seq[t][b]], goal[b], goal_tag)).reify(e);
                    // at_goal implies each bucket holds its goal amount.
                    solver.add_constraint(pumpkin_solver::clause(vec![!g, e], goal_tag)).post();
                    e
                })
                .collect();
            // Every bucket at its goal amount implies at_goal.
            let mut back: Vec<Lit> = parts.iter().map(|&e| !e).collect();
            back.push(g);
            solver.add_constraint(pumpkin_solver::clause(back, goal_tag)).post();
            g
        })
        .collect();

    // Consecutive states: after the goal or after padding comes padding;
    // otherwise the next state is reached by one pour, which always changes the
    // state. These three cases are listed as one table over (state t, state t+1).
    // The goal state is not a source of pours, as the goal forces padding next.
    let pad_row = vec![pad; buckets];
    let mut moves: Vec<Vec<i32>> = Vec::new();
    for (from, to) in &pours {
        if *from != goal {
            moves.push([from.clone(), to.clone()].concat());
        }
    }
    moves.push([goal.clone(), pad_row.clone()].concat());
    moves.push([pad_row.clone(), pad_row.clone()].concat());
    let transfer = solver.new_constraint_tag();
    for t in 0..steps - 1 {
        let scope: Vec<Var> = seq[t].iter().chain(seq[t + 1].iter()).copied().collect();
        solver.add_constraint(pumpkin_solver::table(scope, moves.clone(), transfer)).post();
    }

    // The goal is reached at some step.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::clause(at_goal.clone(), tag)).post();

    // The cost is the number of transfers: the number of states before padding
    // begins, minus one. It is at most MAX_STEPS - 1.
    let states_used = solver.new_bounded_integer(1, steps as i32);
    let tag = solver.new_constraint_tag();
    let real: Vec<Lit> = padded.iter().map(|&p| !p).collect();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(vec![1; steps], real, states_used, tag))
        .post();
    let cost = solver.new_bounded_integer(0, steps as i32 - 1);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(vec![states_used.scaled(1), cost.scaled(-1)], 1, tag))
        .post();

    let mut m = Model::new();
    m.put("cost", cost);
    m.put("sequence", seq);
    m.minimise(cost);
    m
}
