use huub::model::Model;

fn main() {
    // Three values that must all differ, each in 0..=1: no solution exists.
    // The conflict is found by `post()` itself, which returns Err.
    let mut m = Model::default();
    let x = m.new_int_decisions(3, 0..=1);
    if m.unique(x.clone()).post().is_err() {
        println!("infeasible: a constraint conflicts when it is posted");
        return;
    }
    println!("posted without conflict; lowering or solving decides");
}
