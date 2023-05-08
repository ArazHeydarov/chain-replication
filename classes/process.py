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
        self.data = {}

    def GetMessage(self, request, context):
        message = json.loads(request.text)
        print(self.name, message)
        command = message['command']
        if command == 'assign':
            data = message['data']
            self.head = data.get('head')
            self.tail = data.get('tail')
            self.successor = data.get('successor')
            self.predecessor = data.get('predecessor')
            response_text = json.dumps({'success': True})

        elif command == 'write_operation':
            name = message['data']['name']
            price = message['data']['price']
            self.data[name] = (price, "dirty")

            response_text = self._send_message_successor(message)
            response_json = json.loads(response_text)
            if response_json.get('success'):
                self.data[name] = (price, "clean")
            else:
                del self.data[name]
        elif command == 'list_books':
            text = ''
            for book in self.data:
                text += f"{book} = {self.data[book][0]}EUR\n"
            response_text = json.dumps({'status': 'success', 'data': text})
        else:
            response_text = json.dumps({'success': True})

        return Message(text=response_text)

    def _send_message_successor(self, message: dict):
        if self.tail:
            return json.dumps({"success": True})
        json_message = json.dumps(message)
        with grpc.insecure_channel(f'localhost:{self.successor["port"]}') as channel:
            stub = MessageServiceStub(channel)
            request = Message(text=json_message)
            response = stub.GetMessage(request)
            channel.close()
        return response.text

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
        # print(f'Server started on port {self.port}...')
        server.wait_for_termination()
