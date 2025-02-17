import subprocess

def run_docker_command(router, command):
    # run a command in a docker container and return the output
    docker_command = f"docker exec clab-scenario-hierarchy-{router} {command}"
    result = subprocess.run(docker_command, shell=True, capture_output=True, text=True)
    return result.stdout

def ping_host(router, host_ip, count=1):
    output = run_docker_command(router, f"ping -c {count} {host_ip}")
    success = "0% packet loss" in output
    if not success:
        print(f"Error: {router} could not ping {host_ip}")
        print(f"Output: {output}")
    return success

def test_connectivity():
    routers = [
        'RR1T', 'RR2T',  # Top Route Reflectors
        'RR1S', 'RR2S',  "RR3S", 'RR4S', # Second Level Route Reflectors
        'R1', 'R2', 'R3', 'R4',  # Clients
        'R5', 'R6', 'R7', 'R8'   # Clients
    ]

    hosts = {
        'H1': 'fc00:2142:1:1::2',
        'H2': 'fc00:2142:1:2::2',
        'H3': 'fc00:2142:1:3::2',
        'AS2_H1': 'fc00:2142:a:2::2',  # host in AS 65010
        'AS3_H1': 'fc00:2142:b:2::2'   # host in AS 65020
    }

    # test connectivity from each router to each host
    results = []
    for router in routers:
        print(f"\nTesting connectivity from {router}...")
        for host_name, host_ip in hosts.items():
            success = ping_host(router, host_ip)
            results.append({
                'router': router,
                'host': host_name,
                'ip': host_ip,
                'success': success
            })
            status = "✓" if success else "✗"
            print(f"{router} → {host_name} ({host_ip}): {status}")

    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    RESET = '\033[0m'

    print("\nConnectivity Test Summary:")
    print("=" * 50)
    success_count = len([r for r in results if r['success']])
    total_tests = len(results)
    print(f"Total tests: {BLUE}{total_tests}{RESET}")
    print(f"Successful:  {GREEN}{success_count}{RESET}")
    print(f"Failed:  {RED}{total_tests - success_count}{RESET}")
    
    
    failed_tests = [r for r in results if not r['success']]
    if failed_tests:
        print("\nFailed Tests:")
        print("-" * 50)
        for test in failed_tests:
            print(f"{test['router']} → {test['host']} ({test['ip']})")

if __name__ == "__main__":
    print("Starting connectivity tests...")
    print("Testing connectivity between all routers and hosts...")
    test_connectivity()
