from sklearn import tree


input_flags = [
    [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1],
    [0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1],
    [0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1],
    [0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1],
    [0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1]
]
relevant_flags = [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
output_flags = [
    [0, 1, 0, 1, 0],
    [0, 0, 1, 1, 0],
    [0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0],
    [1, 0, 1, 0, 1],
    [0, 1, 0, 1, 0]
]
test_flags = [1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1]

training_weights = []
for input_vector in input_flags:
    i = 0
    weight = 0.0
    for relevant_flag in relevant_flags:
        if relevant_flag == 1 and input_vector[i] == 0:
            weight += 1.0
        else:
            weight += 0.1
        i += 1
    training_weights.append(weight)

dt = tree.DecisionTreeClassifier()
dt.fit(input_flags, output_flags, training_weights)
output = dt.predict([test_flags])
print(output)
"""[[0 1 0 1 0]]"""
