"""
Acción: Crear objetivos de viaje diarios
"""
import random

def create_daily_schedule(agent):
    """Crea la agenda diaria del agente basada en su perfil"""
    activities = agent.model.activity_per_profile.get(
        agent.profile_type,
        ["home"] * 24
    )
    
    agent.daily_schedule = []
    
    for hour, activity in enumerate(activities):
        if activity and activity != agent.current_activity:
            agent.daily_schedule.append({
                'hour': hour,
                'minute': random.randint(0, 59),
                'activity': activity
            })
    
    _create_trip_objectives(agent)
    
    # 🆕 AGREGAR: Crear algunos viajes inmediatos para testing
    _create_immediate_test_trips(agent)


def _create_immediate_test_trips(agent):
    """
    Crea 1-2 viajes inmediatos para testing
    Esto fuerza que algunos agentes viajen en los primeros minutos
    """
    # 20% de probabilidad de crear viaje inmediato
    if random.random() < 0.2:
        destination = _find_destination(agent, 'work')
        
        if destination:
            immediate_trip = {
                'hour': 0,  # Hora actual
                'minute': random.randint(1, 10),  # Primeros 10 minutos
                'activity': 'work',
                'destination': destination,
                'completed': False,
                'start_time': None
            }
            agent.trip_objectives.insert(0, immediate_trip)
            print(f"🆕 Agente {agent.unique_id}: viaje inmediato programado en minuto {immediate_trip['minute']}")


def _create_trip_objectives(agent):
    """Genera objetivos específicos de viaje"""
    agent.trip_objectives = []
    
    for schedule_item in agent.daily_schedule:
        destination = _find_destination(agent, schedule_item['activity'])
        
        if destination:
            objective = {
                'hour': schedule_item['hour'],
                'minute': schedule_item['minute'],
                'activity': schedule_item['activity'],
                'destination': destination,
                'completed': False,
                'start_time': None
            }
            agent.trip_objectives.append(objective)


def _find_destination(agent, activity):
    """Encuentra destino apropiado para la actividad"""
    options = activity.split('|')
    activity_type = random.choice(options)
    
    if activity_type in ['home', 'RM', 'RS', 'RL']:
        if not agent.home_location:
            agent.home_location = (
                random.randint(0, agent.model.grid.width - 1),
                random.randint(0, agent.model.grid.height - 1)
            )
        return agent.home_location
    
    elif activity_type in ['work', 'school', 'O', 'OS', 'OM', 'OL']:
        if not agent.work_location:
            agent.work_location = (
                random.randint(0, agent.model.grid.width - 1),
                random.randint(0, agent.model.grid.height - 1)
            )
        return agent.work_location
    
    else:
        return (
            random.randint(0, agent.model.grid.width - 1),
            random.randint(0, agent.model.grid.height - 1)
        )