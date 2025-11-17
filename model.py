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
        self.pedestrian_signal = "DONT_WALK"
        self.timer = 0
        self.green_duration = green_duration
        self.red_duration = red_duration
        self.walk_duration = walk_duration
        self.walk_timer = 0
        self.emergency_override = False

    def step(self):
        # Emergency override: stop cars and pedestrians
        if self.emergency_override or self.model.emergency_active:
            self.state = "RED"
            self.pedestrian_signal = "DONT_WALK"
            self.walk_timer = 0
            self.timer = 0
            return

        x_light, y_light = self.model.intersection_pos
        crosswalk_cells = [(x_light, y_light-1), (x_light, y_light), (x_light, y_light+1)]
        pedestrians_nearby = any(
            any(isinstance(agent, PedestrianAgent) for agent in self.model.grid.get_cell_list_contents(pos))
            for pos in crosswalk_cells if 0 <= pos[1] < self.model.grid.height
        )

        # Trigger pedestrian phase only once when they arrive
        if pedestrians_nearby and self.pedestrian_signal == "DONT_WALK" and self.walk_timer == 0:
            self.pedestrian_signal = "WALK"
            self.walk_timer = self.walk_duration * 2

        if self.pedestrian_signal == "WALK":
            self.state = "RED"
            self.walk_timer -= 1
            if self.walk_timer <= 0:
                self.walk_timer = 0
                self.pedestrian_signal = "DONT_WALK"
        else:
            self.state = "GREEN"
            self.walk_timer = 0

    def advance(self):
        pass

    def activate_emergency_mode(self):
        self.emergency_override = True
        self.state = "RED"
        self.pedestrian_signal = "DONT_WALK"
        self.timer = 0
        self.walk_timer = 0

    def deactivate_emergency_mode(self):
        if self.emergency_override:
            self.emergency_override = False
            self.timer = 0
            self.walk_timer = 0

