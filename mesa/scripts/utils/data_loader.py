"""
Carga datos desde archivos CSV
"""
import pandas as pd
import os

class DataLoader:
    """
    Carga y procesa archivos de configuración
    """
    
    def __init__(self, data_dir="/app/data"):
        self.data_dir = data_dir
    
    def load_proba_car(self):
        """Carga probabilidades de tener auto por perfil"""
        return {
            "High School Student": 0.15,
            "College student": 0.14,
            "Young professional": 0.26,
            "Home maker": 0.87,
            "Mid-career workers": 0.54,
            "Executives": 0.71,
            "Retirees": 0.30
        }
    
    def load_proba_bike(self):
        """Carga probabilidades de tener bicicleta"""
        return {
            "High School Student": 0.05,
            "College student": 0.09,
            "Young professional": 0.05,
            "Home maker": 0.03,
            "Mid-career workers": 0.03,
            "Executives": 0.03,
            "Retirees": 0.03
        }
    
    def load_proportions(self):
        """Carga proporciones de cada perfil"""
        return {
            "High School Student": 0.077,
            "College student": 0.116,
            "Young professional": 0.248,
            "Home maker": 0.193,
            "Mid-career workers": 0.116,
            "Executives": 0.029,
            "Retirees": 0.221
        }
    
    def load_weights(self):
        """Carga pesos de decisión por perfil"""
        default_weights = [-0.2, -0.6, 0.2, -0.7]
        
        return {
            profile: {
                'work': default_weights,
                'home': default_weights,
                'leisure': default_weights
            }
            for profile in self.load_proportions().keys()
        }
    
    def load_modes(self):
        """Carga características de modos de transporte"""
        return {
            'walking': {
                'fix_price': 0,
                'price_per_km': 0.002,
                'waiting_time': 0.3,
                'speed': 3,
                'social_pattern': 0.1,
                'difficulty': 0,
                'weather_coeff': 0.5
            },
            'bike': {
                'fix_price': 0,
                'price_per_km': 0.01,
                'waiting_time': 1,
                'speed': 6,
                'social_pattern': 0.5,
                'difficulty': 0.1,
                'weather_coeff': 1.0
            },
            'car': {
                'fix_price': 0,
                'price_per_km': 0.32,
                'waiting_time': 2.5,
                'speed': 20,
                'social_pattern': 1.0,
                'difficulty': 0.2,
                'weather_coeff': 0.0
            },
            'bus': {
                'fix_price': 4,
                'price_per_km': 0,
                'waiting_time': 10,
                'speed': 20,
                'social_pattern': 0.15,
                'difficulty': 0.4,
                'weather_coeff': 0.2
            }
        }
    
    def load_activities(self):
        """Carga actividades por perfil y hora"""
        return {
            "Young professional": ["home"] * 7 + ["work"] * 9 + ["leisure"] * 3 + ["home"] * 5,
            "Retirees": ["home"] * 24,
            "High School Student": ["home"] * 7 + ["school"] * 8 + ["leisure"] * 4 + ["home"] * 5,
            "College student": ["home"] * 8 + ["school"] * 6 + ["leisure"] * 5 + ["home"] * 5,
            "Home maker": ["home"] * 24,
            "Mid-career workers": ["home"] * 7 + ["work"] * 9 + ["home"] * 8,
            "Executives": ["home"] * 6 + ["work"] * 11 + ["home"] * 7,
        }