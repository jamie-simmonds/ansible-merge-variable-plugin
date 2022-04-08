#!/usr/bin/env python

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.vars import isidentifier
from __main__ import display

strategies = ('overwrite', 'first', 'last', 'remove')

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        name = self._task.args.get('name', '')

        if not name:
            raise AnsibleError('name must be set')

        if not isidentifier(name):
            raise AnsibleError('name "%s" is not a valid identifier' % name)

        keys = sorted([key for key in task_vars.keys() if (key.startswith(name + '__') or key == name)])
        values = [self._templar.template(task_vars[key]) for key in keys]
        merged = None

        display.v('({}) Merging variables in this order: {}'.format(name, keys))

        if values == []:
            return {
                'changed': False,
            }
        elif isinstance(values[0], list):
            for value in values:
                if merged is None:
                    merged = value
                else:
                    merged = _merge_list(merged, value)
        elif isinstance(values[0], dict):
            for value in values:
                if merged is None:
                    merged = value
                else:
                    merged = _merge_dict(merged, value)
        else:
            raise AnsibleError("Don't know how to merge variables of type: {}".format(type(values[0])))

        return {
            'ansible_facts': {name: merged},
            'changed': False,
        }

def _cleanup(obj):
    if obj:
        if isinstance(obj, dict):
            obj.pop('__', None)

            for k, v in obj.items():
                obj[k] = _cleanup(v)
        elif isinstance(obj, list) and isinstance(obj[0], dict) and '__' in obj[0]:
            del obj[0]

    return obj

def _merge_list(stack, obj):
    strategy = 'last'

    if obj and isinstance(obj[0], dict) and '__' in obj[0]:
        strategy = obj[0]['__']
        del obj[0]

    if strategy not in strategies:
        raise AnsibleError('Unknown strategy "{}", should be one of {}'.format(strategy, strategies))

    if strategy == 'overwrite':
        return obj
    elif strategy == 'remove':
        return [item for item in stack if item not in obj]
    elif strategy == 'first':
        return obj + stack
    else:
        return stack + obj

def _merge_dict(stack, obj):
    strategy = obj.pop('__', 'last')

    if strategy not in strategies:
        raise AnsibleError('Unknown strategy "{}", should be one of {}'.format(strategy, strategies))

    if strategy == 'overwrite':
        return _cleanup(obj)
    else:
        for k, v in obj.items():
            if strategy == 'remove':
                stack.pop(k, None)
                continue

            if k in stack:
                if strategy == 'first':
                    stack_k = stack[k]
                    stack[k] = _cleanup(v)
                    v = stack_k

                if type(stack[k]) != type(v):
                    stack[k] = _cleanup(v)
                elif isinstance(v, dict):
                    stack[k] = _merge_dict(stack[k], v)
                elif isinstance(v, list):
                    stack[k] = _merge_list(stack[k], v)
                else:
                    stack[k] = v
            else:
                stack[k] = _cleanup(v)

        return stack
