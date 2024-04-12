import numpy as np

path = r"A_result.txt"

costs = []

with open(path, 'r') as f:
    for line in f.readlines():
        data, cost = line.split()
        if data.startswith("A-"):
            costs.append([float(cost) if cost != "None" else np.nan])
        else:
            costs[-1].append(float(cost) if cost != "None" else np.nan)

costs = np.array(costs)
print(np.nanmean(costs, axis=0))