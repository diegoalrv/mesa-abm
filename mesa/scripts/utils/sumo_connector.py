"""
Conector con SUMO vía TraCI - Versión con manejo de reconexión
"""
import traci
import time
import math

class SumoConnector:
    
    def __init__(self, host="sumo-server", port=8813, mesa_to_sumo_scale=10.0):
        self.host = host
        self.port = port
        self.connected = False
        self.mesa_to_sumo_scale = mesa_to_sumo_scale
        self._connect()
    
    def _connect(self):
        """Conecta a SUMO con reintentos y manejo de reconexión"""
        max_retries = 10
        
        # Primero intentar cerrar cualquier conexión existente
        try:
            traci.close()
            print("🔄 Conexión SUMO anterior cerrada")
            time.sleep(1)
        except:
            pass
        
        for attempt in range(max_retries):
            try:
                print(f"🚦 Intento {attempt + 1}/{max_retries}: Conectando a SUMO en {self.host}:{self.port}...")
                traci.init(port=self.port, host=self.host)
                self.connected = True
                print("✅ Conectado a SUMO exitosamente")
                return
            except Exception as e:
                # Si el error es "already active", intentar cerrar y reconectar
                if "already active" in str(e).lower():
                    try:
                        traci.close()
                        time.sleep(1)
                        traci.init(port=self.port, host=self.host)
                        self.connected = True
                        print("✅ Reconectado a SUMO exitosamente")
                        return
                    except:
                        pass
                
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    print(f"💥 No se pudo conectar a SUMO: {e}")
    
    def close(self):
        """Cierra la conexión SUMO"""
        if self.connected:
            try:
                traci.close()
                self.connected = False
                print("🔌 Conexión SUMO cerrada")
            except:
                pass
    
    def simulation_step(self):
        """Avanza un paso en SUMO"""
        if self.connected:
            try:
                traci.simulationStep()
            except Exception as e:
                print(f"⚠️ Error en simulation_step: {e}")
                self.connected = False
    
    def add_vehicle(self, vehicle_id, vehicle_type, origin, destination):
        """Agrega vehículo a SUMO en su edge más cercano"""
        if not self.connected:
            return False
        
        try:
            origin_sumo = self._mesa_to_sumo_coords(origin)
            dest_sumo = self._mesa_to_sumo_coords(destination)
            
            origin_edge = self._find_closest_edge(origin_sumo)
            dest_edge = self._find_closest_edge(dest_sumo)
            
            if not origin_edge or not dest_edge:
                print(f"⚠️ No se encontraron edges para {vehicle_id}")
                return False
            
            route_edges = self._calculate_route(origin_edge, dest_edge, vehicle_type)
            
            if not route_edges:
                print(f"⚠️ No se encontró ruta para {vehicle_id}")
                return False
            
            route_id = f"route_{vehicle_id}"
            traci.route.add(route_id, route_edges)
            
            sumo_vtype = self._map_vehicle_type(vehicle_type)
            
            traci.vehicle.add(
                vehID=vehicle_id,
                routeID=route_id,
                typeID=sumo_vtype,
                depart='now',
                departLane='best',
                departSpeed='max'
            )
            
            print(f"✅ Vehículo {vehicle_id} creado: {origin_edge} → {dest_edge}")
            return True
            
        except Exception as e:
            print(f"⚠️ Error al agregar vehículo {vehicle_id}: {e}")
            return False
    
    def _mesa_to_sumo_coords(self, mesa_coords):
        """Convierte coordenadas Mesa a SUMO"""
        if not isinstance(mesa_coords, tuple) or len(mesa_coords) != 2:
            return (0, 0)
        
        x_sumo = mesa_coords[0] * self.mesa_to_sumo_scale
        y_sumo = mesa_coords[1] * self.mesa_to_sumo_scale
        
        return (x_sumo, y_sumo)
    
    def _find_closest_edge(self, sumo_coords):
        """Encuentra el edge más cercano"""
        try:
            edges = traci.edge.getIDList()
            
            if not edges:
                return None
            
            min_distance = float('inf')
            closest_edge = None
            
            for edge_id in edges:
                try:
                    shape = traci.edge.getShape(edge_id)
                    
                    for point in shape:
                        distance = self._euclidean_distance(sumo_coords, point)
                        if distance < min_distance:
                            min_distance = distance
                            closest_edge = edge_id
                
                except:
                    continue
            
            return closest_edge
            
        except Exception as e:
            print(f"⚠️ Error buscando edge: {e}")
            return None
    
    def _euclidean_distance(self, point1, point2):
        """Calcula distancia euclidiana"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def _calculate_route(self, origin_edge, dest_edge, vehicle_type='car'):
        """Calcula ruta entre dos edges"""
        try:
            if origin_edge == dest_edge:
                return [origin_edge]
            
            route = traci.simulation.findRoute(
                fromEdge=origin_edge,
                toEdge=dest_edge,
                vType=self._map_vehicle_type(vehicle_type)
            )
            
            if route and route.edges:
                return list(route.edges)
            
            return [origin_edge, dest_edge]
            
        except Exception as e:
            print(f"⚠️ Error calculando ruta: {e}")
            return [origin_edge, dest_edge]
    
    def _map_vehicle_type(self, mesa_vehicle_type):
        """Mapea tipos de vehículo"""
        mapping = {
            'car': 'car',
            'bike': 'bicycle',
            'bus': 'bus',
            'walking': 'pedestrian'
        }
        return mapping.get(mesa_vehicle_type, 'car')
    
    def get_vehicle_position(self, vehicle_id):
        """Obtiene posición del vehículo"""
        if not self.connected:
            return None
        
        try:
            sumo_pos = traci.vehicle.getPosition(vehicle_id)
            mesa_pos = (
                sumo_pos[0] / self.mesa_to_sumo_scale,
                sumo_pos[1] / self.mesa_to_sumo_scale
            )
            return mesa_pos
        except:
            return None
    
    def get_vehicle_data(self, vehicle_id):
        """Obtiene datos del vehículo"""
        if not self.connected:
            return None
        
        try:
            return {
                'speed': traci.vehicle.getSpeed(vehicle_id),
                'max_speed': traci.vehicle.getMaxSpeed(vehicle_id),
                'position': self.get_vehicle_position(vehicle_id),
                'edge': traci.vehicle.getRoadID(vehicle_id)
            }
        except:
            return None
    
    def remove_vehicle(self, vehicle_id):
        """Remueve vehículo de SUMO"""
        if self.connected:
            try:
                traci.vehicle.remove(vehicle_id)
            except:
                pass

    def vehicle_exists(self, vehicle_id):
        """
        Verifica si un vehículo existe en la simulación
        
        Returns:
            bool: True si existe, False si no
        """
        if not self.connected:
            return False
        
        try:
            vehicle_list = traci.vehicle.getIDList()
            return vehicle_id in vehicle_list
        except:
            return False