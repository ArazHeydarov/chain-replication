import grpc
import json
import socket
from concurrent import futures
from chain_pb2_grpc import MessageServiceServicer, add_MessageServiceServicer_to_server, MessageServiceStub
from chain_pb2 import Message


class Process(MessageServiceServicer):
    def __init__(self, name):
        self.name = name
        self.master_port = 8000
        self.port = None
        self.head = None
        self.tail = None
        self.predecessor = None
        self.successor = None

    def GetMessage(self, request, context):
        message = json.loads(request.text)
        command = message['command']
        print(self.name, message)
        return Message(text="received")

    def start_server(self):
        self._register_on_master()
        self._start_grpc_server()

    def _register_on_master(self):
        self._set_port()
        with grpc.insecure_channel(f'localhost:{self.master_port}') as channel:
            stub = MessageServiceStub(channel)
            request = Message(text=json.dumps({
                "command": 'register_process',
                "data": {
                    "name": self.name,
                    "port": self.port
                }
            }))
            response = stub.GetMessage(request)
            channel.close()

    def _set_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        self.port = port

    def _start_grpc_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
        add_MessageServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        server.start()
        print(f'Server started on port {self.port}...')
        server.wait_for_termination()