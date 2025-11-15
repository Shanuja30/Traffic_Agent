from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.agent import Agent
import random

# ---------------------------
# Traffic Light Agent
# ---------------------------
class TrafficLightAgent(Agent):
    def __init__(self, unique_id, model, green_duration=10, red_duration=10, walk_duration=5):
        super().__init__(unique_id, model)
        self.state = "GREEN"
        self.pedestrian_signal = "DONT_WALK"  # DONT_WALK or WALK
        self.timer = 0
        self.green_duration = green_duration
        self.red_duration = red_duration
        self.walk_duration = walk_duration
        self.walk_timer = 0
        self.pedestrian_active = False  # True when pedestrians are in crosswalk

    def step(self):
        self.timer += 1
        
        # Check if pedestrians are waiting or crossing
        # Pedestrians can cross when light is RED (when cars are stopped)
        x_light, y_light = self.model.intersection_pos
        crosswalk_cells = [
            (x_light, y_light - 1),  # Top of intersection
            (x_light, y_light),      # Center (intersection)
            (x_light, y_light + 1)   # Bottom of intersection
        ]
        
        pedestrians_nearby = False
        for cell_pos in crosswalk_cells:
            if 0 <= cell_pos[1] < self.model.grid.height:
                cell_agents = self.model.grid.get_cell_list_contents(cell_pos)
                if any(isinstance(agent, PedestrianAgent) for agent in cell_agents):
                    pedestrians_nearby = True
                    break
        
        self.pedestrian_active = pedestrians_nearby
        
        # Pedestrian signal logic
        if self.state == "RED" and pedestrians_nearby:
            # When cars are stopped (RED), pedestrians can cross
            self.pedestrian_signal = "WALK"
            self.walk_timer += 1
            if self.walk_timer >= self.walk_duration:
                # After walk duration, signal DONT_WALK even if still RED
                # (prevents indefinite crossing)
                pass
        else:
            self.pedestrian_signal = "DONT_WALK"
            self.walk_timer = 0
        
        # Traffic light state transitions
        if self.state == "GREEN" and self.timer >= self.green_duration:
            self.state = "RED"
            self.timer = 0
        elif self.state == "RED" and self.timer >= self.red_duration:
            self.state = "GREEN"
            self.timer = 0

    def advance(self):
        pass  # Traffic light doesn't move

# ---------------------------
# Pedestrian Agent
# ---------------------------
class PedestrianAgent(Agent):
    def __init__(self, unique_id, model, spawn_time, direction="crossing"):
        super().__init__(unique_id, model)
        self.spawn_time = spawn_time
        self.direction = direction  # "crossing" means crossing the road
        self.waiting_steps = 0
        self.next_pos = None
        self.remove_flag = False
        self.crossing = False  # True when actively crossing
        self.target_row = None  # Which row to cross to

    def step(self):
        x, y = self.pos
        x_light, y_light = self.model.intersection_pos
        
        # Determine target row for crossing
        if self.target_row is None:
            # Start from top or bottom, cross to the other side
            if y == 0:
                self.target_row = self.model.grid.height - 1
            else:
                self.target_row = 0
        
        # Check if pedestrian is at intersection
        if x == x_light:
            # At the intersection - can cross vertically
            if self.model.traffic_light.pedestrian_signal == "WALK":
                # Check if we've reached target row
                if y == self.target_row:
                    # Finished crossing, exit by moving right
                    next_pos = (x + 1, y)
                    if next_pos[0] >= self.model.grid.width:
                        self.model.pedestrians_crossed += 1
                        self.model.total_pedestrian_time += (self.model.schedule.time - self.spawn_time)
                        self.remove_flag = True
                        return
                    
                    # Check if exit path is clear
                    cell_agents = self.model.grid.get_cell_list_contents(next_pos)
                    car_blocking = any(isinstance(agent, CarAgent) for agent in cell_agents)
                    if not car_blocking:
                        self.next_pos = next_pos
                        self.crossing = False
                    else:
                        self.waiting_steps += 1
                        self.next_pos = self.pos
                    return
                else:
                    # Still crossing - move toward target row
                    next_y = y + 1 if y < self.target_row else y - 1
                    next_pos = (x, next_y)
                    
                    # Check for other pedestrians
                    cell_agents = self.model.grid.get_cell_list_contents(next_pos)
                    pedestrian_blocking = any(isinstance(agent, PedestrianAgent) and agent != self for agent in cell_agents)
                    
                    if not pedestrian_blocking:
                        self.next_pos = next_pos
                        self.crossing = True
                        self.waiting_steps = 0
                    else:
                        self.waiting_steps += 1
                        self.next_pos = self.pos
                    return
            else:
                # DONT_WALK signal - wait at intersection
                self.waiting_steps += 1
                self.next_pos = self.pos
                self.crossing = False
                return
        
        # Not at intersection yet - move toward it
        if x < x_light:
            next_pos = (x + 1, y)
            # Check if path is clear (no cars blocking)
            cell_agents = self.model.grid.get_cell_list_contents(next_pos)
            car_blocking = any(isinstance(agent, CarAgent) for agent in cell_agents)
            pedestrian_blocking = any(isinstance(agent, PedestrianAgent) and agent != self for agent in cell_agents)
            
            if not car_blocking and not pedestrian_blocking:
                self.next_pos = next_pos
                self.waiting_steps = 0
            else:
                self.waiting_steps += 1
                self.next_pos = self.pos
        else:
            # Past intersection, moving to exit
            next_pos = (x + 1, y)
            if next_pos[0] >= self.model.grid.width:
                self.model.pedestrians_crossed += 1
                self.model.total_pedestrian_time += (self.model.schedule.time - self.spawn_time)
                self.remove_flag = True
                return
            
            cell_agents = self.model.grid.get_cell_list_contents(next_pos)
            car_blocking = any(isinstance(agent, CarAgent) for agent in cell_agents)
            if not car_blocking:
                self.next_pos = next_pos
            else:
                self.waiting_steps += 1
                self.next_pos = self.pos

    def advance(self):
        if self.remove_flag:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
        else:
            if self.next_pos is not None:
                self.model.grid.move_agent(self, self.next_pos)
                self.pos = self.next_pos

