import os
import sys
import subprocess
import pandas as pd
import libsumo

OUTPUT_PATH = "data/outputs/vehicles_positions.csv"

def generate_network():
    """Generate network using netconvert from nodes and edges files"""
    print("Generating network from nodes and edges...")
    config_dir = "config"
    
    cmd = [
        "netconvert",
        "-n", os.path.join(config_dir, "nodes.nod.xml"),
        "-e", os.path.join(config_dir, "edges.edg.xml"),
        "-o", os.path.join(config_dir, "network.net.xml")
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error generating network: {result.stderr}")
            return False
        print("Network generated successfully")
        return True
    except Exception as e:
        print(f"Error running netconvert: {e}")
        return False

def main():
    print("Starting SUMO simulation (headless)...")
    
    # Generate network first
    if not generate_network():
        sys.exit(1)

    # Get the config path
    sumocfg_path = os.path.join("config", "simulation.sumocfg")
    
    if not os.path.exists(sumocfg_path):
        print(f"Error: Configuration file not found at {sumocfg_path}")
        sys.exit(1)

    try:
        libsumo.start(["sumo", "-c", sumocfg_path, "--no-step-log", "true"])
    except Exception as e:
        print(f"Error starting SUMO: {e}")
        sys.exit(1)

    records = []
    step = 0
    
    try:
        while libsumo.simulation.getMinExpectedNumber() > 0:
            libsumo.simulationStep()
            for veh_id in libsumo.vehicle.getIDList():
                pos = libsumo.vehicle.getPosition(veh_id)
                speed = libsumo.vehicle.getSpeed(veh_id)
                edge_id = libsumo.vehicle.getRoadID(veh_id)
                lon, lat = libsumo.simulation.convertGeo(pos[0], pos[1])
                records.append({
                    "timestep": step,
                    "veh_id": veh_id,
                    "lon": lon,
                    "lat": lat,
                    "speed": speed,
                    "edge_id": edge_id
                })
            step += 1
    finally:
        libsumo.close()

    if records:
        df = pd.DataFrame(records)
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        df.to_csv(OUTPUT_PATH, index=False)
        print(f"Simulation finished. Results saved to {OUTPUT_PATH}")
        print(f"Total steps: {step}")
        print(f"Total records: {len(records)}")
    else:
        print("No simulation data collected")

if __name__ == "__main__":
    main()