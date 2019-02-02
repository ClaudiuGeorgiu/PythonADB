#!/usr/bin/env python
# coding: utf-8

import os
import pathlib
import subprocess

import pytest

from ..adb.adb import ADB


@pytest.fixture(scope='session')
def adb_instance() -> ADB:
    return ADB(debug=True)


class TestAdbAvailability(object):

    def test_adb_is_available(self, adb_instance: ADB):
        assert adb_instance.adb_is_available()

    def test_adb_not_available(self, monkeypatch):
        monkeypatch.setenv('ADB_PATH', 'fake adb path')
        with pytest.raises(FileNotFoundError):
            ADB()


class TestAdbVersion(object):

    def test_adb_version(self, adb_instance: ADB):
        adb_version = adb_instance.get_version()
        assert isinstance(adb_version, str)
        assert adb_version is not ''


class TestAdbDevice(object):

    def test_adb_device_connected(self, adb_instance: ADB):
        connected_devices = adb_instance.get_available_devices()
        assert isinstance(connected_devices, list)
        assert len(connected_devices) > 0
        assert isinstance(connected_devices[0], str)
        assert connected_devices[0] is not ''


class TestCommandTimeout(object):

    def test_adb_shell_timeout(self, adb_instance: ADB):
        with pytest.raises(subprocess.TimeoutExpired):
            adb_instance.shell(['sleep', '300'], timeout=3)

    def test_adb_pull_timeout(self, adb_instance: ADB, tmp_path: pathlib.Path):
        with pytest.raises(subprocess.TimeoutExpired):
            adb_instance.pull_file('/system', os.fspath(tmp_path), timeout=3)


class TestFileInteraction(object):

    def test_adb_pull_single_valid_file(self, adb_instance: ADB, tmp_path: pathlib.Path):
        dest_file = tmp_path / 'default.prop'
        adb_instance.pull_file('/default.prop', os.fspath(dest_file))
        assert os.path.isfile(dest_file)
        assert os.path.getsize(dest_file) > 0

    def test_adb_pull_multiple_valid_files(self, adb_instance: ADB, tmp_path: pathlib.Path):
        adb_instance.pull_file(['/default.prop', '/system/build.prop'], os.fspath(tmp_path))
        dest_file_1 = tmp_path / 'default.prop'
        dest_file_2 = tmp_path / 'build.prop'
        assert os.path.isfile(dest_file_1)
        assert os.path.isfile(dest_file_2)
        assert os.path.getsize(dest_file_1) > 0
        assert os.path.getsize(dest_file_2) > 0

    def test_adb_pull_single_file_invalid_destination(self, adb_instance: ADB, tmp_path: pathlib.Path):
        dest_file = tmp_path / 'invalid' / 'directory' / 'default.prop'
        with pytest.raises(NotADirectoryError):
            adb_instance.pull_file('/default.prop', os.fspath(dest_file))

    def test_adb_pull_multiple_files_invalid_destination(self, adb_instance: ADB, tmp_path: pathlib.Path):
        dest_file = tmp_path / 'invalid'
        with pytest.raises(NotADirectoryError):
            adb_instance.pull_file(['/default.prop', '/system/build.prop'], os.fspath(dest_file))

    def test_adb_pull_invalid_file(self, adb_instance: ADB, tmp_path: pathlib.Path):
        with pytest.raises(subprocess.CalledProcessError):
            adb_instance.pull_file('/invalid.file', os.fspath(tmp_path))

    def test_adb_pull_incomplete(self, adb_instance: ADB, tmp_path: pathlib.Path, monkeypatch):
        monkeypatch.setattr(ADB, 'execute', lambda _, command, timeout: 'incomplete transfer')
        with pytest.raises(RuntimeError):
            adb_instance.pull_file('/default.prop', os.fspath(tmp_path))

    def test_adb_push_single_valid_file(self, adb_instance: ADB, tmp_path: pathlib.Path):
        source_file_path = tmp_path / 'testfile.txt'
        # noinspection PyTypeChecker
        with open(source_file_path, 'w') as source_file:
            source_file.write('This is a test file\n')
        result = adb_instance.push_file(os.fspath(source_file_path), '/data/local/tmp/')
        assert 'testfile.txt: 1 file pushed.' in result
        assert '{0} bytes in '.format(os.path.getsize(source_file_path)) in result

    def test_adb_push_multiple_valid_files(self, adb_instance: ADB, tmp_path: pathlib.Path):
        source_file_path_1 = tmp_path / 'testfile.txt'
        source_file_path_2 = tmp_path / 'other.txt'
        # noinspection PyTypeChecker
        with open(source_file_path_1, 'w') as source_file_1, open(source_file_path_2, 'w') as source_file_2:
            source_file_1.write('This is a test file\n')
            source_file_2.write('This is another file\n')
        result = adb_instance.push_file([os.fspath(source_file_path_1), os.fspath(source_file_path_2)],
                                        '/data/local/tmp/')
        assert '2 files pushed.' in result
        assert '{0} bytes in '.format(os.path.getsize(source_file_path_1) +
                                      os.path.getsize(source_file_path_2)) in result

    def test_adb_push_invalid_file(self, adb_instance: ADB):
        with pytest.raises(FileNotFoundError):
            adb_instance.push_file('', '/data/local/tmp/')

    def test_adb_push_invalid_files(self, adb_instance: ADB):
        with pytest.raises(FileNotFoundError):
            adb_instance.push_file(['', ''], '/data/local/tmp/')

    def test_adb_push_invalid_destination(self, adb_instance: ADB, tmp_path: pathlib.Path):
        source_file_path = tmp_path / 'testfile.txt'
        # noinspection PyTypeChecker
        with open(source_file_path, 'w') as source_file:
            source_file.write('This is a test file\n')
        with pytest.raises(subprocess.CalledProcessError):
            adb_instance.push_file(os.fspath(source_file_path), '/invalid/directory/')

    def test_adb_push_incomplete(self, adb_instance: ADB, tmp_path: pathlib.Path, monkeypatch):
        monkeypatch.setattr(ADB, 'execute', lambda _, command, timeout: 'incomplete transfer')
        source_file_path = tmp_path / 'testfile.txt'
        # noinspection PyTypeChecker
        with open(source_file_path, 'w') as source_file:
            source_file.write('This is a test file\n')
        with pytest.raises(RuntimeError):
            adb_instance.push_file(os.fspath(source_file_path), '/data/local/tmp/')
