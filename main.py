import json
import subprocess
import sys
import traceback
import uuid
import socket
from pprint import pprint

import grpc
import time
from concurrent import futures
from chain_pb2_grpc import MessageServiceServicer, add_MessageServiceServicer_to_server, MessageServiceStub
from chain_pb2 import Message


class Master(MessageServiceServicer):
    def __init__(self):
        self.id = uuid.uuid4().hex
        self.port = 8000
        self.process = []

    def GetMessage(self, request, context):
        try:
            message = json.loads(request.text)
            print(message)
            if message['command'] == 'register_process':
                self.process.append(message['data'])
            if message['command'] == 'list_processes':
                print(self.process)
        except Exception as e:
            print(f"Message received with error {request.text} with {e}")
        return Message(text="received")

    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
        add_MessageServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        server.start()
        print(f'Server started on port {self.port}...')
        server.wait_for_termination()


class Node:
    def __init__(self, name):
        self.name = name
        self.processes = []
        self.master_port = "8000"

    def execute_command(self, command: str) -> None:
        if 'Local-store-ps' in command:
            cmd, number_of_ps = command.split()
            self._create_process(int(number_of_ps))
        if command == 'kill_all':
            self._kill_all_process()
        if command == 'list_global_processes':
            self._list_global_processes()

    def _create_process(self, number_of_process: int) -> None:
        for i in range(number_of_process):
            new_process = subprocess.Popen(['python', 'main.py',
                                            'process', f"{self.name}-ps{i}"])
            self.processes.append(new_process)

    def _kill_all_process(self):
        for ps in self.processes:
            ps.terminate()

    def _list_global_processes(self):
        with grpc.insecure_channel(f'localhost:{self.master_port}') as channel:
            stub = MessageServiceStub(channel)
            request = Message(text=json.dumps({
                "command": 'list_processes',
            }))
            response = stub.GetMessage(request)
            channel.close()

    def __del__(self):
        self._kill_all_process()


class Process(MessageServiceServicer):
    def __init__(self, name):
        self.name = name
        self.master_port = 8000
        self.port = None

    def GetMessage(self, request, context):
        print(f"Message received {request.text}")
        return Message(text="received")

    def start_server(self):
        self._register_on_master()

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


if len(sys.argv) > 1:
    if sys.argv[1] == 'master':
        master = Master()
        master.start_server()

    if sys.argv[1] == 'node':
        node = Node(name=sys.argv[2])
        while True:
            print(f"{node.name} prompt: ", end='')
            prompt = input()
            node.execute_command(command=prompt)

    if sys.argv[1] == 'process':
        process = Process(name=sys.argv[2])
        process.start_server()
