from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from model import TrafficModel, CarAgent, TrafficLightAgent, PedestrianAgent, EmergencyVehicleAgent

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
    elif isinstance(agent, EmergencyVehicleAgent):
        return {
            "Shape": "rect",
            "w": 0.9,
            "h": 0.9,
            "Color": "magenta",
            "Layer": 3,
            "Filled": True,
            "text": "EM",
            "text_color": "white"
        }
    elif isinstance(agent, TrafficLightAgent):
        color = "green" if agent.state == "GREEN" else "red"
        text = ""
        text_color = "white"
        text_size = "18px"

        if agent.emergency_override:
            text = "EMERGENCY"
            text_color = "#000000"
            text_size = "20px"
        elif agent.pedestrian_signal == "WALK":
            text = "WALK"
            text_color = "#000000"
            text_size = "20px"
        else:
            text = "DON'T WALK"
            text_color = "#000000"
            text_size = "18px"

        return {
            "Shape": "circle",
            "r": 0.6,
            "Color": color,
            "Layer": 2,
            "Filled": True,
            "text": text,
            "text_color": text_color,
            "text_size": text_size,
            "stroke_color": "#ffffff",
            "stroke_width": 2
        }
    
    return {}  # Default for unknown agents

# ---------------------------
# Grid + Charts
# ---------------------------
grid_width = 30
grid_height = 3
canvas_width = 900
canvas_height = 300

grid = CanvasGrid(agent_portrayal, grid_width, grid_height, canvas_width, canvas_height)

# All charts use the same data collector
chart_size = {"canvas_width": 900, "canvas_height": 180}

chart1 = ChartModule(
    [{"Label": "CarsPassed", "Color": "Black"}],
    data_collector_name="datacollector",
    **chart_size
)
chart2 = ChartModule(
    [{"Label": "AvgWaitingTime", "Color": "Red"}], 
    data_collector_name="datacollector",
    **chart_size
)
chart3 = ChartModule(
    [{"Label": "QueueLength", "Color": "Blue"}], 
    data_collector_name="datacollector",
    **chart_size
)
chart4 = ChartModule(
    [{"Label": "PedestriansCrossed", "Color": "Green"}],
    data_collector_name="datacollector",
    **chart_size
)
chart5 = ChartModule(
    [{"Label": "AvgPedestrianTime", "Color": "Purple"}],
    data_collector_name="datacollector",
    **chart_size
)
chart6 = ChartModule(
    [{"Label": "PedestrianWaitTime", "Color": "Yellow"}],
    data_collector_name="datacollector",
    **chart_size
)
chart7 = ChartModule(
    [{"Label": "EmergencyActive", "Color": "Magenta"}],
    data_collector_name="datacollector",
    **chart_size
)
chart8 = ChartModule(
    [{"Label": "EmergenciesCleared", "Color": "Gray"}],
    data_collector_name="datacollector",
    **chart_size
)

# ---------------------------
# Server Configuration
# ---------------------------
server = ModularServer(
    TrafficModel,
    [grid, chart1, chart2, chart3, chart4, chart5, chart6, chart7, chart8],
    "Traffic Flow Simulation with Pedestrians",
    {
        "width": grid_width,
        "height": grid_height,
        "spawn_rate": 0.15,
        "green_duration": 10,
        "red_duration": 10,
        "pedestrian_spawn_rate": 0.05,
        "walk_duration": 5,
        "emergency_spawn_rate": 0.01
    }
)

server.port = 8521

if __name__ == "__main__":
    print(f"Starting Traffic Flow Simulation server on http://localhost:{server.port}")
    server.launch()