# ---------------------------
# Car Agent
# ---------------------------
class CarAgent(Agent):
    def __init__(self, unique_id, model, spawn_time):
        super().__init__(unique_id, model)
        self.spawn_time = spawn_time
        self.waiting_steps = 0
        self.next_pos = None
        self.remove_flag = False

    def step(self):
        x, y = self.pos
        next_pos = (x + 1, y)

        # Check if car exits grid
        if next_pos[0] >= self.model.grid.width:
            self.model.cars_passed += 1
            self.model.total_travel_time += (self.model.schedule.time - self.spawn_time)
            self.remove_flag = True
            return

        # Check intersection
        if next_pos == self.model.intersection_pos:
            if self.model.traffic_light.state == "GREEN":
                # Check for other cars and pedestrians
                cell_agents = self.model.grid.get_cell_list_contents(next_pos)
                car_blocking = any(isinstance(agent, CarAgent) and agent != self for agent in cell_agents)
                pedestrian_blocking = any(isinstance(agent, PedestrianAgent) for agent in cell_agents)
                
                if not car_blocking and not pedestrian_blocking:
                    self.next_pos = next_pos
                    self.waiting_steps = 0  # RESET waiting when moving through intersection
                else:
                    self.waiting_steps += 1
                    self.next_pos = self.pos
            else:  # Red light
                self.waiting_steps += 1
                self.next_pos = self.pos
            return

        # Check for pedestrians in crosswalk (one cell before intersection)
        x_light, y_light = self.model.intersection_pos
        if next_pos[0] == x_light - 1 and next_pos[1] == y_light:
            # One cell before intersection - check for pedestrians crossing
            crosswalk_cells = [
                (x_light, y_light - 1),  # Top of intersection
                (x_light, y_light),      # Center (intersection)
                (x_light, y_light + 1)   # Bottom of intersection
            ]
            
            pedestrians_crossing = False
            for cell_pos in crosswalk_cells:
                if 0 <= cell_pos[1] < self.model.grid.height:
                    cell_agents = self.model.grid.get_cell_list_contents(cell_pos)
                    if any(isinstance(agent, PedestrianAgent) and agent.crossing for agent in cell_agents):
                        pedestrians_crossing = True
                        break
            
            if pedestrians_crossing:
                # Stop for pedestrians crossing
                self.waiting_steps += 1
                self.next_pos = self.pos
                return

        # Normal movement
        cell_agents = self.model.grid.get_cell_list_contents(next_pos)
        car_blocking = any(isinstance(agent, CarAgent) and agent != self for agent in cell_agents)
        pedestrian_blocking = any(isinstance(agent, PedestrianAgent) for agent in cell_agents)
        
        if not car_blocking and not pedestrian_blocking:
            self.next_pos = next_pos
            self.waiting_steps = 0  # RESET waiting when moving normally
        else:
            self.waiting_steps += 1
            self.next_pos = self.pos

    def advance(self):
        if self.remove_flag:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
        else:
            self.model.grid.move_agent(self, self.next_pos)
            self.pos = self.next_pos

