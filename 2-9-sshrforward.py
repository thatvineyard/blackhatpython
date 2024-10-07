import os
import select
import socket
import sys
import threading
import paramiko
import getpass


def reverse_forward_tunnel(server_port, remote_host, remote_port, transport: paramiko.Transport):
  transport.request_port_forward('', server_port)
  while True:
    chan = transport.accept(1000)
    if chan is None:
      continue
    thread = threading.Thread(target=handler, args=(chan, remote_host, remote_port))
    thread.setDaemon(True)
    thread.start()


def handler(chan: paramiko.Channel, host, port):
  sock = socket.socket()
  
  try: 
    sock.connect((host, port))
  except Exception as e:
    print("Sock connect failed")
    return
  
  print("Connected")
  
  while True:
    readList, w, x = select.select([sock, chan], [], [])
    if sock in readList:
      data = sock.recv(1024)
      if len(data) == 0:
        break
      chan.send(data)
    if chan in readList:
      data = chan.recv(1024)
      if len(data) == 0:
        break
      sock.send(data)
      
  chan.close()
  sock.close()
  print("Closed tunnel")
  

def main(server_host, server_port, remote_host, remote_port, username, key_filename):
  client = paramiko.SSHClient()
  client.load_system_host_keys()
  client.set_missing_host_key_policy(paramiko.WarningPolicy())
  
  print(f"Connecting to {server_host}:{server_port} via SSH...")
  
  try:
    client.connect(server_host, server_port, username=username, key_filename=key_filename)
  except Exception as e:
    print(f"Failed to connect {e}")
    sys.exit(1)
    
  print(f"Connected!")
  print(f"Now forwarding to {remote_host}:{remote_port} via TCP...")
  
  try:
    reverse_forward_tunnel(server_port, remote_host, remote_port, client.get_transport())
  except KeyboardInterrupt:
    print("Quitting")
    sys.exit(0)
    
if __name__ == "__main__":
    username = input("Username: ") or "ec2-user"
    password = input("Password (leave empty to use keyfile): ")
    key_filename = None
    if not password:
      key_filename = input("Path to keyfile: ") or "test_rsa.key"

      if not os.path.exists(key_filename):
        raise ValueError(f"Key file {key_filename} does not exist")

    server_host = input("Enter server IP: ") or "127.0.0.1" #"ec2-13-61-0-148.eu-north-1.compute.amazonaws.com"
    server_port = input('Port: ') or 2222 # or 22
    remote_host = input("Enter remote IP: ") or "127.0.0.1"
    remote_port = input('Remote port: ') or 5555
    main(server_host, server_port, remote_host, remote_port, username, key_filename)
    