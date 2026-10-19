"""Every subset of the weights 2, 3, 4, 5, 6 that sums to exactly 9."""
from idp_engine import IDP, Theory

weights = [2, 3, 4, 5, 6]
target = 9

KB = """
vocabulary V {
    type Item <: Int
    weight: Item -> Int
    target: () -> Int
    pick: Item -> Bool              // the decision
    size: () -> Int                 // auxiliary, fixed by pick
}
theory T: V {
    // the chosen weights add up to the target
    sum{{ weight(i) | i in Item: pick(i) }} = target().
    // the auxiliary count is determined by pick, so it cannot multiply the models
    size() = #{ i in Item: pick(i) }.
}
"""

# The data goes into a structure written from Python values.
structure = "structure S: V {\n"
structure += f"    Item := {{0..{len(weights) - 1}}}.\n"
structure += "    weight := {" + ", ".join(f"{i}->{w}" for i, w in enumerate(weights)) + "}.\n"
structure += f"    target := {target}.\n}}\n"

kb = IDP.from_str(KB + structure)
theory = Theory(*kb.get_blocks("T, S"))

count = 0
for model in theory.expand(max=0, timeout_seconds=0):
    if isinstance(model, str):      # the closing message, e.g. "\nNo more models."
        print(model.strip())
        break
    count += 1
    # a Boolean value is an Expression and always truthy: compare its text
    chosen = [w for i, w in enumerate(weights) if str(model[f"pick({i})"].value) == "true"]
    print(f"solution {count}: {chosen} (size {model['size()'].value})")
print(f"Solutions: {count}")
