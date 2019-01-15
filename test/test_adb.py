#!/usr/bin/env python
# coding: utf-8

import os
import pathlib

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
