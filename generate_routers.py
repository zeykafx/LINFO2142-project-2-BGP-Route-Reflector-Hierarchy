import os
from jinja2 import Environment, FileSystemLoader

# Define the template directory and the output directory
template_dir = './templates'
scripts_dir = './clab-scenario-hierarchy'

# Create the environment and load the template
env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)

def generate_top_level_rr():
    template_top_rr = env.get_template("top_rr.jinja")

    # Define the contexts for each router
    contexts = []
    for i in range(1, 3):  # Assuming we have 2 RRs: RR1T and RR2T
        hostname = f'RR{i}T'
        bgp_router_cluster_id = f'1.0.0.{i}'
        net = f'49.0001.0000.0000.000{i}.00'
        # Interface connecting to the other top-level peer
        interfaces = [
            {'name': f'eth-rr{3-i}t', 'ipv6_address': f'fc00:2142:1:2::{i}/64'}
        ]
        for j in range(1, 5):
            interfaces.append({'name': f'eth-rr{j}s', 'ipv6_address': f'fc00:2142:1:{i}{j}::1/64'})
        loopback = {'ipv6_address': f'fc00:2142:1::{i}/128'}
        context = {
            'hostname': hostname,
            'bgp_router_cluster_id': bgp_router_cluster_id,
            'net': net,
            'interfaces': interfaces,
            'loopback': loopback,
        }
        contexts.append(context)

    # Generate configuration files for each context
    for ctx in contexts:
        output = template_top_rr.render(ctx)
        output_dir = f"{scripts_dir}/{ctx['hostname']}"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'frr.conf')
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"Configuration file generated at {output_file}")


def generate_second_level_rr():
    template_second_rr = env.get_template('second_rr.jinja')

    # Define contexts for second level RRs (RR1S through RR4S)
    contexts = []
    for i in range(1, 5):
        hostname = f'RR{i}S'
        bgp_router_cluster_id = f'2.0.0.{i}'
        net = f'49.0001.0000.0000.000{i+2}.00'
        
        # Interfaces connecting to top-level RRs
        top_rr_interfaces = [
            {'name': 'eth-rr1t', 'ipv6_address': f'fc00:2142:1:1{i}::2/64'},
            {'name': 'eth-rr2t', 'ipv6_address': f'fc00:2142:1:2{i}::2/64'}
        ]
        
        # Client interfaces
        client_interfaces = [
            {'name': f'eth-r{(i+1)//2}', 'ipv6_address': f'fc00:2142:1:{i+2}1::1/64'}
        ]
        
        loopback = {'ipv6_address': f'fc00:2142:1::{i+2}/128'}
        
        context = {
            'hostname': hostname,
            'bgp_router_cluster_id': bgp_router_cluster_id,
            'net': net,
            'top_rr_interfaces': top_rr_interfaces,
            'client_interfaces': client_interfaces,
            'loopback': loopback,
            'has_external_peer': (i == 4),  # Only RR4S has external peer
            'has_host': (i == 1),  # Only RR1S has host interface
        }
        
        # Add host interface for RR1S
        if i == 1:
            context['host_interface'] = {
                'name': 'eth-h2',
                'ipv6_address': 'fc00:2142:1:33::1/64'
            }
            context['host_prefix'] = 'fc00:2142:1:33::1/64'
            
        contexts.append(context)

    # Generate configuration files
    for ctx in contexts:
        output = template_second_rr.render(ctx)
        output_dir = f"{scripts_dir}/{ctx['hostname']}"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'frr.conf')
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"Configuration file generated at {output_file}")


def generate_regular_routers():
    template_regular = env.get_template('regular_router.jinja')
    
    # Define contexts for regular routers (R1 through R8)
    contexts = []
    for i in range(1, 9):
        hostname = f'R{i}'
        bgp_router_id = f'3.0.0.{i}'
        net = f'49.0001.0000.0000.00{i+10:02d}.00'
        
        # Each router connects to two RRs based on position
        rr_pair = ((i-1) // 4) * 2 + 1  # This will give 1 for R1-R4, and 3 for R5-R8
        # basically, R1-R4 connect to RR1S and RR2S, while R5-R8 connect to RR3S and RR4S
        rr_interfaces = [
            {'name': f'eth-rr{rr_pair}s', 'ipv6_address': f'fc00:2142:1:{(rr_pair+2)*10+1}::2/64'},
            {'name': f'eth-rr{rr_pair+1}s', 'ipv6_address': f'fc00:2142:1:{(rr_pair+3)*10+1}::2/64'}
        ]
        
        loopback = {'ipv6_address': f'fc00:2142:1::{i+10:02d}/128'}
        
        context = {
            'hostname': hostname,
            'bgp_router_id': bgp_router_id,
            'net': net,
            'rr_interfaces': rr_interfaces,
            'loopback': loopback,
        }
        contexts.append(context)

    # Generate configuration files
    for ctx in contexts:
        output = template_regular.render(ctx)
        output_dir = f"{scripts_dir}/{ctx['hostname']}"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'frr.conf')
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"Configuration file generated at {output_file}")

def generate_clab_file():
    template_clab = env.get_template('clab_file.jinja')

    # Generate configuration file
    output = template_clab.render()
    output_dir = scripts_dir
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'hierarchy.clab.yml')
    with open(output_file, 'w') as f:
        f.write(output)
    print(f"Containerlab file generated at {output_file}")


if __name__ == '__main__':
    generate_clab_file()
    generate_top_level_rr()
    generate_second_level_rr()
    generate_regular_routers()
