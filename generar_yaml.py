"""
This module generates a YAML configuration file
that includes a server and a specified number of clients.
"""

from sys import argv, stderr, exit as sys_exit
import yaml

try:
    yaml_file_name = argv[1]
    n_clients = int(argv[2])
    if n_clients < 0:
        raise ValueError('number of clients must be an integer')
except ValueError as e:
    print(f'Error: {e}', file=stderr)
    sys_exit(-1)
except IndexError:
    print(f'Usage: ./{argv[0]} [dest YAML file] [number of clients]', file=stderr)
    sys_exit(-1)

PROJECT_NAME = 'tp0'
DRIVER_TYPE = 'default'
SUBNET_ADDR = '172.25.125.0/24'

NETWORK_TEST_NAME = 'testing_net'

SERVER_NAME = 'server'
SERVER_IMG = 'server:latest'
SERVER_ENTRYPOINT = 'python3 /main.py'
SERVER_CONFIG = 'config.ini'
SERVER_NET = [
    NETWORK_TEST_NAME
]
SERVER_VOLUMES = [{
    'type': 'bind',
    'source': f'./server/{SERVER_CONFIG}',
    'target': f'/{SERVER_CONFIG}',
}]

CLIENT_ENTRYPOINT = '/client'
CLIENT_IMG = 'client:latest'
CLIENT_NET = [
    NETWORK_TEST_NAME,
]
CLIENT_CONFIG = 'config.yaml'
CLIENT_VOLUMES = [{
    'type': 'bind',
    'source': f'./client/{CLIENT_CONFIG}',
    'target': f'/{CLIENT_CONFIG}',
}]
CLIENT_DEPENDENCIES = [
    'server',
]

BASE_YAML = {
    'name': PROJECT_NAME,
    'services': {
        'server': {
            'container_name': SERVER_NAME,
            'image': SERVER_IMG,
            'entrypoint': SERVER_ENTRYPOINT,
            'networks': SERVER_NET,
            'volumes': SERVER_VOLUMES,
        }
    },
    'networks': {
        NETWORK_TEST_NAME: {
            'ipam': {
                'driver': DRIVER_TYPE,
                'config': [{
                    'subnet': SUBNET_ADDR
                }]
            }
        }
    },
}

for client_number in range(1, n_clients + 1):
    client_name = f'client{client_number}'
    BASE_YAML['services'][client_name] = {
        'container_name': client_name,
        'image': CLIENT_IMG,
        'entrypoint': CLIENT_ENTRYPOINT,
        'environment': [
            f'CLI_ID={client_number}',
            f'CLI_NOMBRE=Santiago Lionel'
            f'CLI_APELLIDO=Lorca'
            f'CLI_DOCUMENTO=30904465'
            f'CLI_NACIMIENTO=1999-03-17'
            f'CLI_NUMERO=7574'
        ],
        'networks': CLIENT_NET,
        'depends_on': CLIENT_DEPENDENCIES,
        'volumes': CLIENT_VOLUMES,
    }

with open(yaml_file_name, "wt", encoding='utf-8') as file:
    yaml.dump(BASE_YAML, file, sort_keys=False)
