import matplotlib.pyplot as plt
from model import TrafficModel
import pandas as pd

def run_batch(runs=10, steps=300, spawn_rate=0.15):
    results = []

    for r in range(runs):
        model = TrafficModel(spawn_rate=spawn_rate)

        for i in range(steps):
            model.step()

        df = model.datacollector.get_model_vars_dataframe()
        df["Run"] = r
        results.append(df)

    return pd.concat(results)


# ---------------------------
# Experiment: vary spawn rate
# ---------------------------
spawn_rates = [0.05, 0.15, 0.30]
all_data = []

for rate in spawn_rates:
    print("Running experiment for spawn rate:", rate)
    df = run_batch(runs=5, steps=300, spawn_rate=rate)
    df["SpawnRate"] = rate
    all_data.append(df)

all_data = pd.concat(all_data)

# ---------------------------
# Plot results
# ---------------------------
plt.figure(figsize=(10, 5))

for rate in spawn_rates:
    subset = all_data[all_data["SpawnRate"] == rate]
    avg_cars_passed = subset.groupby("Run")["CarsPassed"].max()
    plt.plot(avg_cars_passed.values, label=f"Rate {rate}")

plt.title("Cars Passed vs Spawn Rate")
plt.ylabel("Cars Passed")
plt.xlabel("Run Number")
plt.legend()
plt.show()