# ---------------------------
# Pedestrian Agent
# ---------------------------
class PedestrianAgent(Agent):
    def __init__(self, unique_id, model, spawn_time, direction="crossing"):
        super().__init__(unique_id, model)
        self.spawn_time = spawn_time
        self.direction = direction
        self.waiting_steps = 0
        self.next_pos = None
        self.remove_flag = False
        self.crossing = False
        self.target_row = None

    def step(self):
        # Emergency freeze only for pedestrians currently at the traffic light column
        if self.model.emergency_active and self.pos[0] == self.model.intersection_pos[0]:
            self.waiting_steps += 1
            self.next_pos = self.pos
            self.crossing = False
            return

        x, y = self.pos
        x_light, y_light = self.model.intersection_pos
        if self.target_row is None:
            self.target_row = self.model.grid.height - 1 if y == 0 else 0

        if x == x_light:
            # Crossing intersection
            if self.model.traffic_light.pedestrian_signal == "WALK":
                if y != self.target_row:
                    next_y = y + 1 if y < self.target_row else y - 1
                    next_pos = (x, next_y)
                    if not any(isinstance(a, PedestrianAgent) and a != self for a in self.model.grid.get_cell_list_contents(next_pos)):
                        self.next_pos = next_pos
                        self.crossing = True
                        self.waiting_steps = 0
                    else:
                        self.waiting_steps += 1
                        self.next_pos = self.pos
                else:
                    # Finished crossing, move right to exit
                    next_pos = (x + 1, y)
                    if next_pos[0] >= self.model.grid.width:
                        self.model.pedestrians_crossed += 1
                        self.model.total_pedestrian_time += self.model.schedule.time - self.spawn_time
                        self.remove_flag = True
                    else:
                        if not any(isinstance(a, CarAgent) for a in self.model.grid.get_cell_list_contents(next_pos)):
                            self.next_pos = next_pos
                            self.crossing = False
                        else:
                            self.waiting_steps += 1
                            self.next_pos = self.pos
            else:
                self.waiting_steps += 1
                self.next_pos = self.pos
                self.crossing = False
            return

        # Move toward intersection
        if x < x_light:
            next_pos = (x + 1, y)
            if not any(isinstance(a, (CarAgent, PedestrianAgent)) for a in self.model.grid.get_cell_list_contents(next_pos)):
                self.next_pos = next_pos
                self.waiting_steps = 0
            else:
                self.waiting_steps += 1
                self.next_pos = self.pos
        else:
            # Past intersection
            next_pos = (x + 1, y)
            if next_pos[0] >= self.model.grid.width:
                self.model.pedestrians_crossed += 1
                self.model.total_pedestrian_time += self.model.schedule.time - self.spawn_time
                self.remove_flag = True
            else:
                if not any(isinstance(a, CarAgent) for a in self.model.grid.get_cell_list_contents(next_pos)):
                    self.next_pos = next_pos
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
        # Emergency freeze only for cars before intersection
        if self.model.emergency_active:
            x, _ = self.pos
            if x < self.model.intersection_pos[0]:
                self.waiting_steps += 1
                self.next_pos = self.pos
                return

        x, y = self.pos
        next_pos = (x + 1, y)

        # Exit grid
        if next_pos[0] >= self.model.grid.width:
            self.model.cars_passed += 1
            self.model.total_travel_time += self.model.schedule.time - self.spawn_time
            self.remove_flag = True
            return

        # Intersection
        x_light, y_light = self.model.intersection_pos
        if next_pos == self.model.intersection_pos:
            if self.model.traffic_light.state == "GREEN":
                cell_agents = self.model.grid.get_cell_list_contents(next_pos)
                if not any(isinstance(a, (CarAgent, PedestrianAgent)) for a in cell_agents):
                    self.next_pos = next_pos
                    self.waiting_steps = 0
                else:
                    self.waiting_steps += 1
                    self.next_pos = self.pos
            else:
                self.waiting_steps += 1
                self.next_pos = self.pos
            return

        # Crosswalk one cell before intersection
        if next_pos[0] == x_light - 1 and next_pos[1] == y_light:
            crosswalk_cells = [(x_light, y_light-1), (x_light, y_light), (x_light, y_light+1)]
            if any(any(isinstance(a, PedestrianAgent) and a.crossing for a in self.model.grid.get_cell_list_contents(c)) for c in crosswalk_cells):
                self.waiting_steps += 1
                self.next_pos = self.pos
                return

        # Normal movement
        if not any(isinstance(a, (CarAgent, PedestrianAgent)) for a in self.model.grid.get_cell_list_contents(next_pos)):
            self.next_pos = next_pos
            self.waiting_steps = 0
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
# Emergency Vehicle Agent
# ---------------------------
class EmergencyVehicleAgent(Agent):
    def __init__(self, unique_id, model, spawn_time):
        super().__init__(unique_id, model)
        self.spawn_time = spawn_time
        self.next_pos = None
        self.remove_flag = False
        self.priority_active = True
        self.model.activate_emergency_mode(self)

    def step(self):
        x, y = self.pos
        next_pos = (x + 1, y)

        # Exit grid
        if next_pos[0] >= self.model.grid.width:
            self.remove_flag = True
            self.model.emergencies_cleared += 1
            return

        # Release emergency priority once past the intersection
        if self.priority_active and next_pos[0] > self.model.intersection_pos[0]:
            self.model.deactivate_emergency_mode(self)
            self.priority_active = False

        # Move freely except blocked by other emergencies
        cell_agents = self.model.grid.get_cell_list_contents(next_pos)
        if not any(isinstance(a, EmergencyVehicleAgent) and a != self for a in cell_agents):
            self.next_pos = next_pos
        else:
            self.next_pos = self.pos

    def advance(self):
        if self.remove_flag:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            if self.priority_active:
                self.model.deactivate_emergency_mode(self)
        else:
            self.model.grid.move_agent(self, self.next_pos)
            self.pos = self.next_pos

