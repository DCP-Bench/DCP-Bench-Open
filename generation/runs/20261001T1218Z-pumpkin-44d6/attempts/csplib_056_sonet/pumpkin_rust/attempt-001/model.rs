// SONET: put the n nodes (clients) on rings by installing an add-drop
// multiplexer (ADM) for each node on each ring that carries it. Two nodes with
// traffic between them must share a ring, a ring holds at most its capacity in
// nodes, and the total number of ADMs (node-on-ring placements) is minimised.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let r = inst.size("r"); // number of rings available
    let n = inst.size("n"); // number of nodes
    let demand = inst.matrix("demand"); // demand[i][j]: traffic between nodes i and j
    let capacity_nodes = inst.ints("capacity_nodes"); // most nodes each ring can host

    // ring_config[k][i] is true when node i is on ring k (it has an ADM there).
    let ring_config: Vec<Vec<Lit>> = (0..r)
        .map(|_| (0..n).map(|_| solver.new_literal()).collect())
        .collect();

    // Demand: for every pair of nodes i < j with traffic between them, there is
    // a ring k that has both nodes on it. on_ring[k] is true only if both nodes
    // are on ring k, and at least one of the rings must have it true.
    let both_on = solver.new_constraint_tag();
    let share_a_ring = solver.new_constraint_tag();
    for i in 0..n {
        for j in (i + 1)..n {
            if demand[i][j] > 0 {
                let on_ring: Vec<Lit> = (0..r).map(|_| solver.new_literal()).collect();
                for k in 0..r {
                    solver
                        .add_constraint(pumpkin_solver::clause(vec![!on_ring[k], ring_config[k][i]], both_on))
                        .post();
                    solver
                        .add_constraint(pumpkin_solver::clause(vec![!on_ring[k], ring_config[k][j]], both_on))
                        .post();
                }
                solver
                    .add_constraint(pumpkin_solver::clause(on_ring, share_a_ring))
                    .post();
            }
        }
    }

    // Ring capacity: the number of nodes on ring k is at most capacity_nodes[k].
    let capacity = solver.new_constraint_tag();
    for k in 0..r {
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                vec![1; n], ring_config[k].clone(), capacity_nodes[k], capacity))
            .post();
    }

    // Objective: total_adms is one ADM per node placed on a ring, i.e. the
    // number of true entries of ring_config, between 0 and r * n.
    let total_adms = solver.new_bounded_integer(0, (r * n) as i32);
    let everything: Vec<Lit> = ring_config.iter().flatten().copied().collect();
    let adm_count = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(vec![1; r * n], everything, total_adms, adm_count))
        .post();

    let mut m = Model::new();
    m.put("ring_config", ring_config);
    m.put("total_adms", total_adms);
    m.minimise(total_adms);
    m
}
