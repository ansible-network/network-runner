==========
User guide
==========

Network-Runner can be called directly via python API. This section will
show an example of end users could import the network-runner API and
execute switch level network configuration.

#. In a python environment import the network-runner api module.

    .. code-block:: console

      from network_runner import api

#. Create a Host object and create an Inventory object adding the host object
   to the inventory object. Then instantiate the NetworkRunner class. 

    .. code-block:: console

      from network_runner.resources.inventory import Inventory
      from network_runner.resources.inventory.hosts import Host

      host = Host(name='testhost',
                  ansible_host='192.168.121.37',
                  ansible_user='root',
                  ansible_ssh_pass='password',
                  ansible_network_os='junos')

      inventory = Inventory()
      inventory.hosts.add(h)

      net_runr = api.NetworkRunner(inventory)

#. Call functions that configure the switch.

    .. code-block:: console

      hostname = 'testhost'
      vlan = 37
      port = 'xe-0/0/7'
      t_vlans = [3,7,73]
      
      # Create a vlan
      net_runr.create_vlan(hostname, vlan)
      # delete a vlan
      net_runr.delete_vlan(hostname, vlan)

      # Configure an access port
      net_runr.conf_access_port(hostname, port, vlan)
      # configure a trunk port
      net_runr.conf_trunk_port(hostname, port, vlan, t_vlans)
      # delete a port
      net_runr.delete_port(hostname, port)
