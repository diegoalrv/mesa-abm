"""
Acción: Compartir información de tráfico con red social
"""

def share_info(agent):
    """Comparte información de congestión con amigos"""
    if not agent.in_transit or not agent.sumo_vehicle_id:
        return
    
    vehicle_data = agent.model.sumo_connector.get_vehicle_data(agent.sumo_vehicle_id)
    
    if not vehicle_data:
        return
    
    speed = vehicle_data.get('speed', 0)
    max_speed = vehicle_data.get('max_speed', 50)
    
    if speed < max_speed * 0.3:
        congestion_level = 1 - (speed / max_speed)
        
        traffic_info = {
            'location': agent.pos,
            'severity': congestion_level,
            'step': agent.model.schedule.steps,
            'reporter': agent.unique_id
        }
        
        for friend in agent.social_network:
            friend.received_traffic_info.append(traffic_info)
        
        print(f"📢 Agente {agent.unique_id} reporta congestión nivel {congestion_level:.2f}")