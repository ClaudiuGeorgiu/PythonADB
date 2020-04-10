#!/usr/bin/env python3

import os
import pathlib
import subprocess

import pytest

from ..adb.adb import ADB


@pytest.fixture(scope="session")
def adb_instance() -> ADB:
    return ADB(debug=True)


@pytest.fixture(scope="session")
def valid_apk_path() -> pathlib.Path:
    return pathlib.Path(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "test_resources", "test.apk"
        )
    )


class TestAdbAvailability(object):
    def test_adb_is_available(self, adb_instance: ADB):
        assert adb_instance.is_available()

    def test_adb_not_available(self, monkeypatch):
        monkeypatch.setenv("ADB_PATH", "fake adb path")
        with pytest.raises(FileNotFoundError):
            ADB()


class TestAdbVersion(object):
    def test_adb_version_success(self, adb_instance: ADB):
        adb_version = adb_instance.get_version()
        assert isinstance(adb_version, str)
        assert adb_version is not ""

    def test_adb_version_failure(self, adb_instance: ADB, monkeypatch):
        monkeypatch.setattr(ADB, "execute", lambda _, command, timeout: "no version")
        with pytest.raises(RuntimeError):
            adb_instance.get_version()


class TestAdbDevice(object):
    def test_adb_device_connected(self, adb_instance: ADB):
        adb_instance.kill_server(timeout=30)
        adb_instance.connect(timeout=30)
        connected_devices = adb_instance.get_available_devices(timeout=30)
        adb_instance.target_device = connected_devices[0]
        adb_instance.wait_for_device(timeout=30)
        assert isinstance(connected_devices, list)
        assert len(connected_devices) > 0
        assert isinstance(connected_devices[0], str)
        assert connected_devices[0] is not ""

    def test_adb_connection_error(self, adb_instance: ADB):
        with pytest.raises(RuntimeError):
            adb_instance.connect("unknown", timeout=30)

    def test_adb_remount_error(self, adb_instance: ADB):
        with pytest.raises(RuntimeError):
            # This should fail because "adb root" was not executed.
            adb_instance.remount(timeout=30)

    @pytest.mark.last
    def test_adb_reboot(self, adb_instance: ADB):
        result = adb_instance.reboot(timeout=300)
        assert result == ""


class TestCommandExecution(object):
    def test_adb_execute_command(self, adb_instance: ADB):
        result = adb_instance.shell(["sleep", "1"], is_async=False)
        assert result == ""

    def test_adb_execute_async_command(self, adb_instance: ADB):
        result = adb_instance.shell(["sleep", "1"], is_async=True)
        assert result is None

    def test_adb_execute_invalid_command(self, adb_instance: ADB):
        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            adb_instance.execute("not a list of strings")

    def test_adb_shell_invalid_command(self, adb_instance: ADB):
        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            adb_instance.shell("not a list of strings")

    def test_adb_execute_invalid_timeout(self, adb_instance: ADB):
        with pytest.raises(ValueError):
            adb_instance.shell(["sleep", "1"], timeout=0)

    def test_adb_execute_async_timeout_conflict(self, adb_instance: ADB):
        with pytest.raises(RuntimeError):
            adb_instance.shell(["sleep", "1"], is_async=True, timeout=3)

    def test_adb_execute_generic_exception(self, adb_instance: ADB, monkeypatch):
        monkeypatch.setattr(adb_instance.logger, "debug", lambda _: 1 / 0)
        with pytest.raises(Exception):
            adb_instance.shell(["sleep", "1"])


class TestCommandTimeout(object):
    def test_adb_shell_timeout(self, adb_instance: ADB):
        with pytest.raises(subprocess.TimeoutExpired):
            adb_instance.shell(["sleep", "300"], timeout=3)

    def test_adb_pull_timeout(self, adb_instance: ADB, tmp_path: pathlib.Path):
        with pytest.raises(subprocess.TimeoutExpired):
            adb_instance.pull_file("/system/lib", os.fspath(tmp_path), timeout=1)


