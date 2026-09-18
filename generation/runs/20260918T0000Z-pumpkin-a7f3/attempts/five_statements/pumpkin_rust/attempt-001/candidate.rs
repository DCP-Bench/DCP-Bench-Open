// Five statements, each claiming how many of the five are false.
// The statements are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, cp: &mut Cp) -> Model {
    let n = 5;
    let statements = cp.bools(n);

    // Statement i says "exactly i+1 of us are false". With n statements, that is
    // n - true == i + 1, so it holds exactly when the number of true ones is
    // n - i - 1.
    for i in 0..n {
        cp.iff_eq(statements[i], terms(&statements), (n - i - 1) as i32);
    }

    let mut m = Model::new();
    m.put("statements", statements);
    m
}
