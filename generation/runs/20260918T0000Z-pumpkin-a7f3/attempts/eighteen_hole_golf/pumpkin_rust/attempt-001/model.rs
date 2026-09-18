// Eighteen holes of par 3, 4 or 5 adding up to a par-72 course.
// The course specification is the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, cp: &mut Cp) -> Model {
    let num_holes = 18;
    let total_length = 72;

    let holes = cp.ints(num_holes, 3, 5);
    cp.eq(terms(&holes), total_length);

    let mut m = Model::new();
    m.put("holes", holes);
    m
}
