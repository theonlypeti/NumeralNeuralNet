from collections import defaultdict
import pandas as pd

dd = defaultdict(int)
from utils.prune_empty import prune_empty
numbers = prune_empty("output.csv")
for row in range(numbers.shape[0]):
    nums = numbers.loc[row]
    num = numbers.loc[row].iloc[-1]
    dd[num] += 1

print("by label:")
print("\n".join(f"{k}: {v}" for k, v in sorted(dd.items(), key=lambda x: x[0], reverse=False)))
print("by amount:")
print("\n".join(f"{k}: {v}" for k, v in sorted(dd.items(), key=lambda x: x[1], reverse=True)))