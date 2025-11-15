from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from model import TrafficModel, CarAgent, TrafficLightAgent, PedestrianAgent

# ---------------------------
# Agent portrayal
# ---------------------------
def agent_portrayal(agent):
    if isinstance(agent, CarAgent):
        # Use different colors based on waiting time
        if agent.waiting_steps == 0:
            color = "blue"  # Moving
        elif agent.waiting_steps < 5:
            color = "orange"  # Short wait
        else:
            color = "red"  # Long wait
            
        return {
            "Shape": "rect", 
            "w": 0.8, 
            "h": 0.8, 
            "Color": color, 
            "Layer": 1,
            "Filled": True
        }
    elif isinstance(agent, PedestrianAgent):
        # Use different colors based on crossing state
        if agent.crossing:
            color = "lime"  # Actively crossing
        elif agent.waiting_steps > 0:
            color = "yellow"  # Waiting
        else:
            color = "cyan"  # Walking to intersection
            
        return {
            "Shape": "circle",
            "r": 0.5,
            "Color": color,
            "Layer": 1,
            "Filled": True
        }
    elif isinstance(agent, TrafficLightAgent):
        # Traffic light shows car signal (red/green circle)
        color = "green" if agent.state == "GREEN" else "red"
        portrayal = {
            "Shape": "circle", 
            "r": 0.5, 
            "Color": color, 
            "Layer": 2,
            "Filled": True
        }
        
        # Add text indicator for pedestrian signal
        if agent.pedestrian_signal == "WALK":
            portrayal["text"] = "WALK"
            portrayal["text_color"] = "white"
        else:
            portrayal["text"] = ""
        
        return portrayal
    
    return {}  # Default for unknown agents

# ---------------------------
# Grid + Charts
# ---------------------------
grid_width = 30
grid_height = 3

grid = CanvasGrid(agent_portrayal, grid_width, grid_height, 600, 200)

# All charts use the same data collector
chart1 = ChartModule(
    [{"Label": "CarsPassed", "Color": "Black"}],
    data_collector_name="datacollector"
)
chart2 = ChartModule(
    [{"Label": "AvgWaitingTime", "Color": "Red"}], 
    data_collector_name="datacollector"
)
chart3 = ChartModule(
    [{"Label": "QueueLength", "Color": "Blue"}], 
    data_collector_name="datacollector"
)
chart4 = ChartModule(
    [{"Label": "PedestriansCrossed", "Color": "Green"}],
    data_collector_name="datacollector"
)
chart5 = ChartModule(
    [{"Label": "AvgPedestrianTime", "Color": "Purple"}],
    data_collector_name="datacollector"
)
chart6 = ChartModule(
    [{"Label": "PedestrianWaitTime", "Color": "Yellow"}],
    data_collector_name="datacollector"
)

# ---------------------------
# Server Configuration
# ---------------------------
server = ModularServer(
    TrafficModel,
    [grid, chart1, chart2, chart3, chart4, chart5, chart6],
    "Traffic Flow Simulation with Pedestrians",
    {
        "width": grid_width,
        "height": grid_height,
        "spawn_rate": 0.15,
        "green_duration": 10,
        "red_duration": 10,
        "pedestrian_spawn_rate": 0.05,
        "walk_duration": 5
    }
)

server.port = 8521

if __name__ == "__main__":
    print(f"Starting Traffic Flow Simulation server on http://localhost:{server.port}")
    server.launch()