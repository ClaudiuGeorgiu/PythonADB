#!/usr/bin/env python
# coding: utf-8

import logging
import re
import subprocess


logger = logging.getLogger(__name__)


class ADB(object):

    def __init__(self, debug: bool = False):
        if debug:
            logger.setLevel(logging.DEBUG)

        # TODO: init constructor

    def execute(self, command: list, is_async: bool = False):
        # TODO: make sure to have the command as a list
        command.insert(0, 'adb')

        logger.debug('Running command \'{0}\' (async={1})'.format(' '.join(command), is_async))

        # TODO: create another method for the async version?
        if is_async:
            subprocess.Popen(command)
        else:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT).strip()
            return output.decode()

    def shell(self, command: list, is_async: bool = False):
        # TODO: make sure to have the command as a list
        command.insert(0, 'shell')
        return self.execute(command, is_async)

    def get_version(self) -> str:
        # TODO: handle errors
        result = self.execute(['version'])
        match = re.search(r'version\s(.+)', result)
        if match:
            return match.group(1)
        else:
            return None

    def reconnect(self, host: str = None):
        # TODO: handle errors
        if host:
            start_cmd = ['connect', host]
        else:
            start_cmd = ['start-server']
        self.execute(['kill-server'])
        self.execute(start_cmd)

    def wait_for_device(self):
        # TODO: handle errors
        self.execute(['wait-for-device'])

    def remount(self):
        # TODO: handle errors
        self.execute(['remount'])

    def reboot(self):
        # TODO: handle errors
        self.execute(['reboot'])

    def pull_file(self, device_path: str, host_path: str = None):
        # TODO: handle errors
        pull_cmd = ['pull', '{0}'.format(device_path)]
        if host_path:
            pull_cmd.append('{0}'.format(host_path))
        self.execute(pull_cmd)

    def push_file(self, host_path: str, device_path: str):
        # TODO: handle errors
        self.execute(['push', '{0}'.format(host_path), '{0}'.format(device_path)])

    def install_app(self, package_name: str, reinstall: bool = False):
        # TODO: handle errors
        install_cmd = ['install', '{0}'.format(package_name)]
        if reinstall:
            install_cmd.insert(1, '-r')
        self.execute(install_cmd)

    def uninstall_app(self, package_name: str):
        # TODO: handle errors (error message: Failure [DELETE_FAILED_INTERNAL_ERROR])
        self.execute(['uninstall', '{0}'.format(package_name)])


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s> [%(levelname)s][%(funcName)s()] %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')

    # Some random tests.
    adb = ADB(debug=True)
    adb.reconnect()
    adb.wait_for_device()
    adb.remount()
    adb.get_version()
