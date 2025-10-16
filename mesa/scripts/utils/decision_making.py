"""
Utilidades para toma de decisiones multi-criterio
Implementa métodos de decisión para agentes
"""
import random
from typing import List, Dict, Any

def weighted_means_decision(candidates: List[Dict], weights: List[float]) -> int:
    """
    Weighted Means Decision Making
    
    Selecciona la mejor alternativa usando suma ponderada de criterios.
    Menor score = mejor opción (minimización)
    
    Args:
        candidates: Lista de diccionarios con estructura:
                   [{'mode': str, 'criteria': [c1, c2, c3, ...]}, ...]
        weights: Lista de pesos para cada criterio [w1, w2, w3, ...]
    
    Returns:
        int: Índice del candidato seleccionado
    
    Example:
        candidates = [
            {'mode': 'car', 'criteria': [0.8, 0.3, 0.9, 0.2]},
            {'mode': 'bike', 'criteria': [0.1, 0.7, 0.4, 0.6]},
            {'mode': 'walking', 'criteria': [0.0, 1.0, 0.2, 0.0]}
        ]
        weights = [-0.2, -0.6, 0.2, -0.7]  # negativos = minimizar
        
        result = weighted_means_decision(candidates, weights)
        # Retorna índice del mejor candidato
    """
    if not candidates:
        return -1
    
    if len(weights) != len(candidates[0].get('criteria', [])):
        print("⚠️ Warning: weights y criteria tienen longitudes diferentes")
        return 0
    
    scores = []
    
    for i, candidate in enumerate(candidates):
        criteria = candidate.get('criteria', [])
        
        # Calcular score ponderado
        score = sum(w * c for w, c in zip(weights, criteria))
        scores.append((score, i))
    
    # Retornar índice del candidato con menor score (mejor)
    best_candidate = min(scores, key=lambda x: x[0])
    return best_candidate[1]


def normalize_criteria(candidates: List[Dict], method='minmax') -> List[Dict]:
    """
    Normaliza criterios de candidatos entre 0-1
    
    Args:
        candidates: Lista de diccionarios con criterios
        method: 'minmax' o 'maxabs'
    
    Returns:
        Lista de candidatos con criterios normalizados
    """
    if not candidates:
        return candidates
    
    n_criteria = len(candidates[0].get('criteria', []))
    
    if method == 'minmax':
        # Min-Max normalization
        for i in range(n_criteria):
            values = [c['criteria'][i] for c in candidates]
            min_val = min(values)
            max_val = max(values)
            
            range_val = max_val - min_val
            if range_val == 0:
                range_val = 1.0
            
            for candidate in candidates:
                candidate['criteria'][i] = (candidate['criteria'][i] - min_val) / range_val
    
    elif method == 'maxabs':
        # Max absolute value normalization
        for i in range(n_criteria):
            values = [abs(c['criteria'][i]) for c in candidates]
            max_val = max(values) if values else 1.0
            
            if max_val == 0:
                max_val = 1.0
            
            for candidate in candidates:
                candidate['criteria'][i] = candidate['criteria'][i] / max_val
    
    return candidates


def topsis_decision(candidates: List[Dict], weights: List[float], 
                   beneficial_criteria: List[bool] = None) -> int:
    """
    TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
    
    Selecciona alternativa más cercana a la solución ideal y más lejana de la peor
    
    Args:
        candidates: Lista de candidatos con criterios
        weights: Pesos de importancia para cada criterio
        beneficial_criteria: Lista de bool indicando si cada criterio es beneficioso (True)
                           o de costo (False). Si None, asume todos son de costo.
    
    Returns:
        int: Índice del candidato seleccionado
    """
    if not candidates:
        return -1
    
    n_criteria = len(candidates[0].get('criteria', []))
    
    if beneficial_criteria is None:
        # Por defecto, criterios negativos = minimizar (costo)
        beneficial_criteria = [w > 0 for w in weights]
    
    # 1. Normalizar matriz de decisión
    normalized = []
    for i in range(n_criteria):
        values = [c['criteria'][i] for c in candidates]
        sum_squares = sum(v**2 for v in values)
        norm_factor = sum_squares**0.5 if sum_squares > 0 else 1.0
        
        for j, candidate in enumerate(candidates):
            if i == 0:
                normalized.append([])
            normalized[j].append(candidate['criteria'][i] / norm_factor)
    
    # 2. Aplicar pesos
    weighted = []
    for j in range(len(candidates)):
        weighted.append([normalized[j][i] * abs(weights[i]) for i in range(n_criteria)])
    
    # 3. Determinar solución ideal (A+) y peor (A-)
    ideal_best = []
    ideal_worst = []
    
    for i in range(n_criteria):
        values = [w[i] for w in weighted]
        
        if beneficial_criteria[i]:
            # Criterio beneficioso: mayor es mejor
            ideal_best.append(max(values))
            ideal_worst.append(min(values))
        else:
            # Criterio de costo: menor es mejor
            ideal_best.append(min(values))
            ideal_worst.append(max(values))
    
    # 4. Calcular distancias
    distances_best = []
    distances_worst = []
    
    for candidate_weighted in weighted:
        # Distancia euclidiana a la solución ideal
        dist_best = sum((candidate_weighted[i] - ideal_best[i])**2 
                       for i in range(n_criteria))**0.5
        distances_best.append(dist_best)
        
        # Distancia euclidiana a la peor solución
        dist_worst = sum((candidate_weighted[i] - ideal_worst[i])**2 
                        for i in range(n_criteria))**0.5
        distances_worst.append(dist_worst)
    
    # 5. Calcular cercanía relativa (closeness)
    closeness = []
    for i in range(len(candidates)):
        total_dist = distances_best[i] + distances_worst[i]
        if total_dist == 0:
            closeness.append(0)
        else:
            closeness.append(distances_worst[i] / total_dist)
    
    # 6. Retornar candidato con mayor closeness
    best_idx = closeness.index(max(closeness))
    return best_idx


