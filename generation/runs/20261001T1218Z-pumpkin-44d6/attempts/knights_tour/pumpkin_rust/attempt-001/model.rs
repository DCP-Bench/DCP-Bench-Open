// Knight's tour: number the squares of an n x n board 0..n*n-1 in the order a
// knight visits them, visiting every square exactly once (the tour need not
// return to its starting square).
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n");
    let squares = n * n;
    let last = squares as i32 - 1;

    // x[i][j] is the move number at which the knight stands on square (i, j).
    let x: Vec<Vec<Var>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_bounded_integer(0, last)).collect())
        .collect();
    let flat: Vec<Var> = x.iter().flatten().copied().collect();
    // square[k] is the square (numbered i * n + j) visited at move k. It is the
    // inverse of x, introduced so that "move k and move k + 1 are a knight's
    // move apart" is a constraint on two variables.
    let square: Vec<Var> = (0..squares)
        .map(|_| solver.new_bounded_integer(0, last))
        .collect();

    // Each square is visited exactly once: the move numbers are all different,
    // and so are the squares visited at the different moves.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(flat.clone(), tag)).post();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(square.clone(), tag)).post();

    // Link the two views in both directions: the square visited at move k
    // carries the number k, and the number on a square says where that move went.
    let linked = solver.new_constraint_tag();
    for k in 0..squares {
        let number = solver.new_bounded_integer(k as i32, k as i32);
        solver
            .add_constraint(pumpkin_solver::element(
                square[k].scaled(1), flat.clone(), number.scaled(1), linked))
            .post();
    }
    for s in 0..squares {
        let here = solver.new_bounded_integer(s as i32, s as i32);
        solver
            .add_constraint(pumpkin_solver::element(
                flat[s].scaled(1), square.clone(), here.scaled(1), linked))
            .post();
    }

    // Consecutive moves are a knight's move apart (two squares one way and one
    // the other). Since every number appears once, this is the reference's
    // "exactly one knight-neighbour holds the next number and exactly one the
    // previous". The allowed pairs of squares are listed once from the board size.
    let jumps = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)];
    let size = n as i32;
    let mut knight_pairs: Vec<Vec<i32>> = Vec::new();
    for i in 0..size {
        for j in 0..size {
            for &(di, dj) in &jumps {
                let (ni, nj) = (i + di, j + dj);
                if ni >= 0 && nj >= 0 && ni < size && nj < size {
                    knight_pairs.push(vec![i * size + j, ni * size + nj]);
                }
            }
        }
    }
    let knight_move = solver.new_constraint_tag();
    for k in 0..squares.saturating_sub(1) {
        solver
            .add_constraint(pumpkin_solver::table(
                vec![square[k], square[k + 1]], knight_pairs.clone(), knight_move))
            .post();
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
