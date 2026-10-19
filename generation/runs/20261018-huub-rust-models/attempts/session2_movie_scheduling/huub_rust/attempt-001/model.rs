// session2_movie_scheduling: choose movies whose filming periods do not overlap,
// maximising the number of movies chosen. Each movie is [title, first day, last day];
// two movies overlap when their periods share at least one day.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let rows = inst.get("movies").as_array().expect("movies must be an array");
    let n = rows.len();
    let mut starts: Vec<i64> = Vec::with_capacity(n);
    let mut ends: Vec<i64> = Vec::with_capacity(n);
    for r in rows {
        let a = r.as_array().expect("each movie must be an array");
        starts.push(a[1].as_i64().expect("first day must be an integer"));
        ends.push(a[2].as_i64().expect("last day must be an integer"));
    }

    let sel: Vec<View<bool>> = (0..n).map(|_| m.new_bool_decision()).collect();

    // Two movies whose filming periods overlap cannot both be selected.
    for i in 0..n {
        for j in (i + 1)..n {
            if starts[i] <= ends[j] && starts[j] <= ends[i] {
                let pair = vec![sel[i], sel[j]].into_iter().sum::<IntLinearExp>();
                m.linear(pair).le(1).post()?;
            }
        }
    }

    // The number of selected movies is the objective.
    let total = sel.iter().copied().sum::<IntLinearExp>();
    let obj = m.new_int_decision(0..=(n as i64));
    m.linear(total).eq(obj).post()?;

    let mut out = Out::new();
    out.put("selected_movies", sel);
    out.maximise(obj);
    Ok(out)
}
