import argparse
import json

from network_runner import api
from network_runner.resources.inventory import Inventory

TRUNK_SUPPORT = ('cumulus', 'eos', 'junos', 'openvswitch')
PORTS = {
    'cumulus': 'swp1',
    'eos': 'Ethernet1',
    'junos': 'xe-0/0/1',
    'openvswitch': 'testport',
    }

APPLIANCE = 'appliance'
OPENVSWITCH = 'openvswitch'
VLAN = 37
T_VLANS = [3, 7, 73]


def get_parser_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hosts', help='hosts file',
                        default='/etc/ansible/hosts')
    return parser.parse_args()


def get_inv_yaml(args):
    f = open(args.hosts)

    # ## Parses Ansible hosts file format
    # https://ansible-tips-and-tricks.readthedocs.io/en/latest/ansible/inventory
    # lines = f.readlines()
    # hosts = {}
    # for l in lines:
    #     print(l)
    #     line = l.split(' ')
    #     if l[0] != '#' and ' ' in l:
    #         hosts[line[0]] = {
    #             k: val for (k, val) in [x.split('=') for x in line[1:]]
    #         }
    # return {'all': {'hosts': hosts}}

    json_hosts = f.read()
    hosts = json.loads(json_hosts)
    return hosts


def run_tests(inventory, hostname, port, trunk=False):
    # TODO(radez) Use a testing framework to verify

    net_runr = api.NetworkRunner(inventory)
    # ## Create a vlan
    net_runr.create_vlan(hostname, VLAN)

    # ## Configure an access port
    net_runr.conf_access_port(hostname, port, VLAN)
    # ## configure a trunk port
    if trunk:
        net_runr.conf_trunk_port(hostname, port, VLAN, T_VLANS)

    # ## delete a port
    net_runr.delete_port(hostname, port)
    # ## delete a vlan
    net_runr.delete_vlan(hostname, VLAN)


def main():
    # collect information for the run.
    args = get_parser_args()
    inv_yaml = get_inv_yaml(args)
    hosts = inv_yaml['all']['hosts']
    hostname = inv_yaml['all']['children'][OPENVSWITCH]['hosts'].popitem()[0] \
        if OPENVSWITCH in inv_yaml['all']['children'] else \
        inv_yaml['all']['children'][APPLIANCE]['hosts'].popitem()[0]
    net_os = hosts[hostname]['ansible_network_os']
    port = PORTS[net_os]

    # build the inventory object
    inventory = Inventory()
    inventory.deserialize(inv_yaml)

    # execute the tests
    run_tests(inventory, hostname, port, net_os in TRUNK_SUPPORT)


if __name__ == "__main__":
    main()
