import json
ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4]
candies = [1 for _ in ratings]
for idx in range(1, len(ratings)):
    if ratings[idx] > ratings[idx - 1]:
        candies[idx] = candies[idx - 1] + 1
for idx in range(len(ratings) - 2, -1, -1):
    if ratings[idx] > ratings[idx + 1]:
        candies[idx] = max(candies[idx], candies[idx + 1] + 1)
print(json.dumps({'z': sum(candies)}))