import socket
import threading
import time

# Estados posibles de la conexión
class ConnectionState:
    STARTING = "Starting"
    RUNNING = "Running"
    STOPPING = "Stopping"
    STOPPED = "Stopped"
    FAILED = "Failed"

# Clase de conexión individual con estados
class ConnectionHandler:
    def __init__(self, conn, addr, server):
        self.conn = conn
        self.addr = addr
        self.state = ConnectionState.STARTING
        self.server = server
        print(f"Estado de conexión con {self.addr}: {self.state}")

    def run(self):
        try:
            self.state = ConnectionState.RUNNING
            print(f"Estado de conexión con {self.addr}: {self.state}")
            while self.state == ConnectionState.RUNNING:
                data = self.conn.recv(1024)
                if not data or data == b"exit":
                    self.stop()
                    break
                print(f"Recibido de {self.addr}: {data.decode()}")
                self.conn.sendall(data)
        except Exception as e:
            self.state = ConnectionState.FAILED
            print(f"Error en la conexión con {self.addr}: {e}")
        finally:
            self.stop()

    def stop(self):
        self.state = ConnectionState.STOPPING
        print(f"Estado de conexión con {self.addr}: {self.state}")
        self.conn.close()
        self.state = ConnectionState.STOPPED
        print(f"Estado de conexión con {self.addr}: {self.state}")
        self.server.remove_connection(self)

class TCPServer:
    def __init__(self, host, port, max_connections):
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.socket = None
        self.connections = []
        self.state = ConnectionState.STARTING

    def start(self):
        self.state = ConnectionState.STARTING
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(self.max_connections)
        self.state = ConnectionState.RUNNING
        print(f"Servidor TCP en estado: {self.state} y esperando conexiones en {self.host}:{self.port}")

        try:
            while self.state == ConnectionState.RUNNING:
                client_conn, client_addr = self.socket.accept()
                print(f"Conexión aceptada desde {client_addr}")
                connection = ConnectionHandler(client_conn, client_addr, self)
                self.connections.append(connection)
                thread = threading.Thread(target=connection.run)
                thread.start()
                self.update_connections()
        except Exception as e:
            print(f"Error en el servidor: {e}")
            self.state = ConnectionState.FAILED
        finally:
            self.stop()

    def stop(self):
        self.state = ConnectionState.STOPPING
        print(f"Cerrando servidor, estado: {self.state}")
        for connection in self.connections:
            connection.stop()
        self.socket.close()
        self.state = ConnectionState.STOPPED
        print(f"Servidor en estado: {self.state}")

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)
        self.update_connections()

    def update_connections(self):
        print(f"Conexiones activas: {len(self.connections)}")
        for conn in self.connections:
            print(f"Estado de {conn.addr}: {conn.state}")

# Inicialización del servidor
if __name__ == "__main__":
    server = TCPServer("localhost", 65432, 5)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
