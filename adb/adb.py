#!/usr/bin/env python
# coding: utf-8

import logging
import os
import re
import shutil
import subprocess

from typing import Optional, Union, List


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

    def execute(self, command: List[str], is_async: bool = False, timeout: Optional[int] = None) -> Optional[str]:
        """
        Execute an adb command and return the output of the command as a string.

        :param command: The command to execute, formatted as a list of strings.
        :param is_async: If set to True, the adb command will run in background and the program will continue its
                         execution. If False (default), the program will wait until the adb command returns a result.
        :param timeout: How many seconds to wait for the command to finish execution before throwing an exception.
        :return: The (string) output of the command. If the method is called with the parameter is_async = True,
                 None will be returned.
        """
        if not isinstance(command, list) or any(not isinstance(command_token, str) for command_token in command):
            raise TypeError('The command to execute should be passed as a list of strings')

        if timeout is not None and (not isinstance(timeout, int) or timeout <= 0):
            raise ValueError('If a timeout is provided, it must be a positive integer')

        if is_async and timeout:
            raise RuntimeError('The timeout cannot be used when executing the program in background')

        try:
            command.insert(0, self.adb_path)
            self.logger.debug('Running command `{0}` (async={1}, timeout={2})'.format(' '.join(command),
                                                                                      is_async, timeout))

            if is_async:
                # Adb command will run in background, nothing to return.
                subprocess.Popen(command)
                return None
            else:
                output = subprocess.check_output(command, stderr=subprocess.STDOUT, timeout=timeout) \
                                   .strip().decode(errors='backslashreplace')
                self.logger.debug('Command `{0}` successfully returned: {1}'.format(' '.join(command), output))
                return output
        except subprocess.TimeoutExpired as e:
            self.logger.error('Command `{0}` timed out: {1}'.format(
                ' '.join(command), e.output.decode(errors='backslashreplace') if e.output else e))
            raise
        except subprocess.CalledProcessError as e:
            self.logger.error('Command `{0}` exited with error: {1}'.format(
                ' '.join(command), e.output.decode(errors='backslashreplace') if e.output else e))
            raise
        except Exception as e:
            self.logger.error('Generic error during `{0}` command execution: {1}'.format(' '.join(command), e))
            raise

    def get_available_devices(self) -> List[str]:
        """
        Get a list with the serials of the devices currently connected to adb.

        :return: A list of strings, each string is a device serial number.
        """
        output = self.execute(['devices'])

        devices = []
        for line in output.splitlines():
            tokens = line.strip().split()
            if len(tokens) == 2 and tokens[1] == 'device':
                # Add to the list the ip and port of the device.
                devices.append(tokens[0])
        return devices

    def shell(self, command: List[str], is_async: bool = False, timeout: Optional[int] = None) -> Optional[str]:
        # TODO: make sure to have the command as a list
        command.insert(0, 'shell')
        return self.execute(command, is_async, timeout)

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

    def push_file(self, host_path: Union[str, List[str]], device_path: str, timeout: Optional[int] = None) -> str:
        """
        Copy a file (or a list of files) from the computer to the Android device connected through adb.

        :param host_path: The path of the file on the host computer. This parameter also accepts a list of paths
                          (strings) to copy more files at the same time.
        :param device_path: The path on the Android device where the file(s) should be copied.
        :param timeout: How many seconds to wait for the file copy operation before throwing an exception.
        :return: The string with the result of the copy operation.
        """

        # Make sure the files to copy exist on the host computer.
        if isinstance(host_path, list):
            for p in host_path:
                if not os.path.exists(p):
                    raise FileNotFoundError('Cannot copy "{0}" to the Android device: no such file or directory'
                                            .format(p))

        if isinstance(host_path, str) and not os.path.exists(host_path):
            raise FileNotFoundError('Cannot copy "{0}" to the Android device: no such file or directory'
                                    .format(host_path))

        push_cmd = ['push']
        if isinstance(host_path, list):
            push_cmd.extend(host_path)
        else:
            push_cmd.append(host_path)

        push_cmd.append(device_path)

        output = self.execute(push_cmd, timeout=timeout)

        # Make sure the pull operation ended successfully.
        match = re.search(r'\d+ files? pushed\.', output.splitlines()[-1])
        if match:
            return output
        else:
            raise RuntimeError('Something went wrong during the push operation')

    def pull_file(self, device_path: Union[str, List[str]], host_path: str, timeout: Optional[int] = None) -> str:
        """
        Copy a file (or a list of files) from the Android device to the computer connected through adb.

        :param device_path: The path of the file on the Android device. This parameter also accepts a list of paths
                            (strings) to copy more files at the same time.
        :param host_path: The path on the host computer where the file(s) should be copied. If multiple files are
                          copied at the same time, this path should refer to an existing directory on the host.
        :param timeout: How many seconds to wait for the file copy operation before throwing an exception.
        :return: The string with the result of the copy operation.
        """

        # When copying multiple files at the same time, make sure the host path refers to an existing directory.
        if isinstance(device_path, list) and not os.path.isdir(host_path):
            raise NotADirectoryError('When copying multiple files, the destination host path should be an '
                                     'existing directory: "{0}" directory was not found'.format(host_path))

        # Make sure the destination directory on the host exists (adb won't create the missing directories specified
        # on the host path). For example, if test/ directory exists on host, it can be used, but test/nested/ can be
        # used only if it already exists on the host, otherwise adb won't create the nested/ directory.
        if not os.path.isdir(os.path.dirname(host_path)):
            raise NotADirectoryError('The destination host directory "{0}" was not found'
                                     .format(os.path.dirname(host_path)))

        pull_cmd = ['pull']
        if isinstance(device_path, list):
            pull_cmd.extend(device_path)
        else:
            pull_cmd.append(device_path)

        pull_cmd.append(host_path)

        output = self.execute(pull_cmd, timeout=timeout)

        # Make sure the pull operation ended successfully.
        match = re.search(r'\d+ files? pulled\.', output.splitlines()[-1])
        if match:
            return output
        else:
            raise RuntimeError('Something went wrong during the pull operation')

    def install_app(self, package_name: str, reinstall: bool = False):
        # TODO: handle errors
        install_cmd = ['install', '{0}'.format(package_name)]
        if reinstall:
            install_cmd.insert(1, '-r')
        self.execute(install_cmd)

    def uninstall_app(self, package_name: str):
        # TODO: handle errors (error message: Failure [DELETE_FAILED_INTERNAL_ERROR])
        self.execute(['uninstall', '{0}'.format(package_name)])
