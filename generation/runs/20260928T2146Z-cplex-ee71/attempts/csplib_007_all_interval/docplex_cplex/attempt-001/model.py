"""All-interval series: order 0..n-1 so that the distances between neighbours are 1..n-1, each once."""
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]
    places = range(n)
    gaps = range(n - 1)
    pitches = range(n)
    intervals = range(1, n)

    model = Model("all_interval")

    # note[i, v] is 1 when position i holds pitch class v: the series is a
    # permutation of 0..n-1.
    note = model.binary_var_matrix(places, pitches, name="note")
    for i in places:
        model.add_constraint(model.sum(note[i, v] for v in pitches) == 1, ctname=f"place_{i}")
    for v in pitches:
        model.add_constraint(model.sum(note[i, v] for i in places) == 1, ctname=f"pitch_{v}")
    x = [model.sum(v * note[i, v] for v in pitches) for i in places]

    # interval[i, d] is 1 when the i-th interval is d: the intervals are a
    # permutation of 1..n-1.
    interval = model.binary_var_matrix(gaps, intervals, name="interval")
    for i in gaps:
        model.add_constraint(model.sum(interval[i, d] for d in intervals) == 1, ctname=f"gap_{i}")
    for d in intervals:
        model.add_constraint(model.sum(interval[i, d] for i in gaps) == 1, ctname=f"interval_{d}")
    diffs = [model.sum(d * interval[i, d] for d in intervals) for i in gaps]

    # Each interval is the distance between neighbouring notes.
    for i in gaps:
        model.add_constraint(diffs[i] == model.abs(x[i + 1] - x[i]), ctname=f"distance_{i}")

    return model, {"x": x, "diffs": diffs}
