import json
n = 10
sequence = [-1 if i % 2 == 0 else 1 for i in range(n)]
def energy(seq):
    return sum(
        sum(seq[i] * seq[(i + shift) % n] for i in range(n)) ** 2
        for shift in range(1, n)
    )
print(json.dumps({'sequence': sequence, 'E': energy(sequence)}))