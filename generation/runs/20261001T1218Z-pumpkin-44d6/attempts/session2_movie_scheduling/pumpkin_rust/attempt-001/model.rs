// Movie scheduling: an actor is offered movies, each filmed over a period from
// its first to its last day, and cannot accept two movies whose periods overlap.
// Accept as many movies as possible.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    // movies[i] = [title, first day, last day]. A row mixes a string with
    // integers, so the field is read from the raw JSON value.
    let movies: Vec<(i64, i64)> = inst
        .get("movies")
        .as_array()
        .expect("movies: expected an array")
        .iter()
        .map(|row| {
            let items = row.as_array().expect("movies row: expected [title, start, end]");
            (
                items[1].as_i64().expect("movies row: start must be an integer"),
                items[2].as_i64().expect("movies row: end must be an integer"),
            )
        })
        .collect();
    let n = movies.len();

    // selected_movies[i] is true when movie i is accepted.
    let selected_movies: Vec<Lit> = (0..n).map(|_| solver.new_literal()).collect();

    // Two movies whose filming periods overlap (each ends on or after the day the
    // other starts) cannot both be accepted.
    let no_overlap = solver.new_constraint_tag();
    for i in 0..n {
        for j in (i + 1)..n {
            if movies[i].1 >= movies[j].0 && movies[j].1 >= movies[i].0 {
                solver
                    .add_constraint(pumpkin_solver::clause(
                        vec![!selected_movies[i], !selected_movies[j]], no_overlap))
                    .post();
            }
        }
    }

    // The objective is the number of accepted movies.
    let accepted = solver.new_bounded_integer(0, n as i32);
    let tag = solver.new_constraint_tag();
    if n > 0 {
        solver
            .add_constraint(pumpkin_solver::boolean_equals(
                vec![1; n], selected_movies.clone(), accepted, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("selected_movies", selected_movies);
    m.maximise(accepted);
    m
}
