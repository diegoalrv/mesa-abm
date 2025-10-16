"""
Funciones de visualización para la interfaz web
"""

def agent_portrayal(agent):
    """Define cómo se visualiza cada agente"""
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Layer": 0,
        "r": 0.5
    }
    
    portrayal["Color"] = agent.color
    
    if agent.in_transit:
        if agent.current_mode == "walking":
            portrayal["Shape"] = "circle"
            portrayal["r"] = 0.3
        elif agent.current_mode == "bike":
            portrayal["Shape"] = "rect"
            portrayal["w"] = 0.4
            portrayal["h"] = 0.4
        elif agent.current_mode == "car":
            portrayal["Shape"] = "rect"
            portrayal["w"] = 0.6
            portrayal["h"] = 0.6
            portrayal["Color"] = "#dc3545"
        elif agent.current_mode == "bus":
            portrayal["Shape"] = "rect"
            portrayal["w"] = 0.5
            portrayal["h"] = 0.5
            portrayal["Color"] = "#007bff"
    
    return portrayal