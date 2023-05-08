import random
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
        server.wait_for_termination()

    def _create_chain(self):
        self.chain = random.sample(self.process, len(self.process))
        print("Chain", self.chain)
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
