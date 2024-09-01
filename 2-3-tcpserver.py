import socket
import threading

IP = '0.0.0.0'
PORT = 5555

def main():
  # AF_INET - ipv4, STREAM - TCP
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.bind((IP, PORT))
  server.listen(5) # max backlog of 5 connections
  
  print(f'[*] Listening on {IP}:{PORT}')
  
  while True:
    client, address = server.accept() # blocking, waiting for connection
    print(f'[*] Accepted connection from {address[0]}: ')
    
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()
  
def handle_client(client_socket: socket.socket):
  with client_socket as sock:
    request = sock.recv(1024)
    print(f'[*] Received: {request.decode("utf-8")}')
    sock.send(b'ACK') # acknowledge
  
if __name__ == '__main__':
  main()