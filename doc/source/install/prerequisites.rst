Prerequisites
-------------

To successfully install and configure the Networking-Ansible library, you
will need Switch credentials that allow configuration changes to the ports
and VLANS planned to be managed.

For security purposes it is important that you do not provide administrator
access to the switch for network-runner. A user should be created
and granted access for the permissions needed for network-runner.

Network-Runner will need permissions to execute the actions you plan to use.
This could include creating and deleting VLANS, configuring ports in access mode
and trunk mode and deleting port configurations.

Collecting this information and ensuring the proper permissions will successful
installation and operation.
