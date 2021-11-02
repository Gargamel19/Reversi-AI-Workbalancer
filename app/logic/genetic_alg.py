import random


def mutate(rate, matrix):
    new_matrix = matrix.copy()
    for x in range(len(new_matrix)):
        for y in range(len(new_matrix[x])):
            rand = random.randint(0, 10000)
            int_rate = rate*10000
            if rand < int_rate:
                rand_abweichung = random.randint(-5, 5)
                new_matrix[x][y] += rand_abweichung
    return new_matrix


def crossover(rate, matrix1, matrix2):
    new_matrix = matrix1.copy()
    count = 0
    for x in range(len(new_matrix)):
        for y in range(len(new_matrix[x])):
            rand = random.randint(0, 10000)
            int_rate = rate * 10000
            if rand < int_rate:
                count += 1
                new_matrix[x][y] += matrix2[x][y]
    return new_matrix
