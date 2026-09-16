from pychoco.model import Model


def build(instance):
    """Car selection: match participants to cars they are interested in, at
    most one car each and one participant per car, maximizing the matches.
    """
    possible = instance["possible_assignments"]
    participants = len(possible)
    cars = len(possible[0]) if participants else 0

    model = Model()
    assign = [[model.boolvar(name=f"a{i}_{j}") for j in range(cars)]
              for i in range(participants)]

    for i in range(participants):
        for j in range(cars):
            # An assignment is only available where the participant is interested.
            model.arithm(assign[i][j], "<=", possible[i][j]).post()
        model.sum(assign[i], "<=", 1).post()
    for j in range(cars):
        model.sum([assign[i][j] for i in range(participants)], "<=", 1).post()

    flat = [assign[i][j] for i in range(participants) for j in range(cars)]
    matched = model.intvar(0, participants * cars, name="matched")
    model.sum(flat, "=", matched).post()

    return model, {"assignments": assign}, ("maximize", matched)
