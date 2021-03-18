
from powered_up.bluetooth import connect_ble
from socketserver import BaseRequestHandler, ThreadingTCPServer, TCPServer
from powered_up.messages import AttachedIO, DEBUG_REPLAY_ATTACHED_IO_BYTES, DebugReplayAttachedIO, DebugDownstreamMessage, decode_upstream_message
from powered_up.hub import TechnicHub
from threading import Thread
import socket
import logging
from time import sleep


def start_debug_server(mac_address, my_port=8081, proxy_port=8082):
    DebugServer(mac_address, my_port, proxy_port)

def connect_debug_technic_hub(server_port=8081, proxy_port=8082):
    hub = TechnicHub()
    debug_connection = DebugConnection(server_port, proxy_port)
    hub.connect(debug_connection)
    Thread(target=debug_connection.replay_io, daemon=True).start()
    return hub


class DebugServerHandler(BaseRequestHandler):    
    def handle(self):
        data = self.request.recv(1024)
        self.server.on_downstream_bytes(data)


class DebugServer:
    def __init__(self, mac_address, my_port, proxy_port):        
        self._logger = logging.getLogger("DebugServer")
        self._connection = connect_ble(mac_address)
        self._proxy_port = proxy_port
        self._connection.on_upstream_message = self._on_upstream_message
        self._attached_io_messages = []
        self._logger.info("Ready to handle connections")
        with TCPServer(("localhost", my_port), DebugServerHandler) as server:
            server.on_downstream_bytes = self._on_downstream_bytes
            server.serve_forever()

    def _on_downstream_bytes(self, msg_bytes):
        if msg_bytes == DEBUG_REPLAY_ATTACHED_IO_BYTES:
            self._logger.info("Asked to replay attached io messages, here they go")
            for attached_io_msg in self._attached_io_messages:
                self._send_upstream(attached_io_msg)
        else:
            msg = DebugDownstreamMessage(msg_bytes)
            self._logger.info(f'S: {msg}')
            self._connection.send(msg)

    def _on_upstream_message(self, msg):
        self._logger.info(f'R: {msg}')
        if isinstance(msg, AttachedIO):
            self._attached_io_messages.append(msg)
        self._send_upstream(msg)

    def _send_upstream(self, msg):
        sock = None
        try:
            sock = socket.create_connection(("localhost", self._proxy_port), 5)
            sock.sendall(msg.bytes())
        except ConnectionRefusedError:
            pass
        finally:
            if sock != None:
                sock.close()    

CONNECTION_LOGGER = logging.getLogger("DebugProxy")




class ProxyServerHandler(BaseRequestHandler):    
    def handle(self):
        data = self.request.recv(1024)
        upstream_msg = decode_upstream_message(data)
        CONNECTION_LOGGER.debug(f"Recv: {upstream_msg}")
        self.server.on_upstream_message(upstream_msg)


class DebugConnection:
    def __init__(self, server_port, proxy_port):
        self.on_upstream_message = lambda _: None
        self._server_port = server_port
        self._proxy_port = proxy_port
        Thread(target = self.start_proxy_server, daemon=True).start()

    def _on_upstream_message(self, msg):
        self.on_upstream_message(msg)

    def start_proxy_server(self):
        with ThreadingTCPServer(("localhost", self._proxy_port), ProxyServerHandler) as proxy_server:
            proxy_server.on_upstream_message = self._on_upstream_message
            proxy_server.serve_forever()

    def replay_io(self):
        self.send(DebugReplayAttachedIO())
    
    def send(self, msg):
        CONNECTION_LOGGER.debug(f"Send: {msg}")
        sock = None
        try:
            sock = socket.create_connection(("localhost", self._server_port), 5)
            sock.sendall(msg.bytes())
        finally:
            if sock != None:
                sock.close()
