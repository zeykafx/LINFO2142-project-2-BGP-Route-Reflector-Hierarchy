#! /usr/bin/python3

from datetime import datetime, timedelta
import json
import sys
import subprocess
import time
from scripts.full_mesh_connectivity_tests import test_connectivity as full_mesh_test
from scripts.rr_hierarchy_connectivity_test import test_connectivity as hierarchy_test
from scripts.diversity_test import analyze_bgp_paths

def is_lab_running(lab_name):
    # Check if the lab is running by trying to access a router
    router = "RR1T" if lab_name == "hierarchy" else "R1"
    full_command = f"sudo docker exec -it clab-scenario-{lab_name}-{router} vtysh -c 'show bgp ipv6 unicast'"
    result = subprocess.run(full_command, shell=True, check=False, capture_output=True, text=True)
    if "No such container" in result.stderr:
        return False
    return True

def get_running_lab():
    if is_lab_running("hierarchy"):
        return "hierarchy"
    elif is_lab_running("full-mesh"):
        return "full_mesh"
    return None

def main():
    running_lab = get_running_lab()

    # Read lab info from JSON file
    try:
        with open(f'lab_info_{running_lab}.json', 'r') as f:
            lab_info = json.load(f)
    except FileNotFoundError:
        print("Error: lab_info.json not found. Please run start.py first")
        sys.exit(1)

    # Get lab name from info
    lab_name = lab_info.get('lab')
    if not lab_name:
        print("Error: Could not determine lab name")
        sys.exit(1)

    
    # Check if 30 seconds have passed since start time (Since ISIS convergence takes 30 seconds i think)
    start_time_timestamp = lab_info.get('timestamp')
    if not start_time_timestamp:
        print("Error: Could not determine start time")
        sys.exit(1)
    
    
    start_date = datetime.fromtimestamp(start_time_timestamp)
    current_date = datetime.now()
  
    if (current_date - start_date).seconds < 50:
        remaining = 50 - (current_date - start_date).seconds
        print(f"Waiting {remaining:.1f} seconds for ISIS to converge")
        for _ in range(int(remaining)):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
        print("\nConvergence time complete")

    print(f"Running connectivity tests for lab: {lab_name}")

    # Run appropriate test script
    if lab_name == 'hierarchy':
        hierarchy_test()
        analyze_bgp_paths(lab_name='hierarchy', router_name='RR1T')
    elif lab_name == 'full_mesh':
        full_mesh_test()
        analyze_bgp_paths(lab_name='full-mesh', router_name='R1')
    

if __name__ == "__main__":
    main()
 