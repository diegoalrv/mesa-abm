"""
Acción: Aprender de la experiencia de viaje
"""

def learn_from_experience(agent):
    """Registra y aprende del viaje completado"""
    if not agent.current_objective:
        return
    
    start_time = agent.current_objective.get('start_time', 0)
    actual_time = agent.model.schedule.steps - start_time
    
    trip_record = {
        'origin': agent.pos,
        'destination': agent.current_objective['destination'],
        'mode': agent.current_mode,
        'actual_time': actual_time,
        'weather': agent.model.weather_of_day,
        'step': agent.model.schedule.steps
    }
    
    agent.travel_history.append(trip_record)
    
    expected_time = _estimate_travel_time(agent, agent.current_mode, 
                                         agent.current_objective['destination'])
    
    if actual_time > expected_time * 1.5:
        delay = actual_time - expected_time
        route_key = (agent.pos, agent.current_objective['destination'])
        
        if route_key not in agent.learned_delays:
            agent.learned_delays[route_key] = []
        
        agent.learned_delays[route_key].append(delay)
        
        print(f"📚 Agente {agent.unique_id} aprendió delay de {delay} min en ruta")


def _estimate_travel_time(agent, mode, destination):
    """Estima tiempo de viaje esperado"""
    mode_data = agent.model.modes_characteristics.get(mode, {})
    speed = mode_data.get('speed', 5)
    
    if isinstance(agent.pos, tuple) and isinstance(destination, tuple):
        distance = ((agent.pos[0] - destination[0])**2 + 
                   (agent.pos[1] - destination[1])**2)**0.5
    else:
        distance = 10
    
    time = (distance / speed) * 60 if speed > 0 else 30
    
    return time