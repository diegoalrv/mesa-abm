"""
Modelo principal de simulación de movilidad
"""
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents.citizen_agent import CitizenAgent
from utils.sumo_connector import SumoConnector
from utils.data_loader import DataLoader
import random

class MobilityModel(Model):
    """Modelo de simulación de movilidad urbana"""
    
    def __init__(self, n_agents=50, width=50, height=50, 
                 sumo_host="sumo-server", sumo_port=8813):
        super().__init__()
        
        self.n_agents = n_agents
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        
        # Conexión SUMO
        self.sumo_connector = SumoConnector(
            sumo_host, 
            sumo_port, 
            mesa_to_sumo_scale=10.0
        )
        
        # Cargar datos
        self.data_loader = DataLoader()
        self.proba_car_per_type = self.data_loader.load_proba_car()
        self.proba_bike_per_type = self.data_loader.load_proba_bike()
        self.proportion_per_type = self.data_loader.load_proportions()
        self.weights_map = self.data_loader.load_weights()
        self.modes_characteristics = self.data_loader.load_modes()
        self.activity_per_profile = self.data_loader.load_activities()
        
        # Clima
        self.weather_impact = True
        self.weather_of_day = random.uniform(0, 1)
        
        # Estadísticas
        self.transport_usage = {
            "walking": 0,
            "bike": 0,
            "car": 0,
            "bus": 0
        }
        
        # Data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Walking": lambda m: m.transport_usage["walking"],
                "Bike": lambda m: m.transport_usage["bike"],
                "Car": lambda m: m.transport_usage["car"],
                "Bus": lambda m: m.transport_usage["bus"],
                "Home": lambda m: sum(1 for a in m.schedule.agents if a.current_activity == "home"),
                "Work": lambda m: sum(1 for a in m.schedule.agents if a.current_activity in ["work", "school"]),
                "Leisure": lambda m: sum(1 for a in m.schedule.agents if a.current_activity == "leisure")
            }
        )
        
        # Crear agentes
        self._create_agents()
        
        print(f"✅ Modelo inicializado con {n_agents} agentes")
    
    def _create_agents(self):
        """Crea los agentes ciudadanos"""
        from actions.create_objectives import create_daily_schedule
        
        for i in range(self.n_agents):
            profile = self._select_profile()
            
            agent = CitizenAgent(i, self, profile)
            
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))
            
            self.schedule.add(agent)
            
            create_daily_schedule(agent)
    
    def _select_profile(self):
        """Selecciona perfil según proporciones"""
        profiles = list(self.proportion_per_type.keys())
        weights = list(self.proportion_per_type.values())
        return random.choices(profiles, weights=weights)[0]
    
    def step(self):
        """Avanza un paso la simulación"""
        self.schedule.step()
        
        self.sumo_connector.simulation_step()
        
        self.datacollector.collect(self)
        
        if self.schedule.steps % 1440 == 0:
            self.weather_of_day = random.uniform(0, 1)
    
    def __del__(self):
        """Limpieza al destruir el modelo"""
        try:
            self.sumo_connector.close()
        except:
            pass