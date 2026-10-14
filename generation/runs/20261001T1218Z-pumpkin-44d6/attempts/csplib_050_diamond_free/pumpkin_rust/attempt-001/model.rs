// Diamond-free graphs: a simple undirected graph on N vertices in which no four
// vertices span five or more edges, every vertex has a positive degree that is a
// multiple of 3, and the degrees add up to a multiple of 12.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("N"); // number of vertices
    let n_i32 = n as i32;

    // matrix[i][j] is true when vertices i and j are adjacent.
    let matrix: Vec<Vec<Lit>> = (0..n)
        .map(|_| (0..n).map(|_| solver.new_literal()).collect())
        .collect();

    // No vertex is adjacent to itself.
    let no_loops = solver.new_constraint_tag();
    for i in 0..n {
        solver
            .add_constraint(pumpkin_solver::clause(vec![!matrix[i][i]], no_loops))
            .post();
    }

    // The graph is undirected: matrix[i][j] and matrix[j][i] are the same.
    let symmetric = solver.new_constraint_tag();
    for i in 0..n {
        for j in (i + 1)..n {
            solver
                .add_constraint(pumpkin_solver::clause(
                    vec![!matrix[i][j], matrix[j][i]], symmetric))
                .post();
            solver
                .add_constraint(pumpkin_solver::clause(
                    vec![matrix[i][j], !matrix[j][i]], symmetric))
                .post();
        }
    }

    // Every vertex has a degree greater than zero that is a multiple of 3. The
    // degree of a vertex is at most n - 1, so the domain is 3, 6, 9, ... up to there.
    let degree_values: Vec<i32> = (1..n_i32).filter(|d| d % 3 == 0).collect();
    let degree: Vec<Var> = (0..n)
        .map(|_| solver.new_sparse_integer(degree_values.clone()))
        .collect();
    let row_sum = solver.new_constraint_tag();
    for i in 0..n {
        solver
            .add_constraint(pumpkin_solver::boolean_equals(
                vec![1; n], matrix[i].clone(), degree[i], row_sum))
            .post();
    }

    // The sum of the whole matrix, which is the sum of the degrees, is a multiple
    // of 12: it equals 12 * blocks for some whole number blocks.
    let blocks = solver.new_bounded_integer(0, n_i32 * (n_i32 - 1) / 12);
    let mut terms: Vec<Term> = degree.iter().map(|d| d.scaled(1)).collect();
    terms.push(blocks.scaled(-12));
    let total = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(terms, 0, total))
        .post();

    // Diamond-free: among any four vertices there are at most four of the six
    // possible edges.
    let diamond = solver.new_constraint_tag();
    for a in 0..n {
        for b in (a + 1)..n {
            for c in (b + 1)..n {
                for d in (c + 1)..n {
                    let edges = vec![
                        matrix[a][b], matrix[a][c], matrix[a][d],
                        matrix[b][c], matrix[b][d], matrix[c][d],
                    ];
                    solver
                        .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                            vec![1; 6], edges, 4, diamond))
                        .post();
                }
            }
        }
    }

    let mut m = Model::new();
    m.put("matrix", matrix);
    m
}
