import itertools
import json

total = 100
coin_numbers = [16, 17, 23, 24, 39, 40]
limits = [total // value for value in coin_numbers]
for bags in itertools.product(*(range(limit + 1) for limit in limits)):
    if sum(count * value for count, value in zip(bags, coin_numbers)) == total:
        print(json.dumps({"bags": list(bags)}))
        break
