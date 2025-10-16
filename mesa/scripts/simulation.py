"""
Entry point principal de la simulación Mesa + SUMO
"""
import os
from models.mobility_model import MobilityModel
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from visualization.portrayals import agent_portrayal

def run_simulation():
    """Ejecuta la simulación con visualización web"""
    
    N_AGENTS = int(os.getenv("N_AGENTS", "50"))
    GRID_WIDTH = 50
    GRID_HEIGHT = 50
    
    grid = CanvasGrid(agent_portrayal, GRID_WIDTH, GRID_HEIGHT, 800, 800)
    
    chart_transport = ChartModule([
        {"Label": "Walking", "Color": "#28a745"},
        {"Label": "Bike", "Color": "#ffc107"},
        {"Label": "Car", "Color": "#dc3545"},
        {"Label": "Bus", "Color": "#007bff"}
    ], data_collector_name="datacollector")
    
    chart_activities = ChartModule([
        {"Label": "Home", "Color": "#6c757d"},
        {"Label": "Work", "Color": "#17a2b8"},
        {"Label": "Leisure", "Color": "#e83e8c"}
    ], data_collector_name="datacollector")
    
    server = ModularServer(
        MobilityModel,
        [grid, chart_transport, chart_activities],
        "Mesa + SUMO Mobility Simulation",
        {
            "n_agents": N_AGENTS,
            "width": GRID_WIDTH,
            "height": GRID_HEIGHT,
            "sumo_host": os.getenv("SUMO_HOST", "sumo-server"),
            "sumo_port": int(os.getenv("SUMO_PORT", "8813"))
        }
    )
    
    server.port = 8521
    server.launch()

if __name__ == "__main__":
    print("🚀 Iniciando Mesa + SUMO Simulation...")
    run_simulation()