# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import chain_pb2 as chain__pb2


class MessageServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetMessage = channel.unary_unary(
                '/MessageService/GetMessage',
                request_serializer=chain__pb2.Message.SerializeToString,
                response_deserializer=chain__pb2.Message.FromString,
                )


class MessageServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetMessage(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MessageServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetMessage': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMessage,
                    request_deserializer=chain__pb2.Message.FromString,
                    response_serializer=chain__pb2.Message.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'MessageService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class MessageService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetMessage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/MessageService/GetMessage',
            chain__pb2.Message.SerializeToString,
            chain__pb2.Message.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)