// Flow Free: colour every cell of the board so that matching endpoints are joined
// by pipes that cover the board without crossing. Each endpoint has exactly one
// neighbour of its colour, and every other cell exactly two (it lies inside a
// pipe).
//
// The board comes from the instance (0 = empty cell). The colour range 1..10 is
// the reference's own domain, mirrored here.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let board = inst.matrix("board");
    let rows = board.len();
    let cols = board[0].len();

    let b: Vec<Vec<Var>> = (0..rows)
        .map(|_| (0..cols).map(|_| solver.new_bounded_integer(1, 10)).collect())
        .collect();

    // same[(i, j, k, l)]: cell (i, j) has the colour of its neighbour (k, l).
    let same_colour = solver.new_constraint_tag();
    let endpoints = solver.new_constraint_tag();
    let pipe = solver.new_constraint_tag();
    let one = solver.new_bounded_integer(1, 1);
    let two = solver.new_bounded_integer(2, 2);
    for i in 0..rows {
        for j in 0..cols {
            let mut neighbours: Vec<(usize, usize)> = Vec::new();
            if i > 0 {
                neighbours.push((i - 1, j));
            }
            if i + 1 < rows {
                neighbours.push((i + 1, j));
            }
            if j > 0 {
                neighbours.push((i, j - 1));
            }
            if j + 1 < cols {
                neighbours.push((i, j + 1));
            }
            let same: Vec<Lit> = neighbours
                .iter()
                .map(|&(k, l)| {
                    let eq = solver.new_literal();
                    solver
                        .add_constraint(pumpkin_solver::equals(
                            vec![b[i][j].scaled(1), b[k][l].scaled(-1)],
                            0,
                            same_colour,
                        ))
                        .reify(eq);
                    eq
                })
                .collect();
            let weights = vec![1; same.len()];
            if board[i][j] != 0 {
                // An endpoint keeps its colour and continues into one neighbour.
                solver.add_constraint(pumpkin_solver::equals(vec![b[i][j]], board[i][j], endpoints)).post();
                solver.add_constraint(pumpkin_solver::boolean_equals(weights, same, one, endpoints)).post();
            } else {
                // An empty cell lies on a pipe: two neighbours share its colour.
                solver.add_constraint(pumpkin_solver::boolean_equals(weights, same, two, pipe)).post();
            }
        }
    }

    let mut m = Model::new();
    m.put("B", b);
    m
}
