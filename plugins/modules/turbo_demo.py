#!/usr/bin/python

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: turbo_demo

short_description: A demo module for ansible_module.turbo

version_added: "1.0.0"

description:
    - "This module is an example of an ansible_module.turbo integration"

author:
    - Gonéri Le Bouder (@goneri)
"""

EXAMPLES = """
- name: Run the module
  turbo_demo:
"""

from ansible_collections.cloud.common.plugins.module_utils.turbo.module import (
    AnsibleTurboModule as AnsibleModule,
)


def counter():
    counter.i += 1
    return counter.i


counter.i = 0


def get_message():
    import os

    return f"This is me running with PID: {os.getpid()}, called {counter()} time(s)"


def run_module():
    result = dict(changed=False, message=get_message())

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec={}, supports_check_mode=True)

    if module.check_mode:
        module.exit_json(**result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
