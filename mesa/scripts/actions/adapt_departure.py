"""
Acción: Adaptar hora de salida según delays aprendidos
"""

def adjust_departure_time(agent, objective):
    """Ajusta hora de salida si se han aprendido delays en la ruta"""
    route_key = (agent.pos, objective['destination'])
    
    if route_key in agent.learned_delays:
        avg_delay = sum(agent.learned_delays[route_key]) / len(agent.learned_delays[route_key])
        
        original_minute = objective['minute']
        adjusted_minute = max(0, original_minute - int(avg_delay))
        
        objective['minute'] = adjusted_minute
        
        print(f"⏰ Agente {agent.unique_id} adelanta salida {int(avg_delay)} min")