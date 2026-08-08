import itertools
import json

for guilty in itertools.product([False, True], repeat=6):
    artie, bill, crackitt, dodgy, edgy, fingers = guilty
    guilty_count = sum(guilty)
    if not (1 <= guilty_count <= 2):
        continue
    statements = [
        not artie,
        crackitt,
        not crackitt,
        (not crackitt) or bill,
        guilty_count != 1,
        artie and dodgy and guilty_count == 2,
    ]
    if all(statement == (not is_guilty) for statement, is_guilty in zip(statements, guilty)):
        print(json.dumps({
            "artie": artie,
            "bill": bill,
            "crackitt": crackitt,
            "dodgy": dodgy,
            "edgy": edgy,
            "fingers": fingers,
        }))
        break
