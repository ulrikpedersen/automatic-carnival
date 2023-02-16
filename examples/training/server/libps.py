"""
Simple socket library to access the "hardware" simulator
provided by ps-simulator.py.
"""

from time import sleep
from socket import create_connection


class PowerSupplyClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.sock_stream = None

    def connect(self):
        self.sock = create_connection((self.host, self.port))
        self.sock_stream = self.sock.makefile("rwb", newline="\n", buffering=0)

    def disconnect(self):
        if self.sock_stream:
            self.sock_stream.close()
            self.sock_stream = None
        if self.sock:
            self.sock.close()
            self.sock = None

    def write_readline(self, msg):
        if self.sock_stream is None:
            self.connect()
        self.sock_stream.write(msg)
        return self.sock_stream.readline()

    def get_voltage(self):
        return float(self.write_readline(b"VOL?\n"))

    def do_calibration(self):
        self.start_calibration()
        self.wait_for_calibration()

    def start_calibration(self):
        self.write_readline(b"CALIB 1\n")

    def wait_for_calibration(self):
        while self.is_calibration_busy():
            sleep(0.1)

    def is_calibration_busy(self):
        return int(self.write_readline(b"STAT?\n")) > 0
