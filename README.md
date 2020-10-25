# PythonADB

> Android Debug Bridge (ADB) wrapper in Python.

[![Codacy](https://app.codacy.com/project/badge/Grade/18fa128fe8414a79a32c126f036dd6ac)](https://www.codacy.com/gh/ClaudiuGeorgiu/PythonADB)
[![Ubuntu Build Status](https://github.com/ClaudiuGeorgiu/PythonADB/workflows/Ubuntu/badge.svg)](https://github.com/ClaudiuGeorgiu/PythonADB/actions?query=workflow%3AUbuntu)
[![Windows Build Status](https://github.com/ClaudiuGeorgiu/PythonADB/workflows/Windows/badge.svg)](https://github.com/ClaudiuGeorgiu/PythonADB/actions?query=workflow%3AWindows)
[![MacOS Build Status](https://github.com/ClaudiuGeorgiu/PythonADB/workflows/MacOS/badge.svg)](https://github.com/ClaudiuGeorgiu/PythonADB/actions?query=workflow%3AMacOS)
[![Code Coverage](https://codecov.io/gh/ClaudiuGeorgiu/PythonADB/badge.svg)](https://codecov.io/gh/ClaudiuGeorgiu/PythonADB)
[![Python Version](https://img.shields.io/badge/Python-3.6%2B-green.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/ClaudiuGeorgiu/PythonADB/blob/master/LICENSE)



This project contains a basic Python wrapper of the command line `adb` (Android Debug Bridge) tool (by using the `subprocess` module in Python). Currently the main functions are supported (`shell` commands, file copy operations and app installations) but the wrapper is easily extensible with new features. All the implemented functions support an optional timeout value (tested on Ubuntu, Windows and MacOS) to let the command fail if it takes too long to finish execution (this can be useful during automatic testing).



## ❱ Prerequisites

This project is only a wrapper of [ADB](https://developer.android.com/studio/command-line/adb), so `adb` should be already installed and working. In order to test if you have a working `adb` installation, you can run the following command in a terminal:

```Shell
$ adb version
Android Debug Bridge version 1.0.41
...
```

If `adb` is installed in a custom location, `ADB_PATH` environment variable can be used to specify the `adb` executable to be used by PythonADB (e.g., in Ubuntu, run `export ADB_PATH=/custom/location/adb` before running PythonADB in the same terminal).



## ❱ Usage

Apart from [ADB](https://developer.android.com/studio/command-line/adb), the only requirement of this project is a working `Python 3` (at least `3.6`) installation. The first thing to do is to get a local copy of this repository, so open up a terminal in the directory where you want to save the project and clone the repository:

```Shell
$ git clone https://github.com/ClaudiuGeorgiu/PythonADB.git
$ cd PythonADB
```

Make sure to execute the following commands in the previously created `PythonADB/` directory:

```Shell
$ # The usage of a virtual environment is highly recommended, e.g., virtualenv.
$ # If not using virtualenv (https://virtualenv.pypa.io/), skip the next 2 lines.
$ virtualenv -p python3 venv
$ source venv/bin/activate

$ # Install PythonADB requirements.
$ python3 -m pip install -r requirements.txt
```

Usage example (see [start.py](https://github.com/ClaudiuGeorgiu/PythonADB/blob/master/start.py) file for a complete example):

```Python
from adb.adb import ADB

adb = ADB()
adb.get_version()
adb.wait_for_device()
adb.shell(["ls"])
# The following commands will fail if not completed in 30 seconds.
adb.install_app("/path/to/file.apk", timeout=30)
adb.pull_file("/path/on/device", "/path/on/host", timeout=30)
# ... more ...
```

See [adb/adb.py](https://github.com/ClaudiuGeorgiu/PythonADB/blob/master/adb/adb.py) file for a complete list with all the implemented `adb` commands.



## ❱ Contributing

Questions, bug reports and pull requests are welcome on GitHub at [https://github.com/ClaudiuGeorgiu/PythonADB](https://github.com/ClaudiuGeorgiu/PythonADB).



## ❱ License

You are free to use this code under the [MIT License](https://github.com/ClaudiuGeorgiu/PythonADB/blob/master/LICENSE).
