use huub::model::Model;
use huub::solver::{Solver, Status};

fn main() {
    // Three tasks on a resource of capacity 2: usages 1, 2 and 1.
    let duration = vec![3i64, 2, 2];
    let usage = vec![1i64, 2, 1];

    let mut m = Model::default();
    let start = m.new_int_decisions(3, 0..=10);
    m.cumulative()
        .start_times(start.clone())
        .durations(duration.clone())
        .usages(usage)
        .capacity(2)
        .post()
        .unwrap();

    let makespan = m.new_int_decision(0..=20);
    for (s, d) in start.iter().zip(&duration) {
        m.linear(*s + *d).le(makespan).post().unwrap();
    }

    let (mut solver, map): (Solver, _) = m.lower().to_solver().unwrap();
    let objective = map.get(&mut solver, makespan);
    match solver.solve().minimize(objective) {
        (Status::Complete, Some(best)) => println!("Makespan: {best}"),
        (status, _) => println!("no proven optimum: {status:?}"),
    }
}
