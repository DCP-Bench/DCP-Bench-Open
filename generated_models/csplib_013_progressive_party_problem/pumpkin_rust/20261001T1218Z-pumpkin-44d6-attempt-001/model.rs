// Progressive party: choose as few host boats as possible and schedule the guest
// crews' visits to them over several periods.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n_boats = inst.size("n_boats");
    let n_periods = inst.size("n_periods");
    let capacity = inst.ints("capacity"); // people a boat can hold at once
    let crew_size = inst.ints("crew_size"); // people in each boat's crew

    // is_host[b]: boat b is a host boat.
    let is_host: Vec<Lit> = (0..n_boats).map(|_| solver.new_literal()).collect();
    // visits[p][b]: the boat that the crew of boat b is aboard in period p.
    let visits: Vec<Vec<Var>> = (0..n_periods)
        .map(|_| {
            (0..n_boats)
                .map(|_| solver.new_bounded_integer(0, n_boats as i32 - 1))
                .collect()
        })
        .collect();

    // aboard[p][c][b] is true exactly when crew c is on boat b in period p.
    // The counting constraints below need these indicators because Pumpkin has
    // no count constraint.
    let indicator = solver.new_constraint_tag();
    let mut aboard: Vec<Vec<Vec<Lit>>> = Vec::new();
    for p in 0..n_periods {
        let mut per_crew: Vec<Vec<Lit>> = Vec::new();
        for c in 0..n_boats {
            let mut per_boat: Vec<Lit> = Vec::new();
            for b in 0..n_boats {
                let flag = solver.new_literal();
                solver
                    .add_constraint(pumpkin_solver::equals(
                        vec![visits[p][c].scaled(1)], b as i32, indicator))
                    .reify(flag);
                per_boat.push(flag);
            }
            per_crew.push(per_boat);
        }
        aboard.push(per_crew);
    }

    // Crews of host boats stay on their own boat in every period.
    let host_stays = solver.new_constraint_tag();
    for b in 0..n_boats {
        for p in 0..n_periods {
            solver
                .add_constraint(pumpkin_solver::clause(
                    vec![!is_host[b], aboard[p][b][b]], host_stays))
                .post();
        }
    }

    // Non-host boats cannot be visited (and so are not the destination of any crew).
    let only_hosts = solver.new_constraint_tag();
    for p in 0..n_periods {
        for c in 0..n_boats {
            for b in 0..n_boats {
                solver
                    .add_constraint(pumpkin_solver::clause(
                        vec![!aboard[p][c][b], is_host[b]], only_hosts))
                    .post();
            }
        }
    }

    // The people aboard a boat in a period, host crew and guests together, never
    // exceed its capacity. A zero crew size is left out of the sum because
    // Pumpkin cannot take a zero coefficient.
    let capacity_tag = solver.new_constraint_tag();
    for p in 0..n_periods {
        for b in 0..n_boats {
            let (sizes, crews): (Vec<i32>, Vec<Lit>) = (0..n_boats)
                .filter(|&c| crew_size[c] != 0)
                .map(|c| (crew_size[c], aboard[p][c][b]))
                .unzip();
            if crews.is_empty() {
                continue;
            }
            solver
                .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                    sizes, crews, capacity[b], capacity_tag))
                .post();
        }
    }

    // A guest crew cannot visit the same boat twice: for a non-host boat, the
    // boats it visits in two different periods differ. (A host boat stays put,
    // so it is exempt.)
    let no_revisit = solver.new_constraint_tag();
    for c in 0..n_boats {
        for p in 0..n_periods {
            for q in (p + 1)..n_periods {
                for b in 0..n_boats {
                    solver
                        .add_constraint(pumpkin_solver::clause(
                            vec![is_host[c], !aboard[p][c][b], !aboard[q][c][b]], no_revisit))
                        .post();
                }
            }
        }
    }

    // Two crews cannot meet more than once: counting the periods in which crews
    // c1 and c2 are on the same boat, the total is at most 1.
    let meeting = solver.new_constraint_tag();
    let at_most_once = solver.new_constraint_tag();
    for c1 in 0..n_boats {
        for c2 in (c1 + 1)..n_boats {
            let mut together: Vec<Lit> = Vec::new();
            for p in 0..n_periods {
                let flag = solver.new_literal();
                solver
                    .add_constraint(pumpkin_solver::equals(
                        vec![visits[p][c1].scaled(1), visits[p][c2].scaled(-1)], 0, meeting))
                    .reify(flag);
                together.push(flag);
            }
            solver
                .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                    vec![1; n_periods], together, 1, at_most_once))
                .post();
        }
    }

    // Minimise the number of host boats.
    let host_count = solver.new_bounded_integer(0, n_boats as i32);
    let count_tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(
            vec![1; n_boats], is_host.clone(), host_count, count_tag))
        .post();

    let mut m = Model::new();
    m.put("visits", visits);
    m.put("is_host", is_host);
    m.minimise(host_count);
    m
}
