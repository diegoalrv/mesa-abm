import os
import traci
import time

SUMO_HOST = os.getenv("SUMO_HOST", "sumo-server")
SUMO_PORT = int(os.getenv("SUMO_PORT", "8813"))

if __name__ == "__main__":
    print(f"🚦 Connecting to SUMO at {SUMO_HOST}:{SUMO_PORT}...")
    traci.init(port=SUMO_PORT, host=SUMO_HOST)
    print("✅ Connected!")

    step = 0
    while traci.simulation.getMinExpectedNumber() > 0 and step < 100:
        traci.simulationStep()
        print(f"🌀 Step {step}")
        step += 1
        time.sleep(0.1)

    traci.close()
    print("🏁 Simulation finished.")
