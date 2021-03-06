import json
import os
import socket
import sys
import time

import ansible.module_utils.basic
from .exceptions import EmbeddedModuleSuccess, EmbeddedModuleFailure

if False:
    from .server import please_include_me

    # This is a trick to be sure server.py is embedded in the Ansiblez
    # zip archive.🥷
    please_include_me


class AnsibleTurboModule(ansible.module_utils.basic.AnsibleModule):
    embedded_in_server = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._socket = None
        self._socket_path = os.environ["HOME"] + "/.ansible/turbo_mode.socket"
        self._running = None
        self.embedded_in_server = sys.argv[0].endswith("/server.py")
        if not self.embedded_in_server:
            self.run_on_daemon()

    def start_daemon(self):
        import subprocess

        if self._running:
            return

        ansiblez_path = sys.path[0]
        env = os.environ
        env.update({"PYTHONPATH": ansiblez_path})
        p = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "ansible_collections.cloud.common.plugins.module_utils.turbo.server",
                "--fork",
                "--socket-path",
                self._socket_path,
            ],
            env=env,
            close_fds=True,
        )
        self._running = True
        # p.pid
        # p.returncode
        p.communicate()
        return

    def connect(self):
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        for attempt in range(100, -1, -1):
            try:
                self._socket.connect(self._socket_path)
                return
            except (ConnectionRefusedError, FileNotFoundError) as e:
                self.start_daemon()
                if attempt == 0:
                    raise
            time.sleep(0.01)

    def run_on_daemon(self):
        self.connect()
        result = dict(changed=False, original_message="", message="")
        ansiblez_path = sys.path[0]
        data = [
            ansiblez_path,
            ansible.module_utils.basic._ANSIBLE_ARGS.decode(),
        ]
        self._socket.send(json.dumps(data).encode())
        raw_answer = b""
        while True:
            b = self._socket.recv((1024 * 10))
            if not b:
                break
            raw_answer += b
        self._socket.close()

        result = json.loads(raw_answer.decode())
        self.exit_json(**result)

    def exit_json(self, **kwargs):
        if not self.embedded_in_server:
            super().exit_json(**kwargs)
        else:
            self.do_cleanup_files()
            raise EmbeddedModuleSuccess(**kwargs)

    def fail_json(self, **kwargs):
        if not self.embedded_in_server:
            super().fail_json(**kwargs)
        else:
            self.do_cleanup_files()
            raise EmbeddedModuleFailure(**kwargs)
