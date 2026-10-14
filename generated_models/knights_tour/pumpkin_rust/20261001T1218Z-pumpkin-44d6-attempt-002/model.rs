// Knight's tour: number the squares of an n x n board 0..n*n-1 in the order a
// knight visits them, visiting every square exactly once (the tour need not
// return to its starting square).
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let squares = n * n;
    let last = squares as i32 - 1;
    let size = n as i32;

    // x[i][j] is the move number at which the knight stands on square (i, j);
    // flat[s] is the same variable for square s = i * n + j.
    let x: Vec<Vec<Var>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_bounded_integer(0, last)).collect())
        .collect();
    let flat: Vec<Var> = x.iter().flatten().copied().collect();

    // Each square is visited exactly once: the move numbers are all different.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(flat.clone(), tag)).post();

    // The squares a knight's move (two squares one way, one the other) away.
    let jumps = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)];
    let neighbours: Vec<Vec<usize>> = (0..squares)
        .map(|s| {
            let (i, j) = ((s / n) as i32, (s % n) as i32);
            jumps
                .iter()
                .map(|&(di, dj)| (i + di, j + dj))
                .filter(|&(a, b)| a >= 0 && b >= 0 && a < size && b < size)
                .map(|(a, b)| (a * size + b) as usize)
                .collect()
        })
        .collect();

    // jump[s][k] is true when the knight goes from square s straight to its k-th
    // neighbour. Working on these knight-move literals, instead of the move
    // numbers alone, lets the solver reason about the tour's arcs directly.
    let jump: Vec<Vec<Lit>> = (0..squares)
        .map(|s| neighbours[s].iter().map(|_| solver.new_literal()).collect())
        .collect();
    // arriving[t] lists the literals of the moves that land on square t.
    let mut arriving: Vec<Vec<Lit>> = vec![Vec::new(); squares];
    for s in 0..squares {
        for (k, &t) in neighbours[s].iter().enumerate() {
            arriving[t].push(jump[s][k]);
        }
    }

    // A move goes to the next move number: jumping from s to t means x[t] = x[s] + 1.
    let step = solver.new_constraint_tag();
    for s in 0..squares {
        for (k, &t) in neighbours[s].iter().enumerate() {
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![flat[t].scaled(1), flat[s].scaled(-1)], 1, step))
                .implied_by(jump[s][k]);
        }
    }

    // The reference's rule: a square that is not the last one visited has
    // exactly one knight-neighbour holding the next number, and a square that is
    // not the first has exactly one holding the previous number. With the
    // numbers all different that is: every square except the last is left by
    // exactly one move, every square except the first is entered by exactly one
    // move, and the last (first) square is left (entered) by none.
    let degree = solver.new_constraint_tag();
    for s in 0..squares {
        let is_last = solver.new_literal();
        solver
            .add_constraint(pumpkin_solver::equals(vec![flat[s].scaled(1)], last, degree))
            .reify(is_last);
        let is_first = solver.new_literal();
        solver
            .add_constraint(pumpkin_solver::equals(vec![flat[s].scaled(1)], 0, degree))
            .reify(is_first);
        for (lits, end) in [(jump[s].clone(), is_last), (arriving[s].clone(), is_first)] {
            // at least one move unless this is the end of the tour
            let mut some = lits.clone();
            some.push(end);
            solver.add_constraint(pumpkin_solver::clause(some, degree)).post();
            // no move at the end of the tour
            for &l in &lits {
                solver.add_constraint(pumpkin_solver::clause(vec![!end, !l], degree)).post();
            }
            // at most one move
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
