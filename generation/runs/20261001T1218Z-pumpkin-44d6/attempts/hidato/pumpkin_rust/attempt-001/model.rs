// Hidato: fill the grid with the numbers 1..r*c, keeping the numbers already
// given, so that every two consecutive numbers sit in cells that touch
// horizontally, vertically or diagonally.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    // puzzle[i][j] is the given number in row i, column j; 0 is an empty cell.
    let puzzle = inst.matrix("puzzle");
    let r = puzzle.len();
    let c = puzzle[0].len();
    let cells = r * c;
    let last = cells as i32;

    // x[i][j] is the number in row i, column j.
    let x: Vec<Vec<Var>> = (0..r)
        .map(|_| (0..c).map(|_| solver.new_bounded_integer(1, last)).collect())
        .collect();
    let flat: Vec<Var> = x.iter().flatten().copied().collect();
    // place[k] is the cell (numbered i * c + j) holding number k + 1. It is the
    // inverse of x, introduced so that "k and k + 1 touch" is a constraint on two
    // variables instead of a search over positions.
    let place: Vec<Var> = (0..cells)
        .map(|_| solver.new_bounded_integer(0, last - 1))
        .collect();

    // All the numbers are different, and so are the cells they are placed in.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(flat.clone(), tag)).post();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(place.clone(), tag)).post();

    // Link the two views: the cell holding number k + 1 contains k + 1, and the
    // number in a cell says where that number is placed (both directions are
    // stated so each view propagates to the other).
    let linked = solver.new_constraint_tag();
    for k in 0..cells {
        let number = solver.new_bounded_integer(k as i32 + 1, k as i32 + 1);
        solver
            .add_constraint(pumpkin_solver::element(
                place[k].scaled(1), flat.clone(), number.scaled(1), linked))
            .post();
    }
    for cell in 0..cells {
        let here = solver.new_bounded_integer(cell as i32, cell as i32);
        solver
            .add_constraint(pumpkin_solver::element(
                flat[cell].offset(-1), place.clone(), here.scaled(1), linked))
            .post();
    }

    // The numbers already filled in.
    let given = solver.new_constraint_tag();
    for i in 0..r {
        for j in 0..c {
            if puzzle[i][j] > 0 {
                solver
                    .add_constraint(pumpkin_solver::equals(
                        vec![x[i][j].scaled(1)], puzzle[i][j], given))
                    .post();
            }
        }
    }

    // Consecutive numbers touch: the pair (cell of k, cell of k + 1) must be two
    // different cells at most one row and one column apart. The allowed pairs
    // are listed once from the grid size and used as a table for every k.
    let mut touching: Vec<Vec<i32>> = Vec::new();
    for i in 0..r as i32 {
        for j in 0..c as i32 {
            for a in -1..=1 {
                for b in -1..=1 {
                    let (ni, nj) = (i + a, j + b);
                    if (a != 0 || b != 0) && ni >= 0 && nj >= 0 && ni < r as i32 && nj < c as i32 {
                        touching.push(vec![i * c as i32 + j, ni * c as i32 + nj]);
                    }
                }
            }
        }
    }
    let next_to = solver.new_constraint_tag();
    for k in 0..cells.saturating_sub(1) {
        solver
            .add_constraint(pumpkin_solver::table(
                vec![place[k], place[k + 1]], touching.clone(), next_to))
            .post();
    }

    let mut m = Model::new();
    m.put("x", x);
    m
}
