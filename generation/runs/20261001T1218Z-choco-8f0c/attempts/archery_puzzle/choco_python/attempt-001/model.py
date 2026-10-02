# Archery puzzle: choose how many arrows to put on each target so that the total
# score gets as close as possible to the target score.
from pychoco.model import Model


def build(instance):
    targets = instance["targets"]  # points scored by one hit on each target
    target_score = instance["target_score"]  # the total score the archer aims for
    n = len(targets)

    model = Model()

    # hits[i] = number of arrows that hit target i (as many arrows as she pleases;
    # the upper bound target_score is the one the reference model declares)
    hits = [model.intvar(0, target_score, name=f"hits_{i}") for i in range(n)]
    # total score of all arrows
    score = model.intvar(0, 2 * target_score, name="score")
    # how far the total score is from the target score
    deviation = model.intvar(0, 2 * target_score, name="deviation")

    # the score is the sum over targets of hits times the points of that target
    model.scalar(hits, targets, "=", score).post()

    # the deviation is the distance between the score and the target score
    model.distance(score, model.intvar(target_score, target_score), "=", deviation).post()

    # get as close as possible to the target score
    return model, {"hits": hits}, ("minimize", deviation)
