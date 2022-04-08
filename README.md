# Ansible: Merge variable plugin

## Use case

This plugin can be used to define a variable multiple times, either via host_vars, group_vars, inventory variables or other, and at runtime combine the variable values to have a single variable that can be used within a role. This is similar to how [Salt](https://docs.saltproject.io) allows its pillar data to be defined.

This works with both arrays, lists, and dictionaries in YAML

## Configuration
Ansible should be configured to use a plugin directory that holds a copy of merge_variables.py

This can be done via ansible.cfg or using environment variables

[Ansible documentation](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#default-action-plugin-path)

## Using the plugin

The plugin needs to be called as a task, provided with the variable name that needs to be merged:

```
- merge_variables:
    name: variable_name
```

The plugin will then look for any variable that matches either `variable_name` or starts with `variable_name__` and will then start the merge process

_Variables cannot be defined multiple times with the same name, Ansible will merge these before the plugin can access them_

Example:

group_vars/all.yaml

```
variable_name:
  - a
  - b
```

host_vars/host.yaml

```
variable_name__host:
  - c
  - d
```

These will be merged and able to be used as `variable_name` within the role

```
variable_name:
  - a
  - b
  - c
  - d
```

Merge stratigies are available and work the same way as Salt

- overwrite
- first
- last
- remove

These can be used by defining a __ key at the start of the data.

Example:

group_vars/all.yaml

```
variable_name:
  - a
  - b
```

host_vars/host.yaml

```
variable_name__host:
  __: overwrite
  - c
  - d
```
