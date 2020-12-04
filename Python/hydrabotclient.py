#!/usr/bin/python3

"""
This is the client module for interacting with hydrabotserver.py
-Ben Avants
"""

import logging
import socket
from select import select
from threading import Thread, Event

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)


class OT2Client(Thread):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.ot2 = None
        self.hostname = None
        self.port = None
        self._connect_event = Event()
        self.connected = False
        self._disconnect_event = Event()
        self.robot_connected = False
        self._claim_robot = None
        self._command = None
        self._send_event = Event()
        self.responded = Event()
        self.response = None
        self._stop_event = Event()

        self.args = args
        for attrib, value in kwargs.items():
            setattr(self, attrib, value)

    def run(self):
        while self._stop_event.wait(0) is False:
            if self._connect_event.wait(0.001):
                if self._connect(self.hostname, self.port) is False:
                    #  Maybe do some re-attempts or something here
                    pass
                self._connect_event.clear()
            while self.connected is True and self._stop_event.wait(0) is False:
                if self._send_event.wait(0):
                    if 'robot' in self._command:
                        self._robot(self._command, self._claim_robot)
                    else:
                        self._send(self._command)
                    self._send_event.clear()
                r, w, e = select((self.ot2,), [], [], 0.001)
                if r:
                    response = self.ot2.recv(4096)
                    if response is None or len(response) == 0:
                        self.ot2.close()
                        self.ot2 = None
                        self.connected = False
                        self.robot_connected = False
                        self.response = None
                        self.responded.set()
                    else:
                        if self.responded.is_set():
                            logging.info('Unchecked Response: "%s"' % self.response)
                        self.response = response.decode('utf-8')
                        self.responded.set()
                if self._disconnect_event.wait(0):
                    if self._disconnect() is False:
                        logging.warning('OT-2 disconnect was not clean')
                    self._disconnect_event.clear()

    def stop(self, wait: float = 0):
        if self.is_alive() is False:
            return True
        self._stop_event.set()
        return self._stop_event.wait(wait)

    def connect(self, hostname: str = None, port: int = 14400):
        if self.connected is True:
            return True
        if self._connect_event.is_set():
            return False
        if self.is_alive() is False:
            self.start()
        if hostname is None:
            hostname = 'c976f83.local'
        self.hostname = hostname
        self.port = port
        self._connect_event.set()
        if self._connect_event.wait(1) is False:
            return False
        return self.connected

    def disconnect(self):
        if self.connected is False:
            return True
        if self._disconnect_event.is_set():
            return False
        self._disconnect_event.set()
        return self._disconnect_event.wait(1)

    def command(self, func_call: str, claim_robot: bool = True, wait_for_reply: bool = False):
        if self.connected is False:
            return False
        self._command = func_call
        self._claim_robot = claim_robot
        self._send_event.set()
        if wait_for_reply is False:
            return self._send_event.wait(1)
        if self._send_event.wait(1) is False:
            return False
        if self.responded.wait(30):
            self.responded.clear()
            return self.response
        else:
            return False

    def check(self, timeout: int = 30):
        if self.connected is False:
            return False
        if self.responded.wait(timeout):
            self.responded.clear()
            return self.response
        return False

    def _connect(self, hostname: str = None, port: int = 14400):
        if self.connected is True:
            return True
        try:
            if hostname is None:
                if self.hostname is None:
                    return False
                hostname = self.hostname
            self.ot2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ot2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.ot2.connect((hostname, port))
            self.connected = True
            self.hostname = hostname
            return True
        except Exception as e:
            logging.error(e)
            return False

    def _disconnect(self):
        if self.connected is False:
            return True
        if self.robot_connected is True:
            self._robot_disconnect()
        try:
            self.ot2.shutdown(socket.SHUT_RDWR)
            self.ot2.close()
            self.ot2 = None
            self.connected = False
            return True
        except Exception as e:
            self.ot2 = None
            self.connected = False
            logging.error(e)
            return False

    def _robot_connect(self):
        self.ot2.sendall('self.robot.connect()'.encode('utf-8'))
        #  Check connectivity HERE
        self.robot_connected = True
        return True

    def _robot_disconnect(self):
        self._send('self.robot.disconnect()')
        #  Check connectivity HERE
        self.robot_connected = False
        return True

    def _send(self, missive: str):
        try:
            self.ot2.sendall(missive.encode('utf-8'))
            return True
        except Exception as e:
            logging.error(e)
            r, w, e = select([], (self.ot2, ), (self.ot2, ))
            if w is None or e is not None:
                logging.warning('OT-2 connection lost')
                self.ot2.close()
                self.connected = False
            return False

    def _robot(self, command: str, connect=True):
        if self.connected is False:
            return False
        if self.robot_connected is False and connect is True:
            if self._robot_connect() is False:
                return False
        elif self.robot_connected is True and connect is False:
            if self._robot_disconnect() is False:
                return False
        if self._send(command) is False:
            return False
        #  Wait for response HERE, maybe?
        return True

