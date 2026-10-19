use huub::model::Model;
use huub::solver::{Solver, Status};

fn main() {
    // Huub has no circuit constraint. `next[i]` is the successor of node i. The
    // decomposition makes the successors all different, and a visiting order that
    // starts at node 0 follows `next` through every node.
    let n = 5usize;
    let mut m = Model::default();
    let next = m.new_int_decisions(n, 0..=(n as i64 - 1));
    let order = m.new_int_decisions(n, 0..=(n as i64 - 1));
    m.unique(next.clone()).post().unwrap();
    m.unique(order.clone()).post().unwrap();
    m.linear(order[0]).eq(0).post().unwrap();
    for (i, succ) in next.iter().enumerate() {
        m.linear(*succ).ne(i as i64).post().unwrap();
    }
    for k in 0..n - 1 {
        m.element(next.clone()).index(order[k]).result(order[k + 1]).post().unwrap();
    }
    m.element(next.clone()).index(order[n - 1]).result(order[0]).post().unwrap();

    // Enumerate over the successors only: `order` is auxiliary.
    let (mut solver, map): (Solver, _) = m.lower().to_solver().unwrap();
    let outputs: Vec<_> = next.iter().map(|&v| map.get(&mut solver, v)).collect();
    let mut tours = 0;
    let status = solver
        .solve()
        .all_solutions(outputs)
        .on_solution(|_| tours += 1)
        .satisfy();
    println!("Tours: {tours} ({status:?})");
    assert!(matches!(status, Status::Complete));
}
