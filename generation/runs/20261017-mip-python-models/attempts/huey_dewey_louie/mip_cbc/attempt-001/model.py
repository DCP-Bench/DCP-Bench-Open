# Huey, Dewey and Louie: who (if any) is guilty, given that all three statements are true
# (cub scouts cannot tell a lie). Satisfaction problem; outputs huey, dewey, louie are Booleans.
import mip


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    huey = model.add_var("huey", var_type=mip.BINARY)
    dewey = model.add_var("dewey", var_type=mip.BINARY)
    louie = model.add_var("louie", var_type=mip.BINARY)

    # Huey: "Dewey and Louie has equal share in it; if one is guilty, so is the other."
    model.add_constr(dewey - louie == 0)

    # Dewey: "If Huey is guilty, then so am I."
    model.add_constr(huey - dewey <= 0)

    # Louie: "Dewey and I are not both guilty."
    model.add_constr(dewey + louie <= 1)

    return model, {"huey": huey, "dewey": dewey, "louie": louie}
