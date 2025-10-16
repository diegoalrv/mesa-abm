"""
Acción: Ejecutar viaje usando SUMO
"""

def check_and_execute_trip(agent):
    """Verifica si es hora de iniciar un viaje"""
    current_step = agent.model.schedule.steps
    current_hour = (current_step // 60) % 24
    current_minute = current_step % 60
    
    for objective in agent.trip_objectives:
        if (objective['hour'] == current_hour and
            objective['minute'] <= current_minute and
            not objective['completed'] and
            not agent.in_transit):
            
            _start_trip(agent, objective)
            break


def _start_trip(agent, objective):
    """Inicia un viaje hacia el objetivo"""
    from actions.choose_mode import choose_transport_mode
    
    mode = choose_transport_mode(agent, objective['destination'])
    
    # Walking sin SUMO
    if mode == 'walking':
        _handle_walking_trip(agent, objective)
    else:
        _spawn_in_sumo(agent, mode, objective['destination'])
    
    agent.current_objective = objective
    agent.current_mode = mode
    agent.in_transit = True
    agent.liveness = 360
    objective['start_time'] = agent.model.schedule.steps
    
    print(f"🚗 Agente {agent.unique_id} inicia viaje en {mode} hacia {objective['activity']}")


def _handle_walking_trip(agent, objective):
    """Maneja viajes a pie sin SUMO"""
    distance = _calculate_distance(agent.pos, objective['destination'])
    walking_speed = 3
    estimated_time = int((distance / walking_speed) * 60)
    
    agent.walking_arrival_step = agent.model.schedule.steps + max(1, estimated_time)
    agent.walking_destination = objective['destination']


def _calculate_distance(pos1, pos2):
    """Calcula distancia"""
    if isinstance(pos1, tuple) and isinstance(pos2, tuple):
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
    return 10.0


def _spawn_in_sumo(agent, mode, destination):
    """Crea vehículo en SUMO"""
    agent.sumo_vehicle_id = f"agent_{agent.unique_id}_{mode}_{agent.model.schedule.steps}"
    
    success = agent.model.sumo_connector.add_vehicle(
        vehicle_id=agent.sumo_vehicle_id,
        vehicle_type=mode,
        origin=agent.pos,
        destination=destination
    )
    
    if not success:
        print(f"⚠️ No se pudo crear vehículo en SUMO para agente {agent.unique_id}")
        agent.in_transit = False
        agent.sumo_vehicle_id = None


def update_trip_status(agent):
    """Actualiza estado del viaje"""
    
    # Manejo walking
    if agent.current_mode == 'walking':
        _update_walking_status(agent)
        return
    
    # Para otros modos, verificar existencia primero
    if not agent.sumo_vehicle_id:
        return
    
    # ✅ NUEVO: Verificar si el vehículo existe antes de consultar
    if not agent.model.sumo_connector.vehicle_exists(agent.sumo_vehicle_id):
        # Vehículo ya no existe = llegó al destino
        _complete_trip(agent)
        return
    
    # Obtener posición
    position = agent.model.sumo_connector.get_vehicle_position(agent.sumo_vehicle_id)
    
    if position is None:
        _complete_trip(agent)
        return
    
    # Actualizar posición en grilla
    grid_x = min(int(position[0]), agent.model.grid.width - 1)
    grid_y = min(int(position[1]), agent.model.grid.height - 1)
    
    grid_x = max(0, grid_x)
    grid_y = max(0, grid_y)
    
    agent.model.grid.move_agent(agent, (grid_x, grid_y))


def _update_walking_status(agent):
    """Actualiza estado de viaje a pie"""
    if agent.model.schedule.steps >= getattr(agent, 'walking_arrival_step', 0):
        destination = getattr(agent, 'walking_destination', agent.pos)
        
        dest_x = min(max(0, destination[0]), agent.model.grid.width - 1)
        dest_y = min(max(0, destination[1]), agent.model.grid.height - 1)
        
        agent.model.grid.move_agent(agent, (dest_x, dest_y))
        _complete_trip(agent)


def _complete_trip(agent):
    """Completa el viaje actual"""
    if not agent.current_objective:
        return
    
    print(f"✅ Agente {agent.unique_id} completó viaje a {agent.current_objective['activity']}")
    
    agent.in_transit = False
    agent.current_objective['completed'] = True
    agent.current_activity = agent.current_objective['activity']
    agent.current_location = agent.current_objective['destination']
    
    from actions.learn_from_trip import learn_from_experience
    learn_from_experience(agent)
    
    # Limpiar
    if agent.sumo_vehicle_id:
        agent.model.sumo_connector.remove_vehicle(agent.sumo_vehicle_id)
        agent.sumo_vehicle_id = None
    
    agent.current_objective = None
    agent.liveness = 360
    
    if hasattr(agent, 'walking_arrival_step'):
        delattr(agent, 'walking_arrival_step')
    if hasattr(agent, 'walking_destination'):
        delattr(agent, 'walking_destination')