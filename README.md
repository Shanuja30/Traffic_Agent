# Traffic Simulation with Pedestrian Crossing

An agent-based traffic simulation built with [Mesa](https://mesa.readthedocs.io/) that models cars and pedestrians interacting at a traffic intersection with a traffic light system.

## Features

### 🚗 **Cars**
- Cars spawn on the left side of the road and move right
- Cars stop at red traffic lights
- Cars avoid collisions with other vehicles
- Cars yield to pedestrians crossing the road
- Real-time color coding based on waiting time:
  - **Blue**: Moving freely
  - **Orange**: Short wait
  - **Red**: Long wait

### 🚶 **Pedestrians**
- Pedestrians spawn at the top or bottom of the road
- Pedestrians move horizontally to reach the intersection
- Pedestrians wait for WALK signal to cross vertically
- Pedestrian signals activate when traffic light is RED
- Real-time visualization:
  - **Cyan**: Walking to intersection
  - **Yellow**: Waiting at intersection
  - **Lime**: Actively crossing

### 🚦 **Traffic Light System**
- Automatic traffic light that cycles between GREEN and RED
- Configurable green and red durations
- Pedestrian WALK/DONT_WALK signals synchronized with traffic lights
- Pedestrians can cross when light is RED (cars stopped)

### 📊 **Real-time Metrics**
- **Cars Passed**: Total number of cars that exited the grid
- **Average Travel Time**: Mean time for cars to traverse the road
- **Average Waiting Time**: Mean time cars spend waiting
- **Queue Length**: Number of cars waiting before intersection
- **Pedestrians Crossed**: Total pedestrians who completed crossing
- **Average Pedestrian Time**: Mean time for pedestrians to complete journey
- **Pedestrian Wait Time**: Average time pedestrians wait at intersection

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
- Adjust parameters (spawn rates, traffic light durations)
- Watch real-time agent movements
- View live charts of metrics
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
    pedestrian_spawn_rate=0.05,  # Probability of pedestrian spawning per step
    walk_duration=5        # Pedestrian walk signal duration (steps)
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

