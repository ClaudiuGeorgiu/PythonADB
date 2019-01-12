#!/usr/bin/env python
# coding: utf-8

import logging

from adb.adb import ADB

if __name__ == '__main__':

    # Logging configuration.
    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(asctime)s> [%(levelname)s][%(name)s][%(funcName)s()] %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)

    adb = ADB(debug=True)

    logger.info('ADB version: {0}'.format(adb.get_version()))
