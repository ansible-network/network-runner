========
Bindings
========

Bindings allow for Ansible roles to be transformed into Python programmable
objects.  When used, bindings all for Ansible roles to be embedded into other
applications by given you a programmatic interface into building and consuming
playbooks.

In order to get started with bindings, its import to understand the structure
of the `bindings.yml` file.  

Actions
-------

Actions provide the method names to be dynmically created along with the
associated method signature.  For instance, lets assume we are building a
binding for a role that configures VLANS and we have two task lists in our
role: `tasks/create_vlan.yml` and `tasks/delete_vlan.yml`.   Further let's
assume the `create_vlan.yml` task list requires a `vlan_id` and an optional
`vlan_name` in order to work properly and the `delete_vlan.yml` task 
requires only a `vlan_id` argument.

We can expose those tasks in the `actions` section of `bindings.yml` as
follows:

    .. code-block:: console

    ---
    actions:
      create_vlan:
        args:
          vlan_id: { type: int, required: True }
          vlan_name: { type: str }
      delete_vlan:
        args:
          vlan_id: { type: int, required: True}

When the above bindings file is loaded, it will create an instance of a Python
object with two configured methods: `create_vlan` and `delete_vlan`. 


Models
------

Models provide the opportunity to build more complex arguments for method calls
instead of just using scalar arguments.  Let's assume that instead of creating
two arguments for the `create_vlan` method we instead want to pass a single
argument.  To do this, we can create a model.

    .. code-block:: console

    ---
    models:
      vlan:
        vlan_id: { type: int, required: True }
        vlan_name: { type: str }

    actions:
      create_vlan:
        args:
          vlan: { type: vlan }

In the above example, the `create_vlan` method now only accepts a single
keyword argument `vlan` which is comprised of two properties: `vlan_id` and
`vlan_name`.


Validators
----------

Validators allow for data validation to be applied to arguments to make sure
they conform to defined constraints.  Once again building on the VLAN example,
lets add a validator that will validate the value for `vlan_id` is within the
allowable range of 1 to 4094.

    .. cod-block:: console

    ---
    validators:
      vlan_id: { type: range, minval: 1, maxval: 4094 }

    models:
      vlan:
        vlan_id: { type: int, required: True, validators: [vlan_id] }
        vlan_name: { type: str }

    actions:
      create_vlan:
        args:
          vlan: { type: vlan }

      delete_vlan:
        args:
          vlan_id: { type: int, required: True, validators: [vlan_id] }

When either the `create_vlan` or the `delete_vlan` method is called from Python
the value of `vlan_id` will be checked to make sure it falls within the range
of ` to 4094.

Now that we have an idea about how to create a bindings file, lets shift focus
to looking at how to use the bindings from Python to programmatically consume
the role.

#. In a python environment import the `load` method 

    .. code-block:: console

    from network_runner.bindings.role import load

#. Next we need to load the role which will build the dynamic object based on
   the bindings file.

    .. code-block:: console

    role = load('network-runner')

#. Call the desired methods with appropriate keyword arguments

   .. code-block:: console

    vlan = role.new(vlan_id=1, vlan_name='default')
    create_task = role.create_vlan(vlan=vlan)

    delete_task = role.delete_vlan(vlan_id=10)
