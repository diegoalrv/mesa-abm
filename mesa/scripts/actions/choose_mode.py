"""
Acción: Elegir modo de transporte
"""
import random

def _get_available_modes(agent):
    """Retorna modos disponibles"""
    modes = []
    
    # ✅ TEMPORAL: Priorizar car/bike para testing
    if agent.has_car:
        modes.append('car')
    
    if agent.has_bike:
        modes.append('bike')
    
    # Solo walking como último recurso
    if not modes:
        modes.append('walking')
    
    return modes

# def _get_available_modes(agent):
#     """Retorna modos disponibles"""
#     modes = ['walking']
    
#     if agent.has_car:
#         modes.append('car')
    
#     if agent.has_bike:
#         modes.append('bike')
    
#     modes.append('bus')
    
#     return modes


def _calculate_distance(pos1, pos2):
    """Calcula distancia"""
    if isinstance(pos1, tuple) and isinstance(pos2, tuple):
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
    return 10.0


def _normalize_criteria(candidates):
    """Normaliza criterios"""
    if not candidates:
        return candidates
    
    n_criteria = len(candidates[0]['criteria'])
    
    max_values = []
    for i in range(n_criteria):
        max_val = max(abs(c['criteria'][i]) for c in candidates)
        max_values.append(max_val if max_val > 0 else 1.0)
    
    for cand in candidates:
        cand['criteria'] = [
            c / max_val for c, max_val in zip(cand['criteria'], max_values)
        ]
    
    return candidates


def _weighted_decision(candidates, weights):
    """Weighted means decision making"""
    scores = []
    
    for cand in candidates:
        score = sum(w * c for w, c in zip(weights, cand['criteria']))
        scores.append((score, cand['mode']))
    
    return min(scores, key=lambda x: x[0])[1]


def choose_transport_mode(agent, destination):
    """Elige modo de transporte usando weighted decision making"""
    
    available_modes = _get_available_modes(agent)
    
    if not available_modes:
        return 'walking'
    
    candidates = []
    
    for mode in available_modes:
        mode_data = agent.model.modes_characteristics.get(mode, {})
        
        distance = _calculate_distance(agent.pos, destination)
        
        price = mode_data.get('fix_price', 0) + mode_data.get('price_per_km', 0) * distance
        time = mode_data.get('waiting_time', 0) + distance / max(mode_data.get('speed', 1), 0.1)
        social = mode_data.get('social_pattern', 0.5)
        difficulty = mode_data.get('difficulty', 0.5)
        
        if agent.model.weather_impact:
            weather_coeff = mode_data.get('weather_coeff', 0.5)
            difficulty *= (1.0 + agent.model.weather_of_day * weather_coeff)
        
        candidates.append({
            'mode': mode,
            'criteria': [price, time, social, difficulty]
        })
    
    candidates = _normalize_criteria(candidates)
    
    weights = agent.weights.get('work', [0.25, 0.25, 0.25, 0.25])
    best_mode = _weighted_decision(candidates, weights)
    
    agent.model.transport_usage[best_mode] += 1
    
    return best_mode