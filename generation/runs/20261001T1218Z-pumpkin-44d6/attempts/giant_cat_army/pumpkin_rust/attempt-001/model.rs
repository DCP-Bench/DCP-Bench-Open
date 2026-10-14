// Giant cat army: starting from [0], extend a list by adding 5, adding 7 or taking
// the square root of the last number, so that 2, 10 and 14 appear in that order.
// All numbers are distinct integers no larger than 60; the list has 24 entries
// and ends with 14.
//
// The instance has no fields: the length 24, the bound 60 and the operations are
// the puzzle's own constants, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let maxval = 60;
    let n = 24;
    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, maxval)).collect();

    // All numbers in the list are different.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(x.clone(), tag)).post();

    // The list starts at 0, the first step adds 5 or 7, and it ends with 14.
    let given = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(vec![x[0]], 0, given)).post();
    solver.add_constraint(pumpkin_solver::table(vec![x[1]], vec![vec![5], vec![7]], given)).post();
    solver.add_constraint(pumpkin_solver::equals(vec![x[n - 1]], 14, given)).post();

    // Each step adds 5, adds 7, or takes the square root (x[i] == x[i+1]^2). The
    // allowed (x[i], x[i+1]) pairs within 0..60 are listed as a table.
    let mut steps: Vec<Vec<i32>> = Vec::new();
    for v in 0..=maxval {
        for w in 0..=maxval {
            if w == v + 5 || w == v + 7 || v == w * w {
                steps.push(vec![v, w]);
            }
        }
    }
    let step = solver.new_constraint_tag();
    for i in 0..n - 1 {
        solver.add_constraint(pumpkin_solver::table(vec![x[i], x[i + 1]], steps.clone(), step)).post();
    }

    // 2 appears at position ix2 and 10 at position ix10, with ix2 before ix10
    // (positions 1..n-1, 0-based; the reference indexes the list the same way).
    let order = solver.new_constraint_tag();
    let ix2 = solver.new_bounded_integer(1, n as i32 - 1);
    let ix10 = solver.new_bounded_integer(1, n as i32 - 1);
    let two = solver.new_bounded_integer(2, 2);
    let ten = solver.new_bounded_integer(10, 10);
    solver
        .add_constraint(pumpkin_solver::element(ix2.scaled(1), x.clone(), two.scaled(1), order))
        .post();
    solver
        .add_constraint(pumpkin_solver::element(ix10.scaled(1), x.clone(), ten.scaled(1), order))
        .post();
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(vec![ix2.scaled(1), ix10.scaled(-1)], -1, order))
        .post();

    let mut m = Model::new();
    m.put("x", x);
    m
}
