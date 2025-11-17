# Traffic Simulation with Pedestrian Crossing

An agent-based traffic simulation built with [Mesa](https://mesa.readthedocs.io/) that models cars and pedestrians interacting at a traffic intersection with a traffic light system.

## Real-World Problems Solved

This simulation addresses several critical real-world transportation and urban planning challenges:

### 🎯 **Traffic Flow Optimization**
- **Problem**: Urban intersections experience congestion, leading to delays and fuel waste
- **Solution**: Test different traffic light timing strategies to find optimal green/red durations that maximize throughput while minimizing wait times
- **Application**: City traffic engineers can use this model to optimize signal timing before implementing costly real-world changes

### 🚶 **Pedestrian Safety & Mobility**
- **Problem**: Pedestrians face safety risks and long waiting times at intersections
- **Solution**: Model pedestrian crossing behavior and evaluate how different signal timing affects pedestrian wait times and crossing success rates
- **Application**: Urban planners can design safer crosswalks and optimize pedestrian signal timing to improve walkability

### 📊 **Traffic Management Strategy Testing**
- **Problem**: Implementing traffic management solutions (new signals, crosswalks, timing changes) is expensive and disruptive
- **Solution**: Simulate and evaluate strategies virtually before real-world implementation
- **Application**: Test scenarios like "What happens if we increase green light duration?" or "How does pedestrian volume affect car throughput?"

### 🏙️ **Urban Planning & Infrastructure Design**
- **Problem**: New developments need to predict traffic impact, but real-world testing is impossible
- **Solution**: Model traffic patterns to understand how new roads, intersections, or buildings will affect local traffic
- **Application**: City planners can evaluate infrastructure proposals and make data-driven decisions

### 🔬 **Traffic Research & Education**
- **Problem**: Understanding complex traffic dynamics requires hands-on experimentation
- **Solution**: Provides an interactive platform to study agent-based modeling, traffic flow theory, and intersection behavior
- **Application**: Researchers and students can experiment with traffic scenarios and learn about system dynamics

### 📈 **Performance Metrics & Analytics**
- **Problem**: Real-world traffic data collection is time-consuming and expensive
- **Solution**: Generate comprehensive metrics (travel times, queue lengths, waiting times) instantly for analysis
- **Application**: Analyze how different parameters (traffic volume, signal timing) affect overall system performance

### 🌍 **Sustainable Transportation Planning**
- **Problem**: Cities need to balance car traffic with pedestrian-friendly infrastructure for sustainability
- **Solution**: Quantify trade-offs between vehicle throughput and pedestrian accessibility
- **Application**: Evaluate if making intersections more pedestrian-friendly significantly impacts vehicle traffic

### ⚡ **What-If Scenario Analysis**
- **Problem**: Cities need to understand impact of events (rush hours, construction, policy changes)
- **Solution**: Model different scenarios by adjusting spawn rates, signal timing, and pedestrian volume
- **Application**: "What if pedestrian traffic doubles?" or "How does rush hour traffic affect intersection efficiency?"

### 💡 **Key Benefits**
- **Cost-Effective**: Test solutions without expensive real-world trials
- **Risk-Free**: Experiment safely without disrupting actual traffic
- **Fast**: Get results in minutes instead of weeks of data collection
- **Educational**: Understand traffic dynamics through visualization
- **Data-Driven**: Make decisions based on quantitative metrics

## Features

### 🚗 **Cars**
- Cars spawn on the left side of the road and move right
- Cars stop at red traffic lights
- Cars avoid collisions with other vehicles
- Cars yield to pedestrians crossing the road
- Automatically pause only before the light when an ambulance is approaching (cars already past the light keep moving)
- Real-time color coding based on waiting time:
  - **Blue**: Moving freely
  - **Orange**: Short wait
  - **Red**: Long wait

### 🚶 **Pedestrians**
- Pedestrians spawn at the top or bottom of the road
- Pedestrians move horizontally to reach the intersection
- Pedestrians wait for WALK signal to cross vertically
- Walk phase automatically appears when pedestrians arrive, lasts a configurable duration, then instantly returns to green for cars
- Real-time visualization:
  - **Cyan**: Walking to intersection
  - **Yellow**: Waiting at intersection
  - **Lime**: Actively crossing
- Pedestrians already past the light keep moving even during emergency events

### 🚦 **Traffic Light System**
- Default state stays GREEN for cars; turns RED only for short WALK phases or when an ambulance demands priority
- Emergency override halts cars/pedestrians only while the ambulance crosses the intersection, then instantly returns to normal
- WALK/DON'T WALK text labels rendered with large, high-contrast fonts for clarity

### 🚑 **Emergency Vehicle Priority**
- `EmergencyVehicleAgent` spawns periodically and requests a priority corridor
- Cars and pedestrians before the light pause; agents already past the light keep moving so the road clears quickly
- Once the ambulance clears the intersection, normal traffic resumes automatically

### 📊 **Real-time Metrics**
- **Cars Passed**: Total number of cars that exited the grid
- **Average Travel Time**: Mean time for cars to traverse the road
- **Average Waiting Time**: Mean time cars spend waiting
- **Queue Length**: Number of cars waiting before intersection
- **Pedestrians Crossed**: Total pedestrians who completed crossing
- **Average Pedestrian Time**: Mean time for pedestrians to complete journey
- **Pedestrian Wait Time**: Average time pedestrians wait at intersection
- **EmergencyActive**: Binary indicator showing when a priority override is active
- **EmergenciesCleared**: Total ambulances that successfully passed through

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd traffic_sim
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv traffic_env
   ```

3. **Activate the virtual environment**
   
   On macOS/Linux:
   ```bash
   source traffic_env/bin/activate
   ```
   
   On Windows:
   ```bash
   traffic_env\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install mesa matplotlib pandas numpy
   ```

## Usage

### Running the Interactive Simulation

Start the web-based visualization server:

```bash
python server.py
```

Then open your browser and navigate to:
```
http://localhost:8521
```

You can interact with the simulation:
- Scroll to see a full-width road canvas on top and all charts stacked below it
- Adjust parameters (spawn rates, traffic light durations, pedestrian timing)
- Watch real-time agent movements (cars, pedestrians, ambulances)
- View live charts of metrics with the road always visible
- Pause/play the simulation

### Running Experiments

Run batch experiments with different parameters:

```bash
python run_experiments.py
```

This script tests different spawn rates and generates visualizations of the results.

### Programmatic Usage

```python
from model import TrafficModel

# Create a simulation
model = TrafficModel(
    width=30,              # Grid width
    height=3,              # Grid height (road lanes)
    spawn_rate=0.15,       # Probability of car spawning per step
    green_duration=10,     # Traffic light green duration (steps)
    red_duration=10,       # Traffic light red duration (steps)
    pedestrian_spawn_rate=0.05,   # Probability of pedestrian spawning per step
    walk_duration=5,              # Base walk duration (auto-extended for clarity)
    emergency_spawn_rate=0.01     # Probability of ambulance spawning per step
)

# Run simulation for N steps
for i in range(100):
    model.step()

# Access metrics
print(f"Cars passed: {model.cars_passed}")
print(f"Pedestrians crossed: {model.pedestrians_crossed}")
print(f"Average travel time: {model.compute_avg_travel_time():.2f}")

# Get collected data
df = model.datacollector.get_model_vars_dataframe()
```

## Project Structure

```
traffic_sim/
├── model.py              # Core simulation model and agents
├── server.py             # Web visualization server
├── run_experiments.py    # Batch experiment runner
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Model Components

### Agents

- **`CarAgent`**: Represents vehicles moving on the road
  - Moves right one cell per step
  - Stops for red lights and pedestrians
  - Exits when reaching grid boundary

- **`PedestrianAgent`**: Represents pedestrians crossing the road
  - Moves horizontally to intersection
  - Crosses vertically when WALK signal is active
  - Waits for appropriate signal

- **`TrafficLightAgent`**: Controls traffic and pedestrian signals
  - Cycles between GREEN/RED states
  - Activates WALK signal when pedestrians present and light is RED

### Model Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `width` | 30 | Number of grid cells horizontally |
| `height` | 3 | Number of grid cells vertically (road lanes) |
| `spawn_rate` | 0.15 | Probability of car spawn per step (0-1) |
| `green_duration` | 10 | Number of steps traffic light stays green |
| `red_duration` | 10 | Number of steps traffic light stays red |
| `pedestrian_spawn_rate` | 0.05 | Probability of pedestrian spawn per step (0-1) |
| `walk_duration` | 5 | Duration pedestrians can cross (steps) |

## Simulation Behavior

### Traffic Flow
1. Cars spawn at the left edge (middle lane) based on `spawn_rate`
2. Cars move right one cell per step
3. At the intersection (center of grid):
   - Cars proceed if light is GREEN and intersection is clear
   - Cars stop if light is RED
   - Cars stop for pedestrians in crosswalk
4. Cars exit when reaching the right edge

### Pedestrian Flow
1. Pedestrians spawn at top or bottom row based on `pedestrian_spawn_rate`
2. Pedestrians move horizontally toward the intersection
3. At the intersection:
   - Pedestrians wait if signal is DONT_WALK
   - Pedestrians cross vertically when signal is WALK (light is RED)
4. After crossing, pedestrians exit to the right

### Traffic Light Logic
- Cycles between GREEN and RED based on durations
- When RED and pedestrians are present: activates WALK signal
- When GREEN or no pedestrians: DONT_WALK signal

## Metrics Explanation

- **Cars Passed**: Cumulative count of cars that successfully exited
- **Average Travel Time**: Total travel time divided by cars passed
- **Average Waiting Time**: Average of all cars' waiting step counters
- **Queue Length**: Number of cells before intersection occupied by cars
- **Pedestrians Crossed**: Total pedestrians who completed their journey
- **Average Pedestrian Time**: Total pedestrian time divided by pedestrians crossed
- **Pedestrian Wait Time**: Average waiting time for all active pedestrians

## How to Optimize a Busy Intersection - Step-by-Step Guide

### Scenario Setup
You're a traffic engineer tasked with optimizing an intersection that has:
- **High car traffic** during rush hour (spawn_rate = 0.30)
- **Many pedestrians** needing to cross (pedestrian_spawn_rate = 0.10)
- **Current traffic light timing**: 15 seconds green, 15 seconds red
- **Problem**: Long wait times for both cars and pedestrians

---

### Step 1: Establish Baseline Performance

First, measure the current performance to have a comparison point:

```python
from model import TrafficModel
import pandas as pd

def run_simulation(green_duration, red_duration, spawn_rate, pedestrian_spawn_rate, steps=500):
    """Run a single simulation and return final metrics"""
    model = TrafficModel(
        width=30,
        height=3,
        spawn_rate=spawn_rate,
        green_duration=green_duration,
        red_duration=red_duration,
        pedestrian_spawn_rate=pedestrian_spawn_rate
    )
    
    for i in range(steps):
        model.step()
    
    # Get final metrics
    df = model.datacollector.get_model_vars_dataframe()
    final_row = df.iloc[-1]
    
    return {
        'cars_passed': final_row['CarsPassed'],
        'avg_travel_time': final_row['AvgTravelTime'],
        'avg_waiting_time': final_row['AvgWaitingTime'],
        'queue_length': final_row['QueueLength'],
        'pedestrians_crossed': final_row['PedestriansCrossed'],
        'avg_pedestrian_time': final_row['AvgPedestrianTime'],
        'pedestrian_wait_time': final_row['PedestrianWaitTime'],
        'green_duration': green_duration,  # Store for report
        'red_duration': red_duration       # Store for report
    }

# Step 1: Baseline (Current Situation)
baseline = run_simulation(
    green_duration=15,
    red_duration=15,
    spawn_rate=0.30,
    pedestrian_spawn_rate=0.10
)

print("=== BASELINE RESULTS (Current Timing) ===")
print(f"Cars Passed: {baseline['cars_passed']}")
print(f"Average Car Wait Time: {baseline['avg_waiting_time']:.2f} steps")
print(f"Average Travel Time: {baseline['avg_travel_time']:.2f} steps")
print(f"Pedestrians Crossed: {baseline['pedestrians_crossed']}")
print(f"Average Pedestrian Wait: {baseline['pedestrian_wait_time']:.2f} steps")
```

**Expected Output:**
```
=== BASELINE RESULTS (Current Timing) ===
Cars Passed: 45
Average Car Wait Time: 8.50 steps
Average Travel Time: 25.30 steps
Pedestrians Crossed: 22
Average Pedestrian Wait: 12.30 steps
```

---

### Step 2: Test Different Timing Strategies

Now test multiple alternatives to find the optimal configuration:

```python
# Define different strategies to test
strategies = [
    {
        'name': 'Longer Green for Cars',
        'green_duration': 20,
        'red_duration': 10,
        'description': 'Prioritizes car throughput'
    },
    {
        'name': 'Shorter Cycles',
        'green_duration': 10,
        'red_duration': 10,
        'description': 'More frequent signal changes'
    },
    {
        'name': 'Balanced (Longer Red)',
        'green_duration': 12,
        'red_duration': 18,
        'description': 'More time for pedestrians'
    },
    {
        'name': 'Equal Priority',
        'green_duration': 15,
        'red_duration': 15,
        'description': 'Current baseline'
    }
]

# Test each strategy
results = []
for strategy in strategies:
    print(f"\nTesting: {strategy['name']}...")
    metrics = run_simulation(
        green_duration=strategy['green_duration'],
        red_duration=strategy['red_duration'],
        spawn_rate=0.30,
        pedestrian_spawn_rate=0.10
    )
    
    metrics['strategy'] = strategy['name']
    metrics['green_duration'] = strategy['green_duration']
    metrics['red_duration'] = strategy['red_duration']
    results.append(metrics)

# Convert to DataFrame for easy analysis
results_df = pd.DataFrame(results)
```

---

### Step 3: Compare and Analyze Results

```python
import matplotlib.pyplot as plt

# Display comparison table
print("\n=== COMPARISON OF STRATEGIES ===")
print(results_df[['strategy', 'cars_passed', 'avg_waiting_time', 
                  'pedestrians_crossed', 'pedestrian_wait_time']].to_string(index=False))

# Calculate improvement percentages
for idx, row in results_df.iterrows():
    car_improvement = ((row['cars_passed'] - baseline['cars_passed']) / baseline['cars_passed']) * 100
    wait_improvement = ((baseline['avg_waiting_time'] - row['avg_waiting_time']) / baseline['avg_waiting_time']) * 100
    print(f"\n{row['strategy']}:")
    print(f"  Cars Passed: {car_improvement:+.1f}% change")
    print(f"  Car Wait Time: {wait_improvement:+.1f}% improvement")

# Visualize results
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Chart 1: Cars Passed
axes[0, 0].bar(results_df['strategy'], results_df['cars_passed'])
axes[0, 0].axhline(y=baseline['cars_passed'], color='r', linestyle='--', label='Baseline')
axes[0, 0].set_title('Cars Passed')
axes[0, 0].set_ylabel('Count')
axes[0, 0].tick_params(axis='x', rotation=45)
axes[0, 0].legend()

# Chart 2: Average Wait Time
axes[0, 1].bar(results_df['strategy'], results_df['avg_waiting_time'])
axes[0, 1].axhline(y=baseline['avg_waiting_time'], color='r', linestyle='--', label='Baseline')
axes[0, 1].set_title('Average Car Wait Time')
axes[0, 1].set_ylabel('Steps')
axes[0, 1].tick_params(axis='x', rotation=45)
axes[0, 1].legend()

# Chart 3: Pedestrians Crossed
axes[1, 0].bar(results_df['strategy'], results_df['pedestrians_crossed'])
axes[1, 0].axhline(y=baseline['pedestrians_crossed'], color='r', linestyle='--', label='Baseline')
axes[1, 0].set_title('Pedestrians Crossed')
axes[1, 0].set_ylabel('Count')
axes[1, 0].tick_params(axis='x', rotation=45)
axes[1, 0].legend()

# Chart 4: Pedestrian Wait Time
axes[1, 1].bar(results_df['strategy'], results_df['pedestrian_wait_time'])
axes[1, 1].axhline(y=baseline['pedestrian_wait_time'], color='r', linestyle='--', label='Baseline')
axes[1, 1].set_title('Average Pedestrian Wait Time')
axes[1, 1].set_ylabel('Steps')
axes[1, 1].tick_params(axis='x', rotation=45)
axes[1, 1].legend()

plt.tight_layout()
plt.savefig('intersection_optimization_results.png')
plt.show()
```

---

### Step 4: Find Optimal Solution

Create a scoring function to find the best overall solution:

```python
def calculate_score(metrics, weights=None):
    """
    Calculate a composite score for a strategy.
    Higher score = better performance
    """
    if weights is None:
        # Default weights - adjust based on priorities
        weights = {
            'cars_passed': 0.3,        # Throughput important
            'avg_waiting_time': -0.2,  # Lower is better (negative weight)
            'pedestrians_crossed': 0.25,
            'pedestrian_wait_time': -0.15,
            'avg_travel_time': -0.1
        }
    
    # Normalize metrics (using baseline as reference)
    normalized_metrics = {
        'cars_passed': metrics['cars_passed'] / baseline['cars_passed'],
        'avg_waiting_time': metrics['avg_waiting_time'] / baseline['avg_waiting_time'],
        'pedestrians_crossed': metrics['pedestrians_crossed'] / baseline['pedestrians_crossed'],
        'pedestrian_wait_time': metrics['pedestrian_wait_time'] / baseline['pedestrian_wait_time'],
        'avg_travel_time': metrics['avg_travel_time'] / baseline['avg_travel_time']
    }
    
    # Calculate weighted score
    score = sum(
        normalized_metrics[key] * weights[key]
        for key in weights.keys()
    )
    
    return score

# Calculate scores for each strategy
results_df['score'] = results_df.apply(
    lambda row: calculate_score(row.to_dict()), 
    axis=1
)

# Find best strategy
best_strategy = results_df.loc[results_df['score'].idxmax()]

print("\n=== OPTIMAL SOLUTION ===")
print(f"Best Strategy: {best_strategy['strategy']}")
print(f"Green Duration: {best_strategy['green_duration']} steps")
print(f"Red Duration: {best_strategy['red_duration']} steps")
print(f"Overall Score: {best_strategy['score']:.3f}")
print(f"\nExpected Improvements:")
print(f"  Cars Passed: {best_strategy['cars_passed']} ({((best_strategy['cars_passed']/baseline['cars_passed']-1)*100):+.1f}%)")
print(f"  Car Wait Time: {best_strategy['avg_waiting_time']:.2f} steps ({((1-best_strategy['avg_waiting_time']/baseline['avg_waiting_time'])*100):+.1f}% reduction)")
print(f"  Pedestrians Crossed: {best_strategy['pedestrians_crossed']} ({((best_strategy['pedestrians_crossed']/baseline['pedestrians_crossed']-1)*100):+.1f}%)")
print(f"  Pedestrian Wait: {best_strategy['pedestrian_wait_time']:.2f} steps ({((1-best_strategy['pedestrian_wait_time']/baseline['pedestrian_wait_time'])*100):+.1f}% reduction)")
```

---

### Step 5: Run Multiple Trials for Reliability

For robust results, run multiple trials and average the results:

```python
def run_multiple_trials(strategy_config, trials=10):
    """Run multiple trials and return average metrics"""
    all_metrics = []
    
    for trial in range(trials):
        metrics = run_simulation(
            green_duration=strategy_config['green_duration'],
            red_duration=strategy_config['red_duration'],
            spawn_rate=0.30,
            pedestrian_spawn_rate=0.10
        )
        all_metrics.append(metrics)
    
    # Average all metrics
    avg_metrics = {}
    for key in all_metrics[0].keys():
        avg_metrics[key] = sum(m[key] for m in all_metrics) / len(all_metrics)
    
    return avg_metrics

# Test best strategy with multiple trials
print("\nRunning multiple trials for reliability...")
best_config = {
    'green_duration': int(best_strategy['green_duration']),
    'red_duration': int(best_strategy['red_duration'])
}

robust_metrics = run_multiple_trials(best_config, trials=20)
print(f"\nRobust Results (20 trials):")
print(f"Average Cars Passed: {robust_metrics['cars_passed']:.1f}")
print(f"Average Wait Time: {robust_metrics['avg_waiting_time']:.2f} steps")
```

---

### Step 6: Generate Report and Recommendations

```python
def generate_report(baseline, best_strategy, robust_metrics):
    """Generate a summary report"""
    report = f"""
=====================================================================
    INTERSECTION OPTIMIZATION REPORT
=====================================================================

CURRENT SITUATION (Baseline):
- Traffic Light Timing: {baseline['green_duration']}s GREEN / {baseline['red_duration']}s RED
- Cars Passed: {baseline['cars_passed']}
- Average Car Wait: {baseline['avg_waiting_time']:.2f} steps
- Pedestrians Crossed: {baseline['pedestrians_crossed']}
- Pedestrian Wait: {baseline['pedestrian_wait_time']:.2f} steps

RECOMMENDED SOLUTION:
- Traffic Light Timing: {best_strategy['green_duration']}s GREEN / {best_strategy['red_duration']}s RED
- Expected Cars Passed: {robust_metrics['cars_passed']:.1f} ({((robust_metrics['cars_passed']/baseline['cars_passed']-1)*100):+.1f}% change)
- Expected Car Wait: {robust_metrics['avg_waiting_time']:.2f} steps ({((1-robust_metrics['avg_waiting_time']/baseline['avg_waiting_time'])*100):+.1f}% improvement)
- Expected Pedestrians Crossed: {robust_metrics['pedestrians_crossed']:.1f} ({((robust_metrics['pedestrians_crossed']/baseline['pedestrians_crossed']-1)*100):+.1f}% change)
- Expected Pedestrian Wait: {robust_metrics['pedestrian_wait_time']:.2f} steps ({((1-robust_metrics['pedestrian_wait_time']/baseline['pedestrian_wait_time'])*100):+.1f}% improvement)

NEXT STEPS:
1. Implement recommended timing changes
2. Monitor real-world performance for 1-2 weeks
3. Compare actual results with simulation predictions
4. Fine-tune if needed

=====================================================================
"""
    return report

print(generate_report(baseline, best_strategy, robust_metrics))

# Save to file
with open('optimization_report.txt', 'w') as f:
    f.write(generate_report(baseline, best_strategy, robust_metrics))
```

---

### Quick Start: Using the Interactive Server

For visual experimentation, use the web interface:

1. **Start the server:**
   ```bash
   python server.py
   ```

2. **Open browser to:** `http://localhost:8521`

3. **Adjust parameters in real-time:**
   - Change `green_duration` and `red_duration` sliders
   - Adjust `spawn_rate` for traffic volume
   - Modify `pedestrian_spawn_rate` for pedestrian traffic
   - Watch live metrics update

4. **Compare scenarios** by:
   - Taking notes of metrics for different configurations
   - Running scenarios multiple times
   - Observing visual patterns in traffic flow

---

### Complete Example Script

Save this as `optimize_intersection.py`:

```python
from model import TrafficModel
import pandas as pd
import matplotlib.pyplot as plt

def run_simulation(green_duration, red_duration, spawn_rate, pedestrian_spawn_rate, steps=500):
    model = TrafficModel(
        width=30, height=3,
        spawn_rate=spawn_rate,
        green_duration=green_duration,
        red_duration=red_duration,
        pedestrian_spawn_rate=pedestrian_spawn_rate
    )
    for i in range(steps):
        model.step()
    df = model.datacollector.get_model_vars_dataframe()
    return df.iloc[-1].to_dict()

# Baseline
baseline = run_simulation(15, 15, 0.30, 0.10)

# Test strategies
strategies = [
    {'name': 'Longer Green', 'green': 20, 'red': 10},
    {'name': 'Shorter Cycles', 'green': 10, 'red': 10},
    {'name': 'More Pedestrian Time', 'green': 12, 'red': 18},
]

results = []
for s in strategies:
    metrics = run_simulation(s['green'], s['red'], 0.30, 0.10)
    metrics['strategy'] = s['name']
    results.append(metrics)

# Find best
results_df = pd.DataFrame(results)
best = results_df.loc[results_df['CarsPassed'].idxmax()]

print(f"Best Strategy: {best['strategy']}")
print(f"Configuration: {best['green_duration']}s green / {best['red_duration']}s red")
```

Run with:
```bash
python optimize_intersection.py
```

---

**Outcome**: Data-driven optimization that provides concrete recommendations backed by quantitative analysis!

## Customization

You can modify the simulation by adjusting parameters in `server.py`:

```python
server = ModularServer(
    TrafficModel,
    [grid, chart1, chart2, chart3, chart4, chart5, chart6],
    "Traffic Flow Simulation with Pedestrians",
    {
        "width": 30,
        "height": 3,
        "spawn_rate": 0.15,          # Increase for more traffic
        "green_duration": 10,
        "red_duration": 10,
        "pedestrian_spawn_rate": 0.05,  # Increase for more pedestrians
        "walk_duration": 5
    }
)
```

## Technologies

- **Mesa**: Agent-based modeling framework
- **Python**: Programming language
- **Matplotlib**: Data visualization (for experiments)
- **Pandas**: Data analysis (for experiments)

## License

This project is open source and available for educational and research purposes.

## Contributing

Feel free to fork this project and submit pull requests for improvements!

## Testing

The project includes a comprehensive test suite to verify correct operation under busy intersection conditions:

```bash
python test_busy_intersection.py
```

This test suite verifies:
- ✓ System handles very high car traffic correctly
- ✓ System handles very high pedestrian traffic correctly
- ✓ System remains stable under maximum load
- ✓ Queue lengths remain bounded (no infinite growth)
- ✓ No deadlocks occur (agents continue to progress)
- ✓ Extended simulations run without errors
- ✓ Pedestrians can cross even under heavy car traffic

**Note**: Under extremely high traffic conditions, wait times will naturally increase and throughput may decrease. This is realistic behavior - the simulation accurately reflects real-world congestion scenarios.

## Future Enhancements

Potential features for future development:
- Multiple lanes for cars
- Different pedestrian crossing patterns
- Emergency vehicle priority
- Real-time traffic optimization
- Statistics export functionality
- 3D visualization

## Contact

For questions or suggestions, please open an issue on GitHub.

---

**Enjoy simulating traffic! 🚗🚶🚦**

