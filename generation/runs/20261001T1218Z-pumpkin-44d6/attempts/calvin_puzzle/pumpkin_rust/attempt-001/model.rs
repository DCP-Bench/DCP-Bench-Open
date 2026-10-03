// Calvin puzzle: write the numbers 1..n*n into an n x n grid so that each next
// number is placed three squares away horizontally or vertically (a two-square
// gap) or two squares away diagonally (a one-square gap) from the previous one.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let squares = n * n;
    let last = squares as i32;
    let size = n as i32;

    // x[i][j] is the number written in square (i, j); flat[s] is the same
    // variable for square s = i * n + j.
    let x: Vec<Vec<Var>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_bounded_integer(1, last)).collect())
        .collect();
    let flat: Vec<Var> = x.iter().flatten().copied().collect();

    // Every square gets a different number.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(flat.clone(), tag)).post();

    // The allowed moves: three squares along a row or column, or two squares
    // along both (a diagonal), staying on the grid.
    let moves = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)];
    let targets: Vec<Vec<usize>> = (0..squares)
        .map(|s| {
            let (i, j) = ((s / n) as i32, (s % n) as i32);
            moves
                .iter()
                .map(|&(di, dj)| (i + di, j + dj))
                .filter(|&(a, b)| a >= 0 && b >= 0 && a < size && b < size)
                .map(|(a, b)| (a * size + b) as usize)
                .collect()
        })
        .collect();

    // step[s][k] is true when the number after the one in square s is placed in
    // its k-th target square. Working on these move literals, instead of the
    // numbers alone, lets the solver reason about the sequence of moves directly.
    let step: Vec<Vec<Lit>> = (0..squares)
        .map(|s| targets[s].iter().map(|_| solver.new_literal()).collect())
        .collect();
    let mut arriving: Vec<Vec<Lit>> = vec![Vec::new(); squares];
    for s in 0..squares {
        for (k, &t) in targets[s].iter().enumerate() {
            arriving[t].push(step[s][k]);
        }
    }

    // A move goes to the next number: moving from s to t means x[t] = x[s] + 1.
    let next_number = solver.new_constraint_tag();
    for s in 0..squares {
        for (k, &t) in targets[s].iter().enumerate() {
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![flat[t].scaled(1), flat[s].scaled(-1)], 1, next_number))
                .implied_by(step[s][k]);
        }
    }

    // Each number k < n*n has its successor k + 1 one allowed move away (the
    // reference's rule), and with all numbers different this means: every
    // square except the one holding n*n is left by exactly one move, every
    // square except the one holding 1 is entered by exactly one move, and those
    // two squares are left (entered) by none.
    let degree = solver.new_constraint_tag();
    for s in 0..squares {
        let is_last = solver.new_literal();
        solver
            .add_constraint(pumpkin_solver::equals(vec![flat[s].scaled(1)], last, degree))
            .reify(is_last);
        let is_first = solver.new_literal();
        solver
            .add_constraint(pumpkin_solver::equals(vec![flat[s].scaled(1)], 1, degree))
            .reify(is_first);
        for (lits, end) in [(step[s].clone(), is_last), (arriving[s].clone(), is_first)] {
            let mut some = lits.clone();
            some.push(end);
            solver.add_constraint(pumpkin_solver::clause(some, degree)).post();
            for &l in &lits {
                solver.add_constraint(pumpkin_solver::clause(vec![!end, !l], degree)).post();
            }
            if !lits.is_empty() {
                solver
                    .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                        vec![1; lits.len()], lits, 1, degree))
                    .post();
            }
        }
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