# ---------------------------
# Traffic Model
# ---------------------------
class TrafficModel(Model):
    def __init__(self, width=30, height=3, spawn_rate=0.15, green_duration=10, red_duration=10, 
                 pedestrian_spawn_rate=0.05, walk_duration=5, emergency_spawn_rate=0.01):
        super().__init__()
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = SimultaneousActivation(self)
        self.spawn_rate = spawn_rate
        self.pedestrian_spawn_rate = pedestrian_spawn_rate
        self.emergency_spawn_rate = emergency_spawn_rate

        self.intersection_pos = (width // 2, height // 2)
        self.cars_passed = 0
        self.total_travel_time = 0
        self.pedestrians_crossed = 0
        self.total_pedestrian_time = 0
        self.emergencies_cleared = 0
        self.emergency_active = False
        self.active_emergencies = set()

        # Traffic light
        self.traffic_light = TrafficLightAgent(
            "light", self,
            green_duration=green_duration,
            red_duration=red_duration,
            walk_duration=walk_duration
        )
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
                "PedestrianWaitTime": self.compute_avg_pedestrian_waiting_time,
                "EmergencyActive": lambda m: 1 if m.emergency_active else 0,
                "EmergenciesCleared": lambda m: m.emergencies_cleared
            }
        )

    # --- Metrics ---
    def compute_avg_travel_time(self):
        return 0 if self.cars_passed == 0 else self.total_travel_time / self.cars_passed

    def compute_avg_waiting_time(self):
        car_agents = [a for a in self.schedule.agents if isinstance(a, CarAgent)]
        return 0 if not car_agents else sum(a.waiting_steps for a in car_agents) / len(car_agents)

    def get_queue_length(self):
        x_light, y_light = self.intersection_pos
        count = 0
        for dx in range(1, 6):
            pos = (x_light - dx, y_light)
            if pos[0] >= 0:
                if any(isinstance(a, CarAgent) for a in self.grid.get_cell_list_contents(pos)):
                    count += 1
        return count

    def compute_avg_pedestrian_time(self):
        return 0 if self.pedestrians_crossed == 0 else self.total_pedestrian_time / self.pedestrians_crossed

    def compute_avg_pedestrian_waiting_time(self):
        ped_agents = [a for a in self.schedule.agents if isinstance(a, PedestrianAgent)]
        return 0 if not ped_agents else sum(a.waiting_steps for a in ped_agents) / len(ped_agents)

    # --- Emergency handling ---
    def activate_emergency_mode(self, emergency_agent):
        self.active_emergencies.add(emergency_agent.unique_id)
        self.emergency_active = True
        self.traffic_light.activate_emergency_mode()

    def deactivate_emergency_mode(self, emergency_agent):
        self.active_emergencies.discard(emergency_agent.unique_id)
        if not self.active_emergencies:
            self.emergency_active = False
            self.traffic_light.deactivate_emergency_mode()

    # --- Step ---
    def step(self):
        self.schedule.step()

        # Spawn cars
        start_pos = (0, self.grid.height // 2)
        if random.random() < self.spawn_rate:
            if not any(isinstance(a, CarAgent) for a in self.grid.get_cell_list_contents(start_pos)):
                car = CarAgent(self.next_id(), self, spawn_time=self.schedule.time)
                self.grid.place_agent(car, start_pos)
                car.next_pos = start_pos
                self.schedule.add(car)

        # Spawn pedestrians
        if random.random() < self.pedestrian_spawn_rate:
            spawn_row = random.choice([0, self.grid.height-1])
            ped_start_pos = (0, spawn_row)
            if not any(isinstance(a, (PedestrianAgent, CarAgent)) for a in self.grid.get_cell_list_contents(ped_start_pos)):
                pedestrian = PedestrianAgent(self.next_id(), self, spawn_time=self.schedule.time)
                pedestrian.target_row = self.grid.height-1 if spawn_row == 0 else 0
                self.grid.place_agent(pedestrian, ped_start_pos)
                pedestrian.next_pos = ped_start_pos
                self.schedule.add(pedestrian)

        # Spawn emergency vehicle
        if random.random() < self.emergency_spawn_rate and not self.emergency_active:
            emergency_start = (0, self.grid.height // 2)
            if not any(isinstance(a, (CarAgent, PedestrianAgent, EmergencyVehicleAgent)) for a in self.grid.get_cell_list_contents(emergency_start)):
                emergency = EmergencyVehicleAgent(self.next_id(), self, spawn_time=self.schedule.time)
                self.grid.place_agent(emergency, emergency_start)
                emergency.next_pos = emergency_start
                self.schedule.add(emergency)

        self.datacollector.collect(self)