class TestFileInteraction(object):
    def test_adb_pull_single_valid_file(
        self, adb_instance: ADB, tmp_path: pathlib.Path
    ):
        dest_file = tmp_path / "hosts"
        adb_instance.pull_file("/etc/hosts", os.fspath(dest_file))
        assert os.path.isfile(dest_file)
        assert os.path.getsize(dest_file) > 0

    def test_adb_pull_multiple_valid_files(
        self, adb_instance: ADB, tmp_path: pathlib.Path
    ):
        adb_instance.pull_file(["/etc/hosts", "/etc/fonts.xml"], os.fspath(tmp_path))
        dest_file_1 = tmp_path / "hosts"
        dest_file_2 = tmp_path / "fonts.xml"
        assert os.path.isfile(dest_file_1)
        assert os.path.isfile(dest_file_2)
        assert os.path.getsize(dest_file_1) > 0
        assert os.path.getsize(dest_file_2) > 0

    def test_adb_pull_single_file_invalid_destination(
        self, adb_instance: ADB, tmp_path: pathlib.Path
    ):
        dest_file = tmp_path / "invalid" / "directory" / "hosts"
        with pytest.raises(NotADirectoryError):
            adb_instance.pull_file("/etc/hosts", os.fspath(dest_file))

    def test_adb_pull_multiple_files_invalid_destination(
        self, adb_instance: ADB, tmp_path: pathlib.Path
    ):
        dest_file = tmp_path / "invalid"
        with pytest.raises(NotADirectoryError):
            adb_instance.pull_file(
                ["/etc/hosts", "/etc/fonts.xml"], os.fspath(dest_file)
            )

    def test_adb_pull_invalid_file(self, adb_instance: ADB, tmp_path: pathlib.Path):
        with pytest.raises(subprocess.CalledProcessError):
            adb_instance.pull_file("/invalid.file", os.fspath(tmp_path))

    def test_adb_pull_incomplete(
        self, adb_instance: ADB, tmp_path: pathlib.Path, monkeypatch
    ):
        monkeypatch.setattr(
            ADB, "execute", lambda _, command, timeout: "incomplete transfer"
        )
        with pytest.raises(RuntimeError):
            adb_instance.pull_file("/etc/hosts", os.fspath(tmp_path))

    def test_adb_push_single_valid_file(
        self, adb_instance: ADB, tmp_path: pathlib.Path
    ):
        source_file_path = tmp_path / "testfile.txt"
        # noinspection PyTypeChecker
        with open(source_file_path, "w") as source_file:
            source_file.write("This is a test file\n")
        result = adb_instance.push_file(os.fspath(source_file_path), "/data/local/tmp/")
        assert "testfile.txt: 1 file pushed" in result
        assert "{0} bytes in ".format(os.path.getsize(source_file_path)) in result

    def test_adb_push_multiple_valid_files(
        self, adb_instance: ADB, tmp_path: pathlib.Path
    ):
        source_file_path_1 = tmp_path / "testfile.txt"
        source_file_path_2 = tmp_path / "other.txt"
        # noinspection PyTypeChecker
        with open(source_file_path_1, "w") as source_file_1, open(
            source_file_path_2, "w"
        ) as source_file_2:
            source_file_1.write("This is a test file\n")
            source_file_2.write("This is another file\n")
        result = adb_instance.push_file(
            [os.fspath(source_file_path_1), os.fspath(source_file_path_2)],
            "/data/local/tmp/",
        )
        assert "2 files pushed" in result
        assert (
            "{0} bytes in ".format(
                os.path.getsize(source_file_path_1)
                + os.path.getsize(source_file_path_2)
            )
            in result
        )

    def test_adb_push_invalid_file(self, adb_instance: ADB):
        with pytest.raises(FileNotFoundError):
            adb_instance.push_file("", "/data/local/tmp/")

    def test_adb_push_invalid_files(self, adb_instance: ADB):
        with pytest.raises(FileNotFoundError):
            adb_instance.push_file(["", ""], "/data/local/tmp/")

    def test_adb_push_invalid_destination(
        self, adb_instance: ADB, tmp_path: pathlib.Path
    ):
        source_file_path = tmp_path / "testfile.txt"
        # noinspection PyTypeChecker
        with open(source_file_path, "w") as source_file:
            source_file.write("This is a test file\n")
        with pytest.raises(subprocess.CalledProcessError):
            adb_instance.push_file(os.fspath(source_file_path), "/invalid/directory/")

    def test_adb_push_incomplete(
        self, adb_instance: ADB, tmp_path: pathlib.Path, monkeypatch
    ):
        monkeypatch.setattr(
            ADB, "execute", lambda _, command, timeout: "incomplete transfer"
        )
        source_file_path = tmp_path / "testfile.txt"
        # noinspection PyTypeChecker
        with open(source_file_path, "w") as source_file:
            source_file.write("This is a test file\n")
        with pytest.raises(RuntimeError):
            adb_instance.push_file(os.fspath(source_file_path), "/data/local/tmp/")


class TestAppInstallation(object):
    @classmethod
    def teardown_class(cls):
        try:
            # Make sure to uninstall the application used for testing.
            ADB().uninstall_app("com.test.pythonadb", timeout=300)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, RuntimeError):
            pass

    def test_adb_install_valid_apk(
        self, adb_instance: ADB, valid_apk_path: pathlib.Path
    ):
        result = adb_instance.install_app(
            os.fspath(valid_apk_path),
            replace_existing=True,
            grant_permissions=True,
            timeout=300,
        )
        assert "Success" in result

    def test_adb_runtime_install_error(
        self, adb_instance: ADB, tmp_path: pathlib.Path, monkeypatch
    ):
        monkeypatch.setattr(
            ADB, "execute", lambda _, command, timeout: "Failure [ERROR]"
        )
        invalid_apk_path = tmp_path / "invalid.apk"
        # noinspection PyTypeChecker
        with open(invalid_apk_path, "w") as source_file:
            source_file.write("This is not an apk file\n")
        with pytest.raises(RuntimeError):
            adb_instance.install_app(os.fspath(invalid_apk_path), timeout=300)

    def test_adb_install_invalid_apk(self, adb_instance: ADB, tmp_path: pathlib.Path):
        invalid_apk_path = tmp_path / "invalid.apk"
        # noinspection PyTypeChecker
        with open(invalid_apk_path, "w") as source_file:
            source_file.write("This is not an apk file\n")
        with pytest.raises((subprocess.CalledProcessError, RuntimeError)):
            adb_instance.install_app(
                os.fspath(invalid_apk_path), replace_existing=True, timeout=300
            )

    def test_adb_install_missing_apk_file(self, adb_instance: ADB):
        with pytest.raises(FileNotFoundError):
            adb_instance.install_app("", timeout=300)

    def test_adb_uninstall_valid_apk(
        self, adb_instance: ADB, valid_apk_path: pathlib.Path
    ):
        result = adb_instance.install_app(
            os.fspath(valid_apk_path), replace_existing=True, timeout=300
        )
        assert "Success" in result
        result = adb_instance.uninstall_app("com.test.pythonadb", timeout=300)
        assert "Success" in result

    def test_adb_uninstall_invalid_apk(self, adb_instance: ADB):
        with pytest.raises((subprocess.CalledProcessError, RuntimeError)):
            adb_instance.uninstall_app("invalid.package.name", timeout=300)
