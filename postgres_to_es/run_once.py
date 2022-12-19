"""Ensure only one instance of ETL process is running"""
import logging
import socket
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# Source: https://stackoverflow.com/a/7758075/196171
def get_lock(process_name):
    # Without holding a reference to our socket somewhere it gets garbage
    # collected when the function exits
    get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    try:
        # The null byte (\0) means the socket is created
        # in the abstract namespace instead of being created
        # on the file system itself.
        # Works only in Linux
        get_lock._lock_socket.bind('\0' + process_name)
    except socket.error:
        logger.critical('ETL instance is already running. Exiting')
        sys.exit()
