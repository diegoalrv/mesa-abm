"""
Agente ciudadano con comportamiento cognitivo y decisiones de movilidad
"""
from mesa import Agent
import random

class CitizenAgent(Agent):
    """Agente que representa una persona con rutinas, decisiones y movilidad"""
    
    def __init__(self, unique_id, model, profile_type):
        super().__init__(unique_id, model)
        
        self.profile_type = profile_type
        self.age = self._assign_age()
        self.color = self._assign_color()
        
        self.has_car = random.random() < model.proba_car_per_type.get(profile_type, 0.5)
        self.has_bike = random.random() < model.proba_bike_per_type.get(profile_type, 0.1)
        
        self.home_location = None
        self.work_location = None
        self.current_location = None
        
        self.current_activity = "home"
        self.current_mode = None
        self.in_transit = False
        self.sumo_vehicle_id = None
        
        self.daily_schedule = []
        self.trip_objectives = []
        self.current_objective = None
        
        self.weights = {}
        
        self.travel_history = []
        self.learned_delays = {}
        
        self.social_network = []
        self.received_traffic_info = []
        
        self.liveness = 360
        
    def _assign_age(self):
        """Asigna edad según perfil"""
        age_ranges = {
            "High School Student": (14, 18),
            "College student": (18, 25),
            "Young professional": (25, 35),
            "Mid-career workers": (35, 50),
            "Executives": (40, 60),
            "Home maker": (25, 60),
            "Retirees": (60, 85)
        }
        low, high = age_ranges.get(self.profile_type, (25, 65))
        return random.randint(low, high)
    
    def _assign_color(self):
        """Asigna color según perfil"""
        colors = {
            "High School Student": "#FFFFB2",
            "College student": "#FECC5C",
            "Young professional": "#FD8D3C",
            "Mid-career workers": "#F03B20",
            "Executives": "#BD0026",
            "Home maker": "#0B5038",
            "Retirees": "#8CAB13"
        }
        return colors.get(self.profile_type, "#CCCCCC")
    
    def step(self):
        """Ejecutado cada tick de simulación"""
        if not self.in_transit:
            self._check_for_new_objective()
        
        if self.in_transit and self.sumo_vehicle_id:
            self._update_from_sumo()
        
        if random.random() < 0.1:
            self._share_traffic_info()
        
        if self.in_transit:
            self.liveness -= 1
            if self.liveness <= 0:
                self._handle_stuck()
    
    def _check_for_new_objective(self):
        """Verifica si es hora de iniciar un nuevo viaje"""
        from actions.execute_trip import check_and_execute_trip
        check_and_execute_trip(self)
    
    def _update_from_sumo(self):
        """Consulta estado del vehículo en SUMO"""
        from actions.execute_trip import update_trip_status
        update_trip_status(self)
    
    def _share_traffic_info(self):
        """Comparte información de tráfico con red social"""
        from actions.share_traffic_info import share_info
        share_info(self)
    
    def _handle_stuck(self):
        """Maneja agente atascado"""
        print(f"⚠️ Agente {self.unique_id} atascado, reiniciando...")
        self.in_transit = False
        self.current_objective = None
        self.liveness = 360
        
        if self.sumo_vehicle_id:
            try:
                self.model.sumo_connector.remove_vehicle(self.sumo_vehicle_id)
            except:
                pass
            self.sumo_vehicle_id = None