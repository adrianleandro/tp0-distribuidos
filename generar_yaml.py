"""
This module generates a YAML configuration file
that includes a server and a specified number of clients.
"""

from sys import argv, stderr
import yaml

try:
    yaml_file_name = argv[1]
    n_clients = int(argv[2])
    if n_clients < 1:
        raise ValueError('number of clients must be an integer')
except ValueError as e:
    print(f'Error: {e}', file=stderr)
    exit(-1)
except IndexError:
    print(f'Usage: ./{argv[0]} [dest YAML file] [number of clients]', file=stderr)
    exit(-1)

PROJECT_NAME = 'tp0'
DRIVER_TYPE = 'default'
SUBNET_ADDR = '172.25.125.0/24'

NETWORK_TEST_NAME = 'testing_net'

SERVER_NAME = 'server'
SERVER_IMG = 'server:latest'
SERVER_ENTRYPOINT = 'python3/main.py'
SERVER_NET = [
    NETWORK_TEST_NAME
]
SERVER_ENV = [
    'PYTHONUNBUFFERED=1',
    'LOGGING_LEVEL=DEBUG',
]

CLIENT_ENTRYPOINT = '/client'
CLIENT_IMG = 'client:latest'
CLIENT_NET = [
    NETWORK_TEST_NAME,
]
CLIENT_DEPENDENCIES = [
    'server',
]
CLIENT_ENV = [
    'CLI_ID=1',
    'CLI_LOG_LEVEL=DEBUG',
]

BASE_YAML = {
    'name': PROJECT_NAME,
    'services': {
        'server': {
            'container_name': SERVER_NAME,
            'image': SERVER_IMG,
            'entrypoint': SERVER_ENTRYPOINT,
            'environment': SERVER_ENV,
            'networks': SERVER_NET,
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
        'environment': CLIENT_ENV,
        'networks': CLIENT_NET,
        'depends_on': CLIENT_DEPENDENCIES,
    }

with open(yaml_file_name, "wt", encoding='utf-8') as file:
    yaml.dump(BASE_YAML, file, sort_keys=False)
