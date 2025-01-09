import zmq
import time
import multiprocessing
from queue import Empty

from .protocol import MessageType

class Talker(multiprocessing.Process):
	def __init__(self, identity):
		super(Talker, self).__init__()

		
		self.address = identity['my_id']

		
		self.initial_backoff = 1.0
		self.operation_backoff = 0.0001

		
		self.messages = multiprocessing.Queue()

		
		self._ready_event = multiprocessing.Event()
		self._stop_event = multiprocessing.Event()

	def stop(self):
		self._stop_event.set()

	def run(self):
		
		context = zmq.Context()
		pub_socket = context.socket(zmq.PUB)
		while True:
			try:
				pub_socket.bind("tcp://%s" % self.address)
				break
			except zmq.ZMQError:
				time.sleep(0.1)

		
		time.sleep(self.initial_backoff)

		
		self._ready_event.set()

		while not self._stop_event.is_set():
			try:
				pub_socket.send_json(self.messages.get_nowait())
			except Empty:
				try:
					time.sleep(self.operation_backoff)
				except KeyboardInterrupt:
					break
			except KeyboardInterrupt:
				break
		
		pub_socket.unbind("tcp://%s" % self.address)
		pub_socket.close()

	def send_message(self, msg):
		self.messages.put(msg)
	
	def wait_until_ready(self):
		while not self._ready_event.is_set():
			time.sleep(0.1)
		return True

class Listener(multiprocessing.Process):
	def __init__(self, port_list, identity):
		super(Listener, self).__init__()

		
		self.address_list = port_list
		self.identity = identity

		self.initial_backoff = 1.0

		self.messages = multiprocessing.Queue()

		self._stop_event = multiprocessing.Event()

	def stop(self):
		self._stop_event.set()

	def run(self):
		
		context = zmq.Context()
		sub_sock = context.socket(zmq.SUB)
		sub_sock.setsockopt(zmq.SUBSCRIBE, b'')
		for a in self.address_list:
			sub_sock.connect("tcp://%s" % a)

		
		poller = zmq.Poller()
		poller.register(sub_sock, zmq.POLLIN)

		
		time.sleep(self.initial_backoff)

		while not self._stop_event.is_set():
			try:
				obj = dict(poller.poll(100))
				if sub_sock in obj and obj[sub_sock] == zmq.POLLIN:
					msg = sub_sock.recv_json()	
					if ((msg['receiver'] == self.identity['my_id']) or (msg['receiver'] is None)):
						self.messages.put(msg)
			except KeyboardInterrupt:
				break
		
		sub_sock.close()
	
	def get_message(self):
		
		try:
			return self.messages.get_nowait()
		except Empty:
			return None
