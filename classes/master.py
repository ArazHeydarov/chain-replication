import random
import time
import uuid
import grpc
import json
from concurrent import futures
from chain_pb2_grpc import MessageServiceServicer, add_MessageServiceServicer_to_server, MessageServiceStub
from chain_pb2 import Message


class Master(MessageServiceServicer):
    def __init__(self):
        self.id = uuid.uuid4().hex
        self.port = 8000
        self.process = []
        self.chain = []
        self.chain_created = False
        self.head = None
        self.tail = None
        self.operations = []
        self.completed_operations = {}

    def GetMessage(self, request, context):
        try:
            status = 'success'
            message = json.loads(request.text)
            command = message['command']
            if command == 'register_process':
                self.process.append(message['data'])

            elif command == 'list_processes':
                print(self.process)

            elif command == 'check_alive_all_processes':
                self._check_process()

            elif 'remove_node' in command:
                cmd, node_name = message['command'].split()
                self.process = [ps for ps in self.process if node_name not in ps['name']]

            elif command == 'create_chain':
                if self.chain_created:
                    raise Exception("Chain has already been created")
                else:
                    self._create_chain()
                    self.chain_created = True
            elif command == 'list_chain':
                if not self.chain_created:
                    raise Exception("Chain hasn't been created yet. Please create it first with 'Create-chain'")
                message = f"{self.head['name']}(Head)"
                for i in range(1, len(self.chain)-1):
                    message += f" -> {self.chain[i]['name']} -> "
                message += f"{self.tail['name']}(Tail)"

            elif command in ['write_operation', 'read_operation', 'list_books', 'set_delay']:
                operation_id = uuid.uuid4().hex
                message['id'] = operation_id
                self.operations.append(message)
                while operation_id not in self.completed_operations:
                    time.sleep(0.5)
                message = self.completed_operations[operation_id]

            else:
                raise Exception("No such command is found in master")
        except Exception as e:
            command = request.text
            status = 'failure'
            message = f"Message received with error {request.text} with {e}"
            print(message)
        return Message(text=json.dumps({"command": command, 'status': status, 'message': message}))

    def _check_process(self):
        for ps in self.process:
            print(f"Checking process {ps['name']} with port {ps['port']}")
            with grpc.insecure_channel(f'localhost:{ps["port"]}') as channel:
                stub = MessageServiceStub(channel)
                request = Message(text=json.dumps({
                    "command": 'alive',
                }))
                response = stub.GetMessage(request)
                channel.close()

    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
        add_MessageServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        server.start()
        print(f'Server started on port {self.port}...')

        while True:
            time.sleep(0.5)
            try:
                operation = self.operations.pop(0)
                if operation['command'] in ['write_operation', 'set_delay']:
                    response = self._send_message_process(self.head['port'], operation)
                    message = json.loads(response.text)['data']
                    self.completed_operations[operation['id']] = message
                elif operation['command'] in ['read_operation', 'list_books']:
                    response = self._send_message_process(self.tail['port'], operation)
                    message = json.loads(response.text)['data']
                    self.completed_operations[operation['id']] = message
            except IndexError:
                pass

    def _create_chain(self):
        self.chain = random.sample(self.process, len(self.process))
        self.head = self.chain[0]
        self.tail = self.chain[-1]
        # Assign head
        self._send_message_process(port=self.head['port'],
                                   message={
                                       "command": "assign",
                                       "data": {
                                           "head": True,
                                           "successor": self.chain[1]
                                       }
                                   })
        # Assign tail
        self._send_message_process(port=self.tail['port'],
                                   message={
                                       "command": "assign",
                                       "data": {
                                           "tail": True,
                                           "predecessor": self.chain[-2]
                                       }
                                   })
        # Assign middle processes
        for i in range(1, len(self.chain) - 1):
            self._send_message_process(self.chain[i]['port'],
                                       message={
                                           "command": "assign",
                                           "data": {
                                               "predecessor": self.chain[i-1],
                                               "successor": self.chain[i+1]
                                           }
                                       })

    @staticmethod
    def _send_message_process(port, message: dict):
        json_message = json.dumps(message)
        with grpc.insecure_channel(f'localhost:{port}') as channel:
            stub = MessageServiceStub(channel)
            request = Message(text=json_message)
            response = stub.GetMessage(request)
            channel.close()
        return response
