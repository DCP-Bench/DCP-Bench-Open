// Frog circle: arrange the cards 1..n on a circle so that a frog that starts on
// card 1 and jumps, from card k, k places clockwise visits every card.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let ni = n as i32;

    // x[p] is the card at position p; pos[i] is the position of the frog after i
    // jumps; visited[i] is the card the frog stands on after i jumps.
    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, ni)).collect();
    let pos: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, ni - 1)).collect();
    let visited: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, ni)).collect();

    // The cards are all different, the positions the frog lands on are all
    // different, and the cards it lands on are all different.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(x.clone(), tag)).post();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(pos.clone(), tag)).post();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(visited.clone(), tag)).post();

    // The frog starts on card 1 at position 0.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(vec![x[0].scaled(1)], 1, tag)).post();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(vec![pos[0].scaled(1)], 0, tag)).post();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(vec![visited[0].scaled(1)], 1, tag)).post();

    // The card visited at jump i is the card lying at the frog's position.
    let on_card = solver.new_constraint_tag();
    for i in 1..n {
        solver
            .add_constraint(pumpkin_solver::element(
                pos[i].scaled(1), x.clone(), visited[i].scaled(1), on_card))
            .post();
    }

    // The next position is the previous position plus the card lying there,
    // taken modulo n. Pumpkin has no modulo constraint, so the sum is written as
    // pos[i-1] + visited[i-1] = n * wrap[i] + pos[i]. Both pos values lie in
    // 0..n-1 and the card in 1..n, so the sum is below 2n and wrap is 0 or 1.
    let step = solver.new_constraint_tag();
    for i in 1..n {
        let wrap = solver.new_bounded_integer(0, 1);
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![
                    pos[i - 1].scaled(1),
                    visited[i - 1].scaled(1),
                    wrap.scaled(-ni),
                    pos[i].scaled(-1),
                ],
                0,
                step))
            .post();
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
