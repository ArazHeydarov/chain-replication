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
                    self.chain_created = True
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
