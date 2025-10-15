import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
import random

# ----------------------------------------------------
# Definir agente
# ----------------------------------------------------
class Walker(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.steps = 0

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
        self.steps += 1

    def step(self):
        self.move()

# ----------------------------------------------------
# Definir modelo
# ----------------------------------------------------
class WalkingModel(Model):
    def __init__(self, N=10, width=10, height=10):
        super().__init__()  # ✅ importante para Mesa 2.2+
        self.num_agents = N
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)
        self.datacollector = DataCollector(
            model_reporters={"TotalSteps": self.total_steps},
            agent_reporters={"Steps": "steps"}
        )

        for i in range(self.num_agents):
            agent = Walker(i, self)
            self.schedule.add(agent)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

    def total_steps(self):
        return sum([a.steps for a in self.schedule.agents])

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

# ----------------------------------------------------
# Visualización
# ----------------------------------------------------
def agent_portrayal(agent):
    # Assign a color based on the agent's unique_id for consistency
    random.seed(agent.unique_id)
    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    return {
        "Shape": "circle",
        "Color": color,
        "Filled": "true",
        "r": 0.5,
        "Layer": 0,
    }

grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
chart = ChartModule([{"Label": "TotalSteps", "Color": "Blue"}])

server = ModularServer(
    WalkingModel,
    [grid, chart],
    "First Mesa Model",
    {"N": 10, "width": 10, "height": 10}
)
server.port = 8521

if __name__ == "__main__":
    print("🚀 Iniciando servidor de Mesa en http://localhost:8521 ...")
    server.launch()
