"""A parameter-free problem still implements the same instance interface."""
import cpmpy as cp


def build(instance):
    men, women, children = cp.intvar(0, 100, shape=3)
    model = cp.Model(men + women + children == 100,
                     6 * men + 4 * women + children == 200,
                     5 * men == women)
    return model, {"men": men, "women": women, "children": children}
