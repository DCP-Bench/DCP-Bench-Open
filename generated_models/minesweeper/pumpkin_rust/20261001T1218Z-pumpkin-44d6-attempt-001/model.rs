// Minesweeper: decide which unopened cells hold mines, given that every opened
// cell shows the number of mines among its (up to eight) neighbours.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    // game_data[r][c] is the number shown on an opened cell, or the instance's
    // marker X for a cell that is not opened.
    let unopened = inst.int("X");
    let game = inst.matrix("game_data");
    let rows = game.len();
    let cols = game[0].len();

    // mines[r][c] is true when cell (r, c) holds a mine.
    let mines: Vec<Vec<Lit>> = (0..rows)
        .map(|_| (0..cols).map(|_| solver.new_literal()).collect())
        .collect();

    let safe = solver.new_constraint_tag();
    let count = solver.new_constraint_tag();
    for r in 0..rows {
        for c in 0..cols {
            let shown = game[r][c];
            if shown == unopened {
                continue;
            }
            // An opened cell is not a mine.
            solver
                .add_constraint(pumpkin_solver::conjunction(vec![!mines[r][c]], safe))
                .post();
            // The number it shows is the number of mines among its neighbours.
            let mut around: Vec<Lit> = Vec::new();
            for a in -1i32..=1 {
                for b in -1i32..=1 {
                    let (nr, nc) = (r as i32 + a, c as i32 + b);
                    if (a, b) != (0, 0) && nr >= 0 && nc >= 0 && nr < rows as i32 && nc < cols as i32 {
                        around.push(mines[nr as usize][nc as usize]);
                    }
                }
            }
            let shown_var = solver.new_bounded_integer(shown, shown);
            if around.is_empty() {
                solver
                    .add_constraint(pumpkin_solver::equals(vec![shown_var.scaled(1)], 0, count))
                    .post();
            } else {
                solver
                    .add_constraint(pumpkin_solver::boolean_equals(
                        vec![1; around.len()], around, shown_var, count))
                    .post();
            }
        }
    }

    let mut m = Model::new();
    m.put("mines", mines);
    m
}
