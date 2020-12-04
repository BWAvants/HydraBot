#!/usr/local/bin/python

# import os
import sys
import signal
import socket
from select import select
import contextlib
from io import StringIO
from threading import Thread, Event
from time import sleep
from queue import Queue, Empty, Full
import logging
from opentrons import robot, labware, instruments
from opentrons.drivers.serial_communication import SerialNoResponse
from opentrons.util.vector import Vector as v
# import pdb
import traceback
from math import pi

# tiprack = labware.load('tiprack-1000ul', slot='11')
#
# pipette = instruments.P1000_Single(mount='right', tip_racks=[tiprack])

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)

version = 'HydraBot 0.2.1'

@contextlib.contextmanager
def stdout_redirect(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


class TermHandler:

    def __init__(self):
        signal.signal(signal.SIGINT, self.term_rcvd)
        signal.signal(signal.SIGTERM, self.term_rcvd)
        signal.signal(signal.SIGHUP, self.term_rcvd)
        signal.signal(signal.SIGQUIT, self.term_rcvd)
        self.termSig = False

    def term_rcvd(self, signum, frame):
        self.termSig = True
        logging.info('TERM Signal Caught\n')
        raise SystemExit


class CommandHandler(Thread):

    def __init__(self, client, *args, **kwargs):
        super().__init__()
        self.stop = Event()
        self.send = Event()
        self.response = None
        self.no_more = Event()
        self.client = client
        self.address = str(client.getpeername())
        self.args = args
        for kwarg, val in kwargs.items():
            setattr(self, kwarg, val)

    def run(self):
        logging.debug('CommandHandler starting for %s' % self.address)
        self.client.sendall(version.encode('utf-8'))
        while not self.stop.is_set():
            if self.no_more.wait(.0001):
                if self.client:
                    try:
                        logging.debug('Stopping incoming messages for %s' % self.address)
                        self.client.shutdown(socket.SHUT_RD)
                    except OSError as E:
                        logging.error('Client Socket Read Shutdown Failed')
                        logging.error(E)
                        self.stop.set()
                        continue
                self.no_more.clear()
            r, w, err = select((self.client,), [], [], 0)
            if r:
                data = self.client.recv(1024)
                if data:
                    missive = data.decode('utf-8')
                    command_queue.put({'address': self.address, 'missive': missive}, timeout=1)
                else:
                    r, w, err = select([], (self.client,), [], 0)
                    if not w:
                        self.stop.set()
                        self.client.close()
                        self.client = None
                        logging.debug('Command Handler for %s Closed - '
                                      'select::writeable indicated client closure' % self.address)
                        self.address = ''
                        continue
            if self.send.is_set():
                self.send.clear()
                if self.response is not None:
                    r, w, err = select([], (self.client,), [], 0.001)
                    if w:
                        self.client.sendall(self.response.encode('utf-8'))
                    else:
                        self.stop.set()
                        self.client.close()
                        self.client = None
                        logging.debug('Command Handler for %s Closed - '
                                      'select::writable indicated client closure' % self.address)
                        self.address = ''
                        continue
        if self.client:
            try:
                self.client.close()
            except OSError as E:
                logging.error('Client Socket Close Failed')
                logging.error(E)
            self.client = None
            logging.debug('Command Handler for %s Closed - internally stopped' % self.address)
            self.address = ''


class OT2Commander(Thread):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.disconnect = Event()
        self.disconnected = True
        self.stop = Event()
        self.args = args
        self.r_offset = 0
        self.t_offset = 0
        self.h_offset = 0
        self.r_offset_cam = 0
        self.t_offset_cam = 0
        self.h_offset_cam = 0
        self.local_context = {'self': self}
        self.global_context = {'robot': robot, 'instruments': instruments, 'labware': labware}
        for kwarg, val in kwargs.items():
            setattr(self, kwarg, val)

    def run(self):
        self.default_setup()
        while not self.stop.is_set():
            if self.disconnect.is_set():
                if robot.is_connected():
                    robot.disconnect()
                    logging.debug('OT-2 robot disconnected')
                self.disconnect.clear()
            try:
                command = command_queue.get(block=True, timeout=0.01)
                missive = command['missive']
            except Empty:
                continue
            with stdout_redirect() as out:
                try:
                    print(missive)
                    retval = eval(missive, self.global_context, self.local_context)
                    if retval:
                        print(retval)
                except SyntaxError:
                    try:
                        exec(missive, self.global_context, self.local_context)
                    except Exception as E:
                        print('EXEC Caught an "%s" exception: %s' % (type(E).__name__, str(E)))
                        print(traceback.format_exc())
                        # pdb.post_mortem()
                except Exception as e:
                    print('EVAL Caught an "%s" exception: %s' % (type(e).__name__, str(e)))
                    print(traceback.format_exc())
                    # pdb.post_mortem()
            if len(out.getvalue()) > 0:
                command['missive'] = str(out.getvalue())
            else:
                command['missive'] = 'ACK'
            response_queue.put(command)
            command_queue.task_done()
        if robot.is_connected():
            robot.disconnect()
            logging.debug('OT-2 robot disconnected')

    def terminate(self):
        self.stop.set()

    def default_setup(self):
        self.r_offset_cam = -0.1
        self.t_offset_cam = 0
        self.h_offset_cam = 2.5
        self.trash = robot.fixed_trash()

        self.tiprack = labware.load('tiprack-1000ul', 11)

        plate_name = '3x2_plate_falcon'
        if plate_name not in labware.list():
            hydra_plate = labware.create(
                plate_name,
                grid=(3, 2),
                spacing=(39.24, 39.24),
                diameter=35.71,
                depth=17.65,
                volume=3000
            )

        self.plate_1 = labware.load(plate_name, '1')
        self.plate_2 = labware.load(plate_name, '2')
        self.plate_3 = labware.load(plate_name, '3')
        self.plate_4 = labware.load(plate_name, '4')
        self.plate_5 = labware.load(plate_name, '5')
        self.plate_6 = labware.load(plate_name, '6')
        self.plate_7 = labware.load(plate_name, '7')
        self.plate_8 = labware.load(plate_name, '8')
        self.plate_9 = labware.load(plate_name, '9')
        self.plate_10 = labware.load(plate_name, '10')

        self.pipette = instruments.P1000_Single('right', tip_racks=[self.tiprack])

        self.camera = instruments.P1000_Single('left')

    def cam_to(self, plate, well, height=0):
        if plate in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
            plate = getattr(self, 'plate_%i' % plate)
        if 'QR' in well:
            pw = plate.wells('A1')
            v_center = pw.from_center(x=0, y=0, z=0)
            v_offset = pw.from_center(r=self.r_offset_cam, theta=self.t_offset_cam, h=self.h_offset_cam)
            v_qr = pw.from_center(r=1.5, theta=-pi/4, h=height)
            v_target = (v_offset - v_center) + v_qr
        else:
            pw = plate.wells(well)
            v_target = pw.from_center(r=self.r_offset_cam, theta=self.t_offset_cam, h=self.h_offset_cam+height)
        self.camera.move_to((pw, v_target))

    def pipette_to(self, plate, well, r=None, t=None, x=None, y=None, height=0):
        if plate in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
            plate = getattr(self, 'plate_%i' % plate)
        pw = plate.wells(well)
        v_center = pw.from_center(x=0, y=0, z=0)
        v_offset = pw.from_center(r=self.r_offset, theta=self.t_offset, h=self.h_offset) - v_center
        if r and t:
            v_naive = pw.from_center(r=r, theta=t, h=height)
        elif x and y:
            v_naive = pw.from_center(x=x, y=y, h=height)
        else:
            return
        v_target = v_offset + v_naive
        self.pipette.move_to((pw, v_target))

    def cam_offset(self, r_offset=None, t_offset=None, h_offset=None):
        if r_offset:
            self.r_offset_cam = r_offset
        if t_offset:
            self.t_offset_cam = t_offset
        if h_offset:
            self.h_offset_cam = h_offset

    def pipette_offset(self, r_offset=None, t_offset=None, h_offset=None):
        if r_offset:
            self.r_offset = r_offset
        if t_offset:
            self.t_offset = t_offset
        if h_offset:
            self.h_offset = h_offset

    def demo(self):
        pass

    def run_protocol(self, filename):
        try:
            with open(filename, 'r') as protocol:
                for line in protocol:
                    try:
                        retval = eval(line, self.global_context, self.local_context)
                        if retval:
                            print(retval)
                    except SyntaxError:
                        try:
                            exec(line, self.global_context, self.local_context)
                        except Exception as E:
                            print('EXEC Caught an "%s" exception: %s' % (type(E).__name__, str(E)))
                            print(traceback.format_exc())
                            # pdb.post_mortem()
                            break
                    except Exception as e:
                        print('EVAL Caught an "%s" exception: %s' % (type(e).__name__, str(e)))
                        print(traceback.format_exc())
                        # pdb.post_mortem()
                        break
        except Exception as ex:
            print('EVAL Caught an "%s" exception: %s' % (type(ex).__name__, str(ex)))
            print(traceback.format_exc())


if __name__ == '__main__':
    print('Starting hydrabotserver.py')
    termHandler = TermHandler()
    logging.info('HydraBot Server Starting Up')

    #  command_queue items are dicts with at least 'missive' and 'return_address'
    command_queue = Queue()
    #  response_queue items are dicts with exactly 'missive' and 'return_address'
    response_queue = Queue()

    ot2 = OT2Commander()

    command_handlers = []

    s = None

    try:
        ot2.start()
        logging.info('OT-2 Commander - started')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # HydraBot port number: h * y * d * r * a  =  8 * 25 * 4 * 18 * 1  =  14400
        s.bind(('0.0.0.0', 14400))
        s.listen(10)
        logging.info('Listening for Connections: PORT 14400')
        while ot2.is_alive():
            r, w, e = select([s], [], [], 0.001)
            for c in r:
                new_client, _ = s.accept()
                new_handler = CommandHandler(new_client)
                new_handler.start()
                command_handlers.append(new_handler)

            for handler in command_handlers:
                if not handler.is_alive():
                    handler.join(1)
                    command_handlers.remove(handler)

            try:
                response = response_queue.get_nowait()
            except Empty:
                response = None
            if response:
                address = response['address']
                for handler in command_handlers:
                    if address == handler.address:
                        handler.response = response['missive']
                        handler.send.set()
                        response_queue.task_done()
                        break
                else:
                    ip, port = address.split(',')
                    ip = ip.strip("(') ")
                    port = int(port.strip("(') "))
                    try:
                        new_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        new_client.connect((ip, port))
                        new_handler = CommandHandler(new_client)
                        new_handler.response = response['missive']
                        new_handler.send.set()
                        new_handler.start()
                        command_handlers.append(new_handler)
                    except (socket.timeout, InterruptedError) as e:
                        logging.error("Response dropped, couldn't connect")
                        logging.error(address)
                        logging.error(e)
                    response_queue.task_done()

    except Exception as e:
        logging.error(e)
    finally:
        if s:
            logging.info('Closing Server Socket')
            try:
                s.shutdown(socket.SHUT_RDWR)
                s.close()
            except OSError as e:
                logging.error('Server Socket not cleanly shutdown')
                logging.error(e)

        logging.info('Stopping Incoming Messages')
        for handler in command_handlers:
            if handler.is_alive():
                handler.no_more.set()
                sleep(0)
            else:
                handler.join(1)
                command_handlers.remove(handler)

        logging.info('Stopping and Releasing OT-2 Commander')
        ot2.disconnect.set()
        sleep(0)
        if ot2.is_alive():
            command_queue.join()
            ot2.stop.set()
            sleep(0)
        ot2.join(2)

        logging.info('Resolving Outgoing Missives')
        while not response_queue.empty():
            response = response_queue.get()
            address = response['address']
            for handler in command_handlers:
                if address == handler.address:
                    handler.response = response['missive']
                    handler.send.set()
            response_queue.task_done()
        response_queue.join()

        logging.info('Finalizing Command Handlers')
        for handler in command_handlers:
            handler.stop.set()
            handler.join(2)
            command_handlers.remove(handler)
