import socket

def client_program():
    host = "localhost"
    port = 65432

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    try:
        while True:
            message = input("Ingrese el mensaje ('exit' para cerrar): ")
            client_socket.send(message.encode())
            if message.lower() == "exit":
                break

            data = client_socket.recv(1024).decode()
            print(f"Recibido del servidor: {data}")
    except Exception as e:
        print(f"Error en el cliente: {e}")
    finally:
        client_socket.close()
        print("Conexión cerrada")

if __name__ == "__main__":
    client_program()