def probabilistic_choice(candidates: List[Dict], weights: List[float], 
                        temperature: float = 1.0) -> int:
    """
    Selección probabilística basada en scores (softmax)
    
    Permite exploración estocástica en lugar de siempre elegir el mejor
    
    Args:
        candidates: Lista de candidatos
        weights: Pesos para criterios
        temperature: Controla aleatoriedad (0 = determinista, >1 = más aleatorio)
    
    Returns:
        int: Índice del candidato seleccionado probabilísticamente
    """
    if not candidates:
        return -1
    
    # Calcular scores
    scores = []
    for candidate in candidates:
        criteria = candidate.get('criteria', [])
        score = sum(w * c for w, c in zip(weights, criteria))
        scores.append(score)
    
    # Invertir scores para que menor = mejor
    scores = [-s for s in scores]
    
    # Aplicar softmax con temperatura
    import math
    
    # Normalizar para evitar overflow
    max_score = max(scores)
    exp_scores = [math.exp((s - max_score) / temperature) for s in scores]
    sum_exp = sum(exp_scores)
    
    probabilities = [e / sum_exp for e in exp_scores]
    
    # Selección probabilística
    rand = random.random()
    cumulative = 0
    
    for i, prob in enumerate(probabilities):
        cumulative += prob
        if rand <= cumulative:
            return i
    
    return len(candidates) - 1  # Fallback


def lexicographic_decision(candidates: List[Dict], weights: List[float]) -> int:
    """
    Decisión lexicográfica: ordena por el criterio más importante primero
    
    Args:
        candidates: Lista de candidatos
        weights: Pesos (determina orden de importancia por magnitud absoluta)
    
    Returns:
        int: Índice del candidato seleccionado
    """
    if not candidates:
        return -1
    
    # Ordenar criterios por importancia (peso absoluto)
    criteria_order = sorted(range(len(weights)), 
                          key=lambda i: abs(weights[i]), 
                          reverse=True)
    
    # Inicializar todos los candidatos como posibles
    possible_indices = list(range(len(candidates)))
    
    # Filtrar por cada criterio en orden de importancia
    for criterion_idx in criteria_order:
        if len(possible_indices) == 1:
            break
        
        # Obtener valores del criterio para candidatos restantes
        values = [(candidates[i]['criteria'][criterion_idx], i) 
                 for i in possible_indices]
        
        # Si el peso es negativo, minimizar; si positivo, maximizar
        if weights[criterion_idx] < 0:
            best_value = min(values, key=lambda x: x[0])[0]
        else:
            best_value = max(values, key=lambda x: x[0])[0]
        
        # Mantener solo los mejores en este criterio
        possible_indices = [i for v, i in values if v == best_value]
    
    return possible_indices[0]


def evaluate_alternatives(alternatives: List[str], 
                         criteria_values: Dict[str, List[float]],
                         weights: List[float],
                         method: str = 'weighted_means') -> str:
    """
    Función de alto nivel para evaluar alternativas
    
    Args:
        alternatives: Lista de nombres de alternativas ['car', 'bike', 'bus']
        criteria_values: Diccionario {alternative: [c1, c2, c3, ...]}
        weights: Pesos para cada criterio
        method: 'weighted_means', 'topsis', 'probabilistic', 'lexicographic'
    
    Returns:
        str: Nombre de la alternativa seleccionada
    
    Example:
        alternatives = ['car', 'bike', 'walking']
        criteria_values = {
            'car': [0.8, 0.3, 0.9, 0.2],
            'bike': [0.1, 0.7, 0.4, 0.6],
            'walking': [0.0, 1.0, 0.2, 0.0]
        }
        weights = [-0.2, -0.6, 0.2, -0.7]
        
        best = evaluate_alternatives(alternatives, criteria_values, weights)
    """
    # Convertir a formato de candidatos
    candidates = [
        {'mode': alt, 'criteria': criteria_values[alt]} 
        for alt in alternatives
    ]
    
    # Normalizar criterios
    candidates = normalize_criteria(candidates, method='maxabs')
    
    # Aplicar método de decisión
    if method == 'weighted_means':
        best_idx = weighted_means_decision(candidates, weights)
    elif method == 'topsis':
        best_idx = topsis_decision(candidates, weights)
    elif method == 'probabilistic':
        best_idx = probabilistic_choice(candidates, weights, temperature=1.5)
    elif method == 'lexicographic':
        best_idx = lexicographic_decision(candidates, weights)
    else:
        print(f"⚠️ Método desconocido: {method}, usando weighted_means")
        best_idx = weighted_means_decision(candidates, weights)
    
    if best_idx < 0 or best_idx >= len(alternatives):
        return alternatives[0]  # Fallback
    
    return alternatives[best_idx]