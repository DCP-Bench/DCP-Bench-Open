// Magic hexagon (CSPLib 023): place the numbers 1..NUM_CELLS in the cells of a
// hexagon with rows of 3, 4, 5, 4, 3 cells (A..S) so that each of the 15 lines,
// the rows and the diagonals in both directions, sums to MAGIC_SUM.
//
// NUM_CELLS and MAGIC_SUM come from the instance; the 15 lines are the shape of
// the order-3 hexagon, mirrored from the reference.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let cells = inst.size("NUM_CELLS");
    let magic = inst.int("MAGIC_SUM");

    let ld: Vec<Var> = (0..cells).map(|_| solver.new_bounded_integer(1, cells as i32)).collect();

    // Every number 1..NUM_CELLS is used exactly once.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(ld.clone(), tag)).post();

    // Cells by position:      A B C / D E F G / H I J K L / M N O P / Q R S
    //                         0 1 2   3 4 5 6   7 8 9 10 11 12 13 14 15 16 17 18
    let lines: [&[usize]; 15] = [
        // rows
        &[0, 1, 2],
        &[3, 4, 5, 6],
        &[7, 8, 9, 10, 11],
        &[12, 13, 14, 15],
        &[16, 17, 18],
        // diagonals from top-left to bottom-right
        &[0, 3, 7],
        &[1, 4, 8, 12],
        &[2, 5, 9, 13, 16],
        &[6, 10, 14, 17],
        &[11, 15, 18],
        // diagonals from top-right to bottom-left
        &[2, 6, 11],
        &[1, 5, 10, 15],
        &[0, 4, 9, 14, 18],
        &[3, 8, 13, 17],
        &[7, 12, 16],
    ];

    // Every line sums to the magic constant.
    let magic_lines = solver.new_constraint_tag();
    for line in lines.iter() {
        let vars: Vec<Var> = line.iter().map(|&c| ld[c]).collect();
        solver.add_constraint(pumpkin_solver::equals(vars, magic, magic_lines)).post();
    }

    let mut m = Model::new();
    m.put("LD", ld);
    m
}