# ---------------------------
# Traffic Model
# ---------------------------
class TrafficModel(Model):
    def __init__(self, width=30, height=3, spawn_rate=0.15, green_duration=10, red_duration=10, 
                 pedestrian_spawn_rate=0.05, walk_duration=5):
        super().__init__()
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = SimultaneousActivation(self)
        self.spawn_rate = spawn_rate
        self.pedestrian_spawn_rate = pedestrian_spawn_rate

        self.intersection_pos = (width // 2, height // 2)
        self.cars_passed = 0
        self.total_travel_time = 0
        self.pedestrians_crossed = 0
        self.total_pedestrian_time = 0

        # Traffic light
        self.traffic_light = TrafficLightAgent(
            "light", self,
            green_duration=green_duration,
            red_duration=red_duration,
            walk_duration=walk_duration
        )
        # Place agent at intersection
        self.grid.place_agent(self.traffic_light, self.intersection_pos)
        self.schedule.add(self.traffic_light)

        # DataCollector
        self.datacollector = DataCollector(
            model_reporters={
                "CarsPassed": lambda m: m.cars_passed,
                "AvgTravelTime": self.compute_avg_travel_time,
                "AvgWaitingTime": self.compute_avg_waiting_time,
                "QueueLength": self.get_queue_length,
                "PedestriansCrossed": lambda m: m.pedestrians_crossed,
                "AvgPedestrianTime": self.compute_avg_pedestrian_time,
                "PedestrianWaitTime": self.compute_avg_pedestrian_waiting_time
            }
        )

    def compute_avg_travel_time(self):
        if self.cars_passed == 0:
            return 0
        return self.total_travel_time / self.cars_passed

    def compute_avg_waiting_time(self):
        car_agents = [a for a in self.schedule.agents if isinstance(a, CarAgent)]
        if not car_agents:
            return 0
        waiting = sum(a.waiting_steps for a in car_agents)
        return waiting / len(car_agents)

    def get_queue_length(self):
        x_light, y_light = self.intersection_pos
        count = 0
        # Check cells before the intersection
        for dx in range(1, 6):  # Check 5 positions before the light
            pos = (x_light - dx, y_light)
            if pos[0] >= 0:  # Ensure within grid bounds
                cell_agents = self.grid.get_cell_list_contents(pos)
                if any(isinstance(a, CarAgent) for a in cell_agents):
                    count += 1
        return count

    def compute_avg_pedestrian_time(self):
        if self.pedestrians_crossed == 0:
            return 0
        return self.total_pedestrian_time / self.pedestrians_crossed

    def compute_avg_pedestrian_waiting_time(self):
        pedestrian_agents = [a for a in self.schedule.agents if isinstance(a, PedestrianAgent)]
        if not pedestrian_agents:
            return 0
        waiting = sum(a.waiting_steps for a in pedestrian_agents)
        return waiting / len(pedestrian_agents)

    def step(self):
        # Step first, then collect data
        self.schedule.step()
        
        # Spawn new car after stepping existing agents
        start_pos = (0, self.grid.height // 2)
        
        # Enhanced empty cell check
        cell_contents = self.grid.get_cell_list_contents(start_pos)
        car_in_cell = any(isinstance(agent, CarAgent) for agent in cell_contents)
        
        if random.random() < self.spawn_rate and not car_in_cell:
            car = CarAgent(self.next_id(), self, spawn_time=self.schedule.time)
            self.grid.place_agent(car, start_pos)
            car.next_pos = start_pos  # Initialize next_pos
            self.schedule.add(car)
        
        # Spawn pedestrians from top or bottom row
        if random.random() < self.pedestrian_spawn_rate:
            # Randomly choose top or bottom row
            spawn_row = random.choice([0, self.grid.height - 1])
            ped_start_pos = (0, spawn_row)
            
            # Check if spawn position is clear
            cell_contents = self.grid.get_cell_list_contents(ped_start_pos)
            ped_in_cell = any(isinstance(agent, PedestrianAgent) for agent in cell_contents)
            car_in_cell = any(isinstance(agent, CarAgent) for agent in cell_contents)
            
            if not ped_in_cell and not car_in_cell:
                pedestrian = PedestrianAgent(
                    self.next_id(), 
                    self, 
                    spawn_time=self.schedule.time,
                    direction="crossing"
                )
                self.grid.place_agent(pedestrian, ped_start_pos)
                pedestrian.next_pos = ped_start_pos  # Initialize next_pos
                pedestrian.target_row = self.grid.height - 1 if spawn_row == 0 else 0
                self.schedule.add(pedestrian)
        
        # Collect data after all updates
        self.datacollector.collect(self)