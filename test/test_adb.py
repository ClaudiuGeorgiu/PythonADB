#!/usr/bin/env python
# coding: utf-8

import pytest

from ..adb.adb import ADB


@pytest.fixture(scope='session')
def adb_instance() -> ADB:
    return ADB()


class TestAdbAvailability(object):

    def test_adb_is_available(self, adb_instance):
        assert adb_instance.adb_is_available() is True

    def test_adb_not_available(self, monkeypatch):
        monkeypatch.setenv('ADB_PATH', 'fake adb path')
        with pytest.raises(FileNotFoundError):
            ADB()


class TestAdbVersion(object):

    def test_adb_version(self, adb_instance):
        adb_version = adb_instance.get_version()
        assert isinstance(adb_version, str) and adb_version != ''
