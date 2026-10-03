// Balanced incomplete block design: arrange v objects into b blocks, given as a
// v-by-b 0/1 incidence matrix, so that every block holds k objects, every
// object lies in r blocks, and every two distinct objects share exactly l blocks.

type Tag = pumpkin_solver::core::proof::ConstraintTag;

// Post "exactly `count` of these literals are true".
fn exactly(solver: &mut Solver, lits: Vec<Lit>, count: i32, tag: Tag) {
    let total = solver.new_bounded_integer(count, count);
    let ones = vec![1; lits.len()];
    solver
        .add_constraint(pumpkin_solver::boolean_equals(ones, lits, total, tag))
        .post();
}

fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let v = inst.size("v"); // number of objects
    let b = inst.size("b"); // number of blocks
    let r = inst.int("r"); // number of blocks each object occurs in
    let k = inst.int("k"); // number of objects in each block
    let l = inst.int("l"); // number of blocks that every pair of objects shares

    // matrix[i][j] is true when object i is in block j.
    let matrix: Vec<Vec<Lit>> = (0..v)
        .map(|_| (0..b).map(|_| solver.new_literal()).collect())
        .collect();

    // Every row (object) adds up to r.
    let object_tag = solver.new_constraint_tag();
    for i in 0..v {
        exactly(solver, matrix[i].clone(), r, object_tag);
    }

    // Every column (block) adds up to k.
    let block_tag = solver.new_constraint_tag();
    for j in 0..b {
        let column: Vec<Lit> = (0..v).map(|i| matrix[i][j]).collect();
        exactly(solver, column, k, block_tag);
    }

    // The scalar product of every pair of rows adds up to l: the two objects
    // are together in exactly l blocks. together[j] is true exactly when both
    // objects are in block j (an "and" of two Booleans, as three clauses), and
    // these are counted.
    let and_tag = solver.new_constraint_tag();
    let pair_tag = solver.new_constraint_tag();
    for i in 0..v {
        for i2 in (i + 1)..v {
            let mut together: Vec<Lit> = Vec::new();
            for j in 0..b {
                let t = solver.new_literal();
                let (x, y) = (matrix[i][j], matrix[i2][j]);
                for clause in [vec![!t, x], vec![!t, y], vec![t, !x, !y]] {
                    solver
                        .add_constraint(pumpkin_solver::clause(clause, and_tag))
                        .post();
                }
                together.push(t);
            }
            exactly(solver, together, l, pair_tag);
        }
    }

    let mut m = Model::new();
    m.put("matrix", matrix);
    m
}
