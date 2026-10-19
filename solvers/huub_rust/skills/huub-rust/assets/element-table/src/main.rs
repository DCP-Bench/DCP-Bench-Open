use huub::model::Model;
use huub::solver::{Solver, Status};

fn main() {
    let mut m = Model::default();

    // A 1-based index into a constant array: element is 0-based, so index with i - 1.
    let i = m.new_int_decision(1..=3);
    let price = m.element(vec![10i64, 20, 30]).index(i - 1).define();

    // Allowed pairs, as a positive table.
    let pair = m.new_int_decisions(2, 0..=5);
    m.table(pair.clone())
        .values(vec![vec![1, 2], vec![2, 3], vec![4, 4]])
        .post()
        .unwrap();

    let (mut solver, map): (Solver, _) = m.lower().to_solver().unwrap();
    let outputs = vec![
        map.get(&mut solver, i),
        map.get(&mut solver, price),
        map.get(&mut solver, pair[0]),
        map.get(&mut solver, pair[1]),
    ];
    let mut rows = 0;
    let status = solver
        .solve()
        .all_solutions(outputs)
        .on_solution(|_| rows += 1)
        .satisfy();
    println!("Solutions: {rows} ({status:?})");
    assert!(matches!(status, Status::Complete));
}
