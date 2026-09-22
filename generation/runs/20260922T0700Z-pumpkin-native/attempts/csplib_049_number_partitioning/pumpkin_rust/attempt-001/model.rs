// Split 1..n into two halves with equal sums and equal sums of squares.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let half = n / 2;
    let top = n as i32;

    let a: Vec<Var> = (0..half).map(|_| solver.new_bounded_integer(1, top)).collect();
    let b: Vec<Var> = (0..half).map(|_| solver.new_bounded_integer(1, top)).collect();

    let mut every: Vec<Var> = a.clone();
    every.extend(b.iter().copied());
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(every, tag)).post();

    // equal sums
    let mut balance: Vec<Term> = a.iter().map(|v| v.scaled(1)).collect();
    balance.extend(b.iter().map(|v| v.scaled(-1)));
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(balance, 0, tag)).post();

    // equal sums of squares, each square introduced by a multiplication
    let mut square_balance: Vec<Term> = Vec::new();
    for (group, sign) in [(&a, 1), (&b, -1)] {
        for &v in group {
            let s = solver.new_bounded_integer(1, top * top);
            let tag = solver.new_constraint_tag();
            solver
                .add_constraint(pumpkin_solver::times(
                    v.scaled(1), v.scaled(1), s.scaled(1), tag))
                .post();
            square_balance.push(s.scaled(sign));
        }
    }
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(square_balance, 0, tag)).post();

    let mut m = Model::new();
    m.put("A", a);
    m.put("B", b);
    m
}
