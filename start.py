#!/usr/bin/env python3

import logging

from adb.adb import ADB

if __name__ == "__main__":

    # Logging configuration.
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format="%(asctime)s> [%(levelname)s][%(name)s][%(funcName)s()] %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
        level=logging.INFO,
    )

    # This is an example file showing how the adb wrapper can be used.

    adb = ADB()

    # Start with a clean adb server.
    adb.kill_server()
    adb.connect()

    adb_version = adb.get_version()
    logger.info("ADB version: {0}".format(adb_version))

    connected_devices = adb.get_available_devices()
    logger.info("Connected devices: {0}".format(connected_devices))

    # Set the first device in the list as the target of the subsequent commands.
    adb.target_device = connected_devices[0]

    adb.wait_for_device()
    logger.info(
        "Message from Android device: {0}".format(adb.shell(['echo "Hello World!"']))
    )
