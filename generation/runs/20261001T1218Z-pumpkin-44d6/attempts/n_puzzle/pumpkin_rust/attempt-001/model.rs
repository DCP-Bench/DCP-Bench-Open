// N-puzzle: slide the tiles of a dim x dim sliding puzzle from the start state
// to the end state in exactly N_STEPS states (start and end included). In each
// step the empty square (0) swaps with a tile next to it.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n_steps = inst.size("N_STEPS");
    let start = inst.matrix("puzzle_start");
    let end = inst.matrix("puzzle_end");
    let dim = start.len();
    let cells = dim * dim;
    let biggest = cells as i32 - 1; // tiles are 1..dim*dim-1, and 0 is the empty square

    // steps[t][i][j] is the tile on square (i, j) in state t.
    let steps: Vec<Vec<Vec<Var>>> = (0..n_steps)
        .map(|_| {
            (0..dim)
                .map(|_| (0..dim).map(|_| solver.new_bounded_integer(0, biggest)).collect())
                .collect()
        })
        .collect();
    // flat[t][c] is the same variable, with square (i, j) numbered c = i * dim + j.
    let flat: Vec<Vec<Var>> = steps
        .iter()
        .map(|state| state.iter().flatten().copied().collect())
        .collect();

    // The first state is the start state and the last is the end state.
    let fixed = solver.new_constraint_tag();
    for c in 0..cells {
        let (i, j) = (c / dim, c % dim);
        solver
            .add_constraint(pumpkin_solver::equals(vec![flat[0][c].scaled(1)], start[i][j], fixed))
            .post();
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![flat[n_steps - 1][c].scaled(1)], end[i][j], fixed))
            .post();
    }

    // In every state all squares hold different tiles.
    let distinct = solver.new_constraint_tag();
    for t in 0..n_steps {
        solver
            .add_constraint(pumpkin_solver::all_different(flat[t].clone(), distinct))
            .post();
    }

    // empty[t][c] is true when square c is the empty square in state t, i.e. holds 0.
    let empty_tag = solver.new_constraint_tag();
    let empty: Vec<Vec<Lit>> = (0..n_steps)
        .map(|t| {
            (0..cells)
                .map(|c| {
                    let lit = solver.new_literal();
                    solver
                        .add_constraint(pumpkin_solver::equals(vec![flat[t][c].scaled(1)], 0, empty_tag))
                        .reify(lit);
                    lit
                })
                .collect()
        })
        .collect();

    // hole[t] is the square that is empty in state t (exactly one square is,
    // because the tiles of a state are all different): hole[t] = sum c * empty[t][c].
    let hole_tag = solver.new_constraint_tag();
    let hole: Vec<Var> = (0..n_steps)
        .map(|t| {
            let h = solver.new_bounded_integer(0, biggest);
            if cells > 1 {
                let weights: Vec<i32> = (1..cells as i32).collect();
                let lits: Vec<Lit> = (1..cells).map(|c| empty[t][c]).collect();
                solver
                    .add_constraint(pumpkin_solver::boolean_equals(weights, lits, h, hole_tag))
                    .post();
            }
            solver.add_constraint(pumpkin_solver::clause(empty[t].clone(), hole_tag)).post();
            h
        })
        .collect();

    // The empty square only moves to a square next to it (left, right, up or
    // down). The reference also lets it stay put, but then only the empty square
    // could differ and the board would not change, which every step requires;
    // so staying is excluded here directly.
    let mut slides: Vec<Vec<i32>> = Vec::new();
    for i in 0..dim as i32 {
        for j in 0..dim as i32 {
            for (di, dj) in [(-1, 0), (1, 0), (0, -1), (0, 1)] {
                let (ni, nj) = (i + di, j + dj);
                if ni >= 0 && nj >= 0 && ni < dim as i32 && nj < dim as i32 {
                    slides.push(vec![i * dim as i32 + j, ni * dim as i32 + nj]);
                }
            }
        }
    }
    let slide = solver.new_constraint_tag();
    for t in 1..n_steps {
        solver
            .add_constraint(pumpkin_solver::table(vec![hole[t - 1], hole[t]], slides.clone(), slide))
            .post();
    }

    // Only the empty square moves: a square that is empty in neither of two
    // consecutive states keeps its tile. (The tile that slides into the old
    // empty square is then forced by the states' tiles being all different.)
    let stays = solver.new_constraint_tag();
    for t in 1..n_steps {
        for c in 0..cells {
            let keep = solver.new_literal();
            solver
                .add_constraint(pumpkin_solver::clause(vec![empty[t - 1][c], empty[t][c], keep], stays))
                .post();
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![flat[t][c].scaled(1), flat[t - 1][c].scaled(-1)], 0, stays))
                .implied_by(keep);
        }
    }

    let mut m = Model::new();
    m.put("steps", steps);
    m
}
