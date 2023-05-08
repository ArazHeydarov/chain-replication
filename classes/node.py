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
        self.master_channel = None
        self.master_stub = None
        self._initialize_master_conn()

    def _initialize_master_conn(self):
        channel = grpc.insecure_channel(f'localhost:{self.master_port}')
        self.master_channel = channel
        stub = MessageServiceStub(channel)
        self.master_stub = stub

    def execute_command(self, command: str) -> None:
        if 'Local-store-ps' in command:
            cmd, number_of_ps = command.split()
            self._create_process(int(number_of_ps))
        if command == 'kill_all':
            self._kill_all_process()
        elif command == 'list_global_processes':
            self._send_command_to_master(command='list_processes')
        elif command == 'check_alive_all_processes':
            self._send_command_to_master(command=command)

    def _create_process(self, number_of_process: int) -> None:
        for i in range(number_of_process):
            new_process = subprocess.Popen(['python', 'main.py',
                                            'process', f"{self.name}-ps{i}"])
            self.processes.append(new_process)

    def _kill_all_process(self):
        self._send_command_to_master(command=f"remove_node {self.name}")
        for ps in self.processes:
            ps.terminate()

    def _send_command_to_master(self, command: str):
        request = Message(text=json.dumps({
            "command": command,
        }))
        response = self.master_stub.GetMessage(request)

    def __del__(self):
        self._kill_all_process()

        if self.master_channel:
            self.master_channel.close()
