================
Provider Support
================
Network-Runner contains platform specific functionality in an
Ansible role that enables specific hardware devices per provider switch added
to this role. The network-runner role is stored in etc/ansible/roles directory.
A platform is refered to as a provider in the network-runner context.

Adding a provider
~~~~~~~~~~~~~~~~~
To add a provider to networki-runners's capabilities the provider must be
added to the Ansible role. To add the provider to the Ansible
role a new directory using the Ansible Networking module name
[`1`_] must be added. That directory will contains files that will define
the Ansible tasks nessessary to perform the respective configuration action.

Inside the directory for the provider, a file for default values, plus a file
for each supported action is required. The currently required files for
basic support are listed below. Each file other than the defaults.yaml file
must be added with atleast a noop task in each.

* defaults.yaml

  Defines default values for VLAN name and ID. For example some
  switch vendors use the name "default" and VLAN ID 1 as a default VLAN
  to assign switchports to. Open vSwitch expects no VLAN ID and VLAN name
  in the case that port is not assigned to a specific VLAN.

* create_vlan.yaml

  Defines the Ansible tasks to create a VLAN on a switch.

* delete_vlan.yaml

  Defines the Ansible tasks to delete a VLAN on a switch.

* update_access_port.yaml

  Defines the Ansible tasks to assign a VLAN to a switchport in access mode.

* conf_trunk_port.yaml

  Defines the Ansible tasks to configure a switchport in trunk mode.

* delete_port.yaml

  Defines the Ansible tasks to remove configuration from a switchport.

[1] https://docs.ansible.com/ansible/2.6/modules/list_of_network_modules.html

.. _1: https://docs.ansible.com/ansible/2.6/modules/list_of_network_modules.html
