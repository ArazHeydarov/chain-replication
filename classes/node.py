import subprocess
import grpc
import json
from chain_pb2_grpc import MessageServiceServicer, add_MessageServiceServicer_to_server, MessageServiceStub
from chain_pb2 import Message

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
