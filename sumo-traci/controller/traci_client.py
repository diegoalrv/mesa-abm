import os
import traci
import time

SUMO_HOST = os.getenv("SUMO_HOST", "sumo-server")
SUMO_PORT = int(os.getenv("SUMO_PORT", "8813"))
MAX_RETRIES = 10
RETRY_DELAY = 2

def connect_to_sumo():
    """Intenta conectar a SUMO con reintentos"""
    for attempt in range(MAX_RETRIES):
        try:
            print(f"🚦 Intento {attempt + 1}/{MAX_RETRIES}: Conectando a SUMO en {SUMO_HOST}:{SUMO_PORT}...")
            traci.init(port=SUMO_PORT, host=SUMO_HOST)
            print("✅ Conexión exitosa!")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"⏳ Reintentando en {RETRY_DELAY} segundos...")
                time.sleep(RETRY_DELAY)
            else:
                print("💥 No se pudo conectar a SUMO después de varios intentos")
                return False

if __name__ == "__main__":
    if not connect_to_sumo():
        exit(1)

    step = 0
    max_steps = 200
    
    print(f"\n🌀 Iniciando simulación (máximo {max_steps} pasos)...\n")
    
    try:
        while traci.simulation.getMinExpectedNumber() > 0 and step < max_steps:
            traci.simulationStep()
            
            # Información de vehículos en cada paso
            vehicle_ids = traci.vehicle.getIDList()
            if vehicle_ids:
                print(f"⏱️  Paso {step:3d} | Vehículos activos: {len(vehicle_ids)} | IDs: {list(vehicle_ids)}")
            else:
                print(f"⏱️  Paso {step:3d} | Sin vehículos")
            
            step += 1
            time.sleep(0.05)  # Pausa corta para ver el progreso
            
    except KeyboardInterrupt:
        print("\n⚠️  Simulación interrumpida por el usuario")
    except Exception as e:
        print(f"\n💥 Error durante la simulación: {e}")
    finally:
        traci.close()
        print("\n🏁 Simulación finalizada")
        print(f"📊 Total de pasos ejecutados: {step}")