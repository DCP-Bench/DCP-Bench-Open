from pycsp3 import *

# the cub scouts cannot lie, so all three statements are true; decide who is guilty
# huey, dewey and louie are 1 when guilty and 0 when not
huey = Var(dom={0, 1})
dewey = Var(dom={0, 1})
louie = Var(dom={0, 1})

satisfy(
    # Huey: Dewey and Louie have an equal share, so if one is guilty the other is too
    dewey == louie,
    # Dewey: if Huey is guilty, then Dewey is guilty too
    imply(huey == 1, dewey == 1),
    # Louie: Dewey and Louie are not both guilty
    dewey + louie <= 1,
)
