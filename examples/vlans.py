import os
import json

from network_runner import api
from network_runner.bindings.role import load
from network_runner.models.inventory import Host
from network_runner.models.inventory import Inventory
from network_runner.models.playbook import Playbook


os.environ['ANSIBLE_ROLES_PATH'] = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, 'etc/ansible/roles')
)


role = load('network-runner')


veos01 = Host(
    name='veos01',
    ansible_host='192.168.86.64',
    ansible_user='admin',
    ansible_password='admin',
    ansible_network_os='eos',
    ansible_connection='network_cli',
    ansible_become=True,
    ansible_become_method='enable'
)


inventory = Inventory()
playbook = Playbook()

inventory.hosts['veos01'] = veos01

play = playbook.new()


def create_vlan(vlan_id, vlan_name):
    play.tasks.append(
        role.create_vlan(vlan_id=vlan_id, vlan_name=vlan_name)
    )


def delete_vlan(vlan_id):
    play.tasks.append(
        role.delete_vlan(vlan_id=vlan_id)
    )


def run(gather_facts=True, quiet=False):
    play.gather_facts = gather_facts
    api.run(playbook, inventory, quiet=quiet)


def show_playbook():
    print(json.dumps(playbook.serialize(), indent=4))


def show_inventory():
    print(json.dumps(inventory.serialize(), indent=4))
