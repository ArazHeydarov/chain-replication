import subprocess
import sys

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

        elif command == 'kill_all':
            self._kill_all_process()

        elif command == 'list_global_processes':
            self._send_command_to_master(command='list_processes')

        elif command == 'check_alive_all_processes':
            self._send_command_to_master(command=command)

        elif command == 'Create-chain':
            self._send_command_to_master(command="create_chain")

        elif command == 'List-chain':
            response = self._send_command_to_master(command="list_chain")
            print(response['message'])

        elif 'Write-operation' in command:
            _, book_details = command.split(" ", 1)
            book_details = book_details[1:-1]
            name, price = book_details.rsplit(" ", 1)
            name = name[1:-2]
            price = price.replace(",", '.')
            self._send_command_to_master(command='write_operation',
                                         data={"name": name, "price": price})

        elif command == 'List-books':
            response = self._send_command_to_master(command='list_books')
            print(response['message'])

        elif 'Read-operation' in command:
            _, book_name = command.split(" ", 1)
            book_name = book_name[1:-1]
            response = self._send_command_to_master(command='read_operation', data={'name': book_name})
            print(response['message'])

        elif 'Time-out' in command:
            _, delay = command.split()
            self._send_command_to_master(command='set_delay', data={'delay': int(delay)})

        elif 'Remove-head' == command:
            self._send_command_to_master(command='remove_head')

        elif command in ['exit', 'quit']:
            sys.exit(0)

        else:
            print("No such command is found in node")

    def _create_process(self, number_of_process: int) -> None:
        for i in range(number_of_process):
            new_process = subprocess.Popen(['python', 'main.py',
                                            'process', f"{self.name}-ps{i}"])
            self.processes.append(new_process)

    def _kill_all_process(self):
        if self.processes:
            self._send_command_to_master(command=f"remove_node {self.name}")
            for ps in self.processes:
                ps.terminate()

    def _send_command_to_master(self, command: str, data: dict = None):
        request = Message(text=json.dumps({
            "command": command,
            "data": data
        }))
        response = self.master_stub.GetMessage(request)
        response = json.loads(response.text)
        if response['status'] == 'failure':
            print("Message from server:", response['message'])
        else:
            pass
            # print("Success")
        return response

    def __del__(self):
        self._kill_all_process()

        if self.master_channel:
            self.master_channel.close()
