use huub::model::Model;
use huub::solver::{Solver, Status};

fn main() {
    let mut m = Model::default();
    let x = m.new_int_decision(0..=10);
    let y = m.new_int_decision(0..=10);
    m.linear(x + y).le(4).post().unwrap();
    m.linear(x + y * 3).le(6).post().unwrap();

    // The objective is a view tied to the expression by a constraint.
    let profit = m.new_int_decision(0..=100);
    m.linear(x * 3 + y * 2).eq(profit).post().unwrap();

    let (mut s, map): (Solver, _) = m.lower().to_solver().unwrap();
    let objective = map.get(&mut s, profit);
    // maximize must be the first solve on this solver.
    match s.solve().maximize(objective) {
        (Status::Complete, Some(best)) => println!("Optimum: {best}"),
        (status, _) => println!("no proven optimum: {status:?}"),
    }
}
