"""
This module generates a YAML configuration file
that includes a server and a specified number of clients.
"""

from sys import argv
import yaml

PROJECT_NAME = 'tp0'
DRIVER_TYPE = 'default'
SUBNET_ADDR = '172.25.125.0/24'

SERVER_NAME = 'server'
SERVER_IMG = 'server:latest'
SERVER_ENTRYPOINT = 'python3/main.py'
SERVER_ENV = [
    'PYTHONUNBUFFERED=1',
    'LOGGING_LEVEL=DEBUG',
]

BASE_YAML = {
    'name': PROJECT_NAME,
    'networks': {
        'testing_net': {
            'ipam': {
                'driver': DRIVER_TYPE,
                'config': [{
                    'subnet': SUBNET_ADDR
                }]
            }
        }
    },
    'services': {
        'server': {
            'container_name': SERVER_NAME,
            'image': SERVER_IMG,
            'entrypoint': SERVER_ENTRYPOINT,
            'environment': SERVER_ENV,
            'networks': [
                'testing_net'
            ],
        }
    }
}

with open(argv[1], "wt", encoding='utf-8') as file:
    yaml.dump(BASE_YAML, file)
