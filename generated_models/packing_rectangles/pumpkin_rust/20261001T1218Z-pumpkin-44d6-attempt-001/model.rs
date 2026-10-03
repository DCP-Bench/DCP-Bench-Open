// Rectangle packing: place every item (a rectangle of given width and height)
// inside an enclosing rectangle without overlaps, and make the area of the
// enclosing rectangle as small as possible.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let widths = inst.ints("widths");
    let heights = inst.ints("heights");
    let n = widths.len();

    // The enclosing rectangle is at least as wide as the widest item and at most
    // as wide as all items side by side; likewise for its height (the
    // reference's bounds).
    let min_x = *widths.iter().max().unwrap();
    let max_x: i32 = widths.iter().sum();
    let min_y = *heights.iter().max().unwrap();
    let max_y: i32 = heights.iter().sum();

    // pos_x[i], pos_y[i] is the bottom-left corner of item i.
    let pos_x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, max_x)).collect();
    let pos_y: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, max_y)).collect();
    let total_x = solver.new_bounded_integer(min_x, max_x);
    let total_y = solver.new_bounded_integer(min_y, max_y);

    // Every item lies within the enclosing rectangle:
    // pos_x[i] + width[i] <= total_x and pos_y[i] + height[i] <= total_y.
    let inside = solver.new_constraint_tag();
    for i in 0..n {
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![pos_x[i].scaled(1), total_x.scaled(-1)], -widths[i], inside))
            .post();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![pos_y[i].scaled(1), total_y.scaled(-1)], -heights[i], inside))
            .post();
    }

    // No overlap: every two items lie fully left of, right of, below or above
    // each other. Each of the four relations gets a literal that implies it,
    // and at least one of the four literals holds.
    let apart = solver.new_constraint_tag();
    let side = solver.new_constraint_tag();
    for i in 0..n {
        for j in (i + 1)..n {
            let relations = [
                (pos_x[i], widths[i], pos_x[j]), // i left of j
                (pos_x[j], widths[j], pos_x[i]), // j left of i
                (pos_y[i], heights[i], pos_y[j]), // i below j
                (pos_y[j], heights[j], pos_y[i]), // j below i
            ];
            let mut options: Vec<Lit> = Vec::new();
            for (first, size, second) in relations {
                let lit = solver.new_literal();
                // first + size <= second
                solver
                    .add_constraint(pumpkin_solver::less_than_or_equals(
                        vec![first.scaled(1), second.scaled(-1)], -size, side))
                    .implied_by(lit);
                options.push(lit);
            }
            solver.add_constraint(pumpkin_solver::clause(options, apart)).post();
        }
    }

    // The objective is the area total_x * total_y.
    let area = solver.new_bounded_integer(min_x * min_y, max_x * max_y);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::times(total_x, total_y, area, tag))
        .post();

    // Implied bound, added to help prove optimality: the items do not overlap,
    // so the area is at least the sum of the items' areas.
    let item_area: i32 = (0..n).map(|i| widths[i] * heights[i]).sum();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(vec![area.scaled(-1)], -item_area, tag))
        .post();

    let mut m = Model::new();
    m.put("pos_x", pos_x);
    m.put("pos_y", pos_y);
    m.put("total_x", total_x);
    m.put("total_y", total_y);
    m.minimise(area);
    m
}
