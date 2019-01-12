#!/usr/bin/env python
# coding: utf-8

import logging
import os
import re
import shutil
import subprocess

from typing import List


class ADB(object):

    def __init__(self, debug: bool = False):
        self.logger = logging.getLogger('{0}.{1}'.format(__name__, self.__class__.__name__))

        if debug:
            self.logger.setLevel(logging.DEBUG)

        # If adb executable is not added to PATH variable, it can be specified by using the
        # ADB_PATH environment variable.
        if 'ADB_PATH' in os.environ:
            self.adb_path: str = os.environ['ADB_PATH']
        else:
            self.adb_path: str = 'adb'

        if not self.adb_is_available():
            raise FileNotFoundError('Adb executable is not available! Make sure to have adb (Android Debug Bridge) '
                                    'installed and added to the PATH variable, or specify the adb path by using the '
                                    'ADB_PATH environment variable.')

    def adb_is_available(self) -> bool:
        """
        Check if adb executable is available.

        :return: True if abd executable is available for usage, False otherwise.
        """
        return shutil.which(self.adb_path) is not None

    def get_available_devices(self) -> List[str]:
        """
        Get a list with the serials of the devices currently connected to adb.

        :return: A list of strings, each string is a device serial number.
        """
        output = subprocess.check_output([self.adb_path, 'devices'], stderr=subprocess.STDOUT).strip().decode()

        devices = []
        for line in output.splitlines():
            tokens = line.strip().split()
            if len(tokens) == 2 and tokens[1] == 'device':
                # Add to the list the ip and port of the device.
                devices.append(tokens[0])
        return devices

    def execute(self, command: list, is_async: bool = False):
        # TODO: make sure to have the command as a list
        command.insert(0, self.adb_path)

        self.logger.debug('Running command \'{0}\' (async={1})'.format(' '.join(command), is_async))

